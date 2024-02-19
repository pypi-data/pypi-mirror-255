#!./runmodule.sh

import os
import shutil
import filecmp
import datetime
import logging
import enum
import typing

from confattr import Config

from .model import ComparisonNode, DirectoryComparisonNode, Statistics, ACTION, TYPE
from .symlink import SYMLINK_TYPE, is_symlink, read_symlink, create_symlink, is_internal_link, change_target, config_change_abs_internal_symlink_to_target
from .lsblk import lsblk


@enum.unique
class PREFERRED_SYMLINK_TYPE(enum.Enum):
	ABSOLUTE = 'absolute'
	RELATIVE = 'relative'
	AUTO = 'auto'
	SAME = 'same'


def get_mount_point(path: str) -> str:
	path = os.path.abspath(path)
	last_path = None
	while path != last_path:
		if os.path.ismount(path):
			return path
		last_path = path
		path = os.path.dirname(path)
	return path


class Synchronizer:

	preferred_symlink_type = Config('symlink.preferred-link-type', PREFERRED_SYMLINK_TYPE.SAME, help={
		PREFERRED_SYMLINK_TYPE.ABSOLUTE : 'when copying a symlink, make it point to an absolute path',
		PREFERRED_SYMLINK_TYPE.RELATIVE : 'when copying a symlink, make it point to a relative path',
		PREFERRED_SYMLINK_TYPE.AUTO : 'use a relative link if the target is in the directory to be synchronized and the new link is created on a removable device so that the new link does not break if the mount point changes; use an absolute path otherwise so that the link does not break if you move the link',
		PREFERRED_SYMLINK_TYPE.SAME : 'create a relative link if the original link is a relative link, create an absolute link if the original link is an absolute link',
	})
	change_abs_internal_symlink_to_target = config_change_abs_internal_symlink_to_target

	time_stamp_format = '# %Y-%m-%d %H:%M'

	def __init__(self, log: logging.Logger = logging.root) -> None:
		self.running = True
		self.log = log
		self.nodes_synchronized = 0
		self.errors = 0
		self._mountpoints: typing.Optional[typing.Set[str]] = None

		self.log.info(datetime.datetime.now().strftime(self.time_stamp_format))

	def stop(self) -> None:
		self.running = False

	def sync(self, node: ComparisonNode) -> None:
		if not self.running:
			self.log.warning('aborting synchronization')
			return

		if node.action is ACTION.NONE:
			pass
		elif node.action is ACTION.IGNORE:
			self.log.info(f'ignoring {node.path_src} ({node.state.name})')
		elif node.action is ACTION.ERROR:
			self.log.error(f'ignoring {node.path_src} ({node.state.name}) because an exception has occured')
			if node.error_src:
				self.log.error(f'    error src: %s', node.error_src)
			if node.error_dst:
				self.log.error(f'    error dst: %s', node.error_dst)
		elif isinstance(node, DirectoryComparisonNode):
			self.sync_dir(node)
		else:
			self.sync_file(node)

		if node.action not in Statistics.ACTIONS_NO_CHANGE:
			self.nodes_synchronized += 1

	def sync_file(self, node: ComparisonNode) -> None:
		if node.action is ACTION.CREATE:
			self.copy_file(node.path_src, node.path_dst, node.root.path_src, node.root.path_dst)
		elif node.action is ACTION.DELETE:
			self.remove_file(node.path_dst)
		elif node.action is ACTION.UNDO_CREATE:
			self.remove_file(node.path_src)
		elif node.action is ACTION.UNDO_DELETE:
			self.copy_file(node.path_dst, node.path_src, node.root.path_dst, node.root.path_src)

		# ComparisonNode only
		elif node.action is ACTION.UPDATE:
			self.copy_file(node.path_src, node.path_dst, node.root.path_src, node.root.path_dst)
		elif node.action is ACTION.DOWNGRADE:
			self.copy_file(node.path_src, node.path_dst, node.root.path_src, node.root.path_dst)
		elif node.action is ACTION.UNDO_UPDATE:
			self.copy_file(node.path_dst, node.path_src, node.root.path_dst, node.root.path_src)
		elif node.action is ACTION.UNDO_DOWNGRADE:
			self.copy_file(node.path_dst, node.path_src, node.root.path_dst, node.root.path_src)
		else:
			assert False

	def sync_dir(self, node: DirectoryComparisonNode) -> None:
		if node.action is ACTION.CREATE:
			self.copy_dir(node.path_src, node.path_dst, node.loaded_children)
		elif node.action is ACTION.DELETE:
			self.rmdir(node.path_dst)
			return
		elif node.action is ACTION.UNDO_CREATE:
			self.rmdir(node.path_src)
			return
		elif node.action is ACTION.UNDO_DELETE:
			self.copy_dir(node.path_dst, node.path_src, node.loaded_children)

		# DirectoryComparisonNode only
		elif node.action is ACTION.DIR_CHANGE_DESTINATION:
			pass
		elif node.action is ACTION.DIR_CHANGE_SOURCE:
			pass
		elif node.action is ACTION.DIR_CHANGE_BOTH:
			pass

		elif node.action is ACTION.CHANGE_DESTINATION_TYPE:
			if node.type_dst == TYPE.DIRECTORY:
				self.rmdir(node.path_dst)
				self.copy_file(node.path_src, node.path_dst, node.root.path_src, node.root.path_dst)
				return
			else:
				self.remove_file(node.path_dst)
				self.copy_dir(node.path_src, node.path_dst, node.loaded_children)
		elif node.action is ACTION.CHANGE_SOURCE_TYPE:
			if node.type_src == TYPE.DIRECTORY:
				self.rmdir(node.path_src)
				self.copy_file(node.path_dst, node.path_src, node.root.path_dst, node.root.path_src)
				return
			else:
				self.remove_file(node.path_src)
				self.copy_dir(node.path_dst, node.path_src, node.loaded_children)

		elif node.action is ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN:
			self.copy_dir(node.path_src, node.path_dst, node.loaded_children)
		elif node.action is ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN:
			self.copy_dir(node.path_dst, node.path_src, node.loaded_children)
		elif node.action is ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN:
			assert node.type_dst is TYPE.FILE or node.type_dst is TYPE.LINK, node.type_dst
			self.remove_file(node.path_dst)
			self.copy_dir(node.path_src, node.path_dst, node.loaded_children)
		elif node.action is ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN:
			assert node.type_src is TYPE.FILE or node.type_src is TYPE.LINK, node.type_src
			self.remove_file(node.path_src)
			self.copy_dir(node.path_dst, node.path_src, node.loaded_children)
		else:
			assert False

		for c in node.children:
			self.sync(c)


	def copy_file(self, path1: str, path2: str, root1: str, root2: str) -> None:
		'''
		copy2() uses copystat() to copy the file metadata.
		But: Even the higher-level file copying functions (shutil.copy(), shutil.copy2()) cannot copy all file metadata.
		On POSIX platforms, this means that file owner and group are lost as well as ACLs.
		On Mac OS, the resource fork and other metadata are not used. This means that resources will be lost and file type and creator codes will not be correct.
		On Windows, file owners, ACLs and alternate data streams are not copied.
		https://docs.python.org/3/library/shutil.html
		'''
		assert path1 != path2
		if os.path.exists(path2) or os.path.islink(path2):
			try:
				os.remove(path2)
			except Exception as e:
				self.log.error(e)
				self.errors += 1
				return
		if is_symlink(path1):
			self.create_link(path1, path2, root1)
			return

		self.log.info('cp %r %r', path1, path2)
		try:
			shutil.copy2(path1, path2)
		except Exception as e:
			self.log.error(e)
			self.errors += 1
			self.stop_if_no_space_left_on_device(e)

	def create_link(self, path1: str, path2: str, root1: str) -> None:
		symlink_type1, target1 = read_symlink(path1)
		is_internal = is_internal_link(path1, target1, root1)
		symlink_type2 = self.get_preferred_symlink_type(symlink_type1, is_internal, path2)
		if is_internal and symlink_type1 is SYMLINK_TYPE.ABSOLUTE and self.change_abs_internal_symlink_to_target:
			target2 = change_target(target=target1, src=path1, dst=path2)
		else:
			target2 = target1
		self.log.info('ln -s %r %r', target2, path2)
		try:
			create_symlink(target2, path2, symlink_type2)
		except Exception as e:
			self.log.error(e)
			self.errors += 1
			self.stop_if_no_space_left_on_device(e)

	def get_preferred_symlink_type(self, original_symlink_type: SYMLINK_TYPE, is_internal: bool, new_link: str) -> SYMLINK_TYPE:
		if self.preferred_symlink_type is PREFERRED_SYMLINK_TYPE.ABSOLUTE:
			return SYMLINK_TYPE.ABSOLUTE
		elif self.preferred_symlink_type is PREFERRED_SYMLINK_TYPE.RELATIVE:
			return SYMLINK_TYPE.RELATIVE
		elif self.preferred_symlink_type is PREFERRED_SYMLINK_TYPE.SAME:
			return original_symlink_type
		elif self.preferred_symlink_type is not PREFERRED_SYMLINK_TYPE.AUTO:
			assert False

		if not is_internal:
			return SYMLINK_TYPE.ABSOLUTE

		if self.is_removable_device(new_link):
			# if the target is on the same removable device prefer a relative sym link so that it does not break if the mount point changes
			return SYMLINK_TYPE.RELATIVE

		# if the target is on the internal hard drive it's unlikely that the mount point will change
		# so prefer an absolute path so that the link does not break when moving it
		return SYMLINK_TYPE.ABSOLUTE

	def is_removable_device(self, path: str) -> bool:
		if self._mountpoints is None:
			self._mountpoints = {dev.mountpoint for dev in lsblk.iter_mounted_devices()}

		mountpoint = get_mount_point(path)
		return mountpoint in self._mountpoints


	def remove_file(self, path: str) -> None:
		self.log.info('rm %r', path)
		try:
			os.remove(path)
		except Exception as e:
			self.log.error(e)
			self.errors += 1


	def copy_dir(self, path1: str, path2: str, without_children: bool) -> None:
		if without_children:
			self.mkdir(path1, path2)
		else:
			self.copy_tree(path1, path2)

	def mkdir(self, path1: str, path2: str) -> None:
		'''
		create directory `path2` with same permissions like directory `path1`
		'''
		assert path1 != path2
		self.log.info('mkdir %r  (with permissions from %r)', path2, path1)
		try:
			os.mkdir(path2)
			shutil.copystat(path1, path2)
		except Exception as e:
			self.log.error(e)
			self.errors += 1
			self.stop_if_no_space_left_on_device(e)

	def copy_tree(self, path1: str, path2: str) -> None:
		'''
		copy directory `path1` to `path2` including all contained files and subdirectories. `path1` must not exist yet.
		'''
		try:
			shutil.copytree(path1, path2, dirs_exist_ok=False)
		except Exception as e:
			self.log.error(e)
			self.errors += 1
			self.stop_if_no_space_left_on_device(e)

	def rmdir(self, path: str) -> None:
		'''
		remove directory `path` and all of it's content
		'''
		self.log.info('rm -r %r', path)
		try:
			shutil.rmtree(path)
		except Exception as e:
			self.log.error(e)
			self.errors += 1

	def stop_if_no_space_left_on_device(self, e: Exception) -> None:
		if 'No space left on device' in str(e):
			self.stop()


class TimeStampSynchronizer(Synchronizer):

	# actions handled by this class
	ACTIONS_CHANGE_DST_FILE = {ACTION.UPDATE, ACTION.DOWNGRADE}
	ACTIONS_CHANGE_SRC_FILE = {ACTION.UNDO_UPDATE, ACTION.UNDO_DOWNGRADE}

	# actions ignored by this class
	ACTIONS_NO_CHANGE = {ACTION.NONE, ACTION.IGNORE, ACTION.ERROR}
	ACTIONS_ONLY_ONE_FILE_EXISTING = {ACTION.CREATE, ACTION.DELETE, ACTION.UNDO_CREATE, ACTION.UNDO_DELETE}
	ACTIONS_DIR = {ACTION.DIR_CHANGE_DESTINATION, ACTION.DIR_CHANGE_SOURCE, ACTION.DIR_CHANGE_BOTH,
		ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN, ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_DESTINATION_TYPE, ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN,
		ACTION.CHANGE_SOURCE_TYPE, ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN}


	files_checked = 0
	files_changed = 0

	@classmethod
	def get_number_files_to_be_checked(cls, cn: ComparisonNode) -> int:
		return sum(cn.statistics[a] for a in cls.ACTIONS_CHANGE_DST_FILE | cls.ACTIONS_CHANGE_SRC_FILE)

	def sync_file(self, node: ComparisonNode) -> None:
		is_link = node.type_src is TYPE.LINK or node.type_dst is TYPE.LINK
		if node.action in self.ACTIONS_CHANGE_DST_FILE:
			self.copy_modification_time(node.path_src, node.path_dst, is_link=is_link)
		elif node.action in self.ACTIONS_CHANGE_SRC_FILE:
			self.copy_modification_time(node.path_dst, node.path_src, is_link=is_link)

	def sync_dir(self, node: DirectoryComparisonNode) -> None:
		for c in node.children:
			self.sync(c)


	def copy_modification_time(self, src: str, dst: str, is_link: bool) -> None:
		# it does not make a difference whether I use shallow=False or not because I have already checked that either the size or the time stamps are different
		if is_link or not filecmp.cmp(src, dst):
			self.files_checked += 1
			return

		self.files_checked += 1

		follow_symlinks = not is_link
		try:
			mtime = os.stat(src, follow_symlinks=follow_symlinks).st_mtime  # I want to copy the modification time from src
			atime = os.stat(dst, follow_symlinks=follow_symlinks).st_atime  # I want to keep the access time of dst unchanged
			os.utime(dst, (atime, mtime), follow_symlinks=follow_symlinks)
			self.files_changed += 1
		except Exception as e:
			self.log.error(e)
			self.errors += 1
