#!/usr/bin/env python3

import os
import enum
import typing

from confattr import Config


virtual_symlinks = Config('symlink.create-virtual-symlinks', True, help={
	True : 'if a file system does not support sym links: create a file which this program will recognize as sym link instead',
	False : 'a sym link which is supposed to be written to a file system which does not support sym links will be displayed as an error',
})
config_change_abs_internal_symlink_to_target = Config('symlink.change-absolute-internal-symlink-to-target', False, help='if the target of an absolute symlink is inside of the synchronized directory change the target to point to the corresponding synchronized file/directory on the other side')


VIRTUAL_SYMLINK_HEADER = b'This file has been created by udsync in place of a symlink because this file system does not support symlinks\n'
LEN_VIRTUAL_SYMLINK_HEADER = len(VIRTUAL_SYMLINK_HEADER)


@enum.unique
class SYMLINK_TYPE(enum.Enum):
	RELATIVE = 'rel'
	ABSOLUTE = 'abs'


class SymlinkSupportChecker:

	_cache: typing.Dict[str, bool] = {}

	def __call__(self, path: str) -> bool:
		if path in self._cache:
			return self._cache[path]

		free_name = self._get_free_name(path)
		try:
			os.symlink('link', free_name)
		except OSError:
			self._cache[path] = False
			return False

		os.remove(free_name)
		self._cache[path] = True
		return True

	def _get_free_name(self, path: str) -> str:
		out = os.path.join(path, '.iiii')
		while os.path.exists(out):
			out += 'i'
		return out

filesystem_supports_symlinks = SymlinkSupportChecker()


def are_symlinks_supported(paths: typing.Sequence[str]) -> bool:
	if virtual_symlinks.value:
		return True
	return all(filesystem_supports_symlinks(p) for p in paths)


def is_symlink(path: str) -> bool:
	if os.path.islink(path):
		return True
	if not virtual_symlinks.value:
		return False
	if not os.path.isfile(path):
		return False
	with open(path, 'rb') as f:
		return f.read(LEN_VIRTUAL_SYMLINK_HEADER) == VIRTUAL_SYMLINK_HEADER


def create_symlink(target: str, new: str, t: SYMLINK_TYPE) -> None:
	'''
	if target is a relative path it is relative to new, not to the current working directory
	'''
	if os.path.islink(new) or os.path.exists(new):
		raise FileExistsError('[Errno 17] File exists: %r' % new)

	isabs = os.path.isabs(target)
	if t is SYMLINK_TYPE.ABSOLUTE:
		if not isabs:
			target = abspath(target, link=new)
	else:
		if isabs:
			target = os.path.relpath(target, start=os.path.dirname(new))

	try:
		os.symlink(target, new)
	except OSError as e:
		if virtual_symlinks.value:
			with open(new, 'wb') as f:
				f.write(VIRTUAL_SYMLINK_HEADER)
				f.write(target.encode('utf-8'))
		else:
			raise e


def read_symlink(path: str) -> typing.Tuple[SYMLINK_TYPE, str]:
	'''
	returns the target as it is, i.e. if it is relative it is relative to path, not to the current working directory
	'''
	try:
		target = os.readlink(path)
	except OSError as e:
		if virtual_symlinks.value:
			with open(path, 'rb') as f:
				if not f.read(LEN_VIRTUAL_SYMLINK_HEADER) == VIRTUAL_SYMLINK_HEADER:
					raise OSError('%r is not a (virtual) sym link' % path)
				target = f.read().decode('utf-8')
		else:
			raise e

	if os.path.isabs(target):
		return SYMLINK_TYPE.ABSOLUTE, target

	return SYMLINK_TYPE.RELATIVE, target


def abspath(target: str, *, link: str) -> str:
	#https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python#comment42739185_51523
	if not os.path.isabs(target):
		path = os.path.dirname(os.path.abspath(link))
		target = os.path.join(path, target)
	return os.path.normpath(target)

def is_internal_link(link: str, target: str, root: str) -> bool:
	target = abspath(target, link=link)
	root = os.path.abspath(root)
	return os.path.commonpath((target, root)) == root

def change_target(target: str, src: str, dst: str) -> str:
	target = abspath(target, link=src)
	target = os.path.relpath(target, start=os.path.dirname(src))
	return abspath(target, link=dst)
