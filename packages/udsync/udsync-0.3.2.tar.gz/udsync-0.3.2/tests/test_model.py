#!../venv/bin/pytest -s

import os
import shutil
import time

from confattr import Config, MultiConfig

import pytest
import typing

from udsync import model
from udsync.model import ComparisonNode, DirectoryComparisonNode, TYPE, STATE, DIRECTION, MIXED_DIRECTION, ACTION, CMP, Statistics, CommandNotAllowed
from udsync.symlink import filesystem_supports_symlinks, create_symlink, SYMLINK_TYPE, config_change_abs_internal_symlink_to_target

PATH_ROOT = 'autotest'
PATH_SRC = PATH_ROOT + os.path.sep + 'src'
PATH_DST = PATH_ROOT + os.path.sep + 'dst'

#appending something so that the file has a different size and is recognized as different
#because they are created too fast so that the modification date does not distinguish them
data = ' '

LOAD_CHILDREN_AUTOMATICALLY = True


# ---------- utils ----------

@pytest.fixture(autouse=True)
def reset_config() -> None:
	reset_config_attribute(ComparisonNode, 'expand_level')
	reset_config_attribute(ComparisonNode, 'compare_mode')

def reset_config_attribute(obj: typing.Any, attr: str) -> None:
	c = getattr(obj, attr)
	assert isinstance(c, Config)
	if not hasattr(c, '__default_value'):
		c.__default_value = c.value  # type: ignore [attr-defined]
	
	c.value = c.__default_value  # type: ignore [attr-defined]

@pytest.fixture(autouse=True)
def create_test_dir() -> None:
	if os.path.exists(PATH_ROOT):
		shutil.rmtree(PATH_ROOT)
	os.mkdir(PATH_ROOT)
	os.mkdir(PATH_SRC)
	os.mkdir(PATH_DST)

def create_file(*path: str, content: typing.Optional[str] = None, older: bool = False, makedirs: bool = False) -> str:
	ffn = os.path.join(*path)
	if makedirs:
		d = os.path.dirname(ffn)
		if not os.path.exists(d):
			os.makedirs(d)
	if content is None:
		content = ffn
	with open(ffn, 'wt') as f:
		f.write(content)
	if older:
		dt_epoch = time.time() - 5
		os.utime(ffn, (dt_epoch, dt_epoch))
	return ffn

def copy_file_from_src_to_dst(*path: str) -> None:
	ffn1 = os.path.join(PATH_SRC, *path)
	ffn2 = os.path.join(PATH_DST, *path)
	copy_file(ffn1, ffn2)

def copy_file(ffn1: str, *path2: str) -> None:
	ffn2 = os.path.sep.join(path2)
	assert os.path.isfile(ffn1)
	assert not os.path.exists(ffn2)
	shutil.copyfile(ffn1, ffn2)

def create_dir(*path: str, multiple: bool = False) -> str:
	ffn = os.path.join(*path)
	if multiple:
		os.makedirs(ffn)
	else:
		os.mkdir(ffn)
	return ffn

def create_link(src: typing.Sequence[str], dst: typing.Sequence[str]) -> None:
	os.symlink(os.path.abspath(os.path.join(*src)), os.path.join(*dst))

def delete_file(*path: str) -> None:
	ffn = os.path.join(*path)
	os.remove(ffn)


def check_node(n: ComparisonNode, *path: str,
	name: typing.Optional[str] = None,
	type_src: TYPE,
	type_dst: TYPE,
	has_children: bool,
	state: STATE,
	direction: DIRECTION,
	action: ACTION,
	has_direction_been_changed: bool,
	realpath: bool = False,
) -> None:
	if name is None:
		name = path[-1]
	def prepend_path(prefix: str, path: typing.Sequence[str]) -> str:
		if not path:
			path = prefix
		else:
			path = os.path.sep.join(path)
			if not path.startswith(prefix):
				path = os.path.join(prefix, path)
		if realpath:
			path = os.path.realpath(path)
		return path
	src = prepend_path(PATH_SRC, path)
	dst = prepend_path(PATH_DST, path)
	assert n.name == name
	assert n.path_src == src
	assert n.path_dst == dst
	assert n.type_src == type_src
	assert n.type_dst == type_dst
	assert n.state    == state
	# Splitting direction into direction and direction_of_children has convinced me
	# that direction is an implementation detail that does not need/should not be tested
	# but I haven't bothered to remove it from tests where it hasn't changed.
	if direction is not None:
		assert n.direction == direction
	assert n.action == action
	assert n.has_children() == has_children
	assert n.has_direction_been_changed() == has_direction_been_changed

def check_dir(n: ComparisonNode, *path: str, **kw: typing.Any) -> None:
	assert isinstance(n, DirectoryComparisonNode)
	kw.setdefault('type_src', TYPE.DIRECTORY)
	kw.setdefault('type_dst', TYPE.DIRECTORY)
	kw.setdefault('direction', None)
	kw.setdefault('has_children', True)
	kw.setdefault('has_direction_been_changed', False)
	has_child_direction_been_changed = kw.pop('has_child_direction_been_changed', False)
	check_node(n, *path, **kw)
	assert n.has_child_direction_been_changed() == has_child_direction_been_changed

def check_file(n: ComparisonNode, *path: str, **kw: typing.Any) -> None:
	kw.setdefault('type_src', TYPE.FILE)
	kw.setdefault('type_dst', TYPE.FILE)
	kw.setdefault('direction', None)
	kw.setdefault('has_children', False)
	kw.setdefault('has_direction_been_changed', False)
	check_node(n, *path, **kw)



class SavedNode:

	def __init__(self, node: ComparisonNode) -> None:
		self.name = node.name
		self.path_src = node.path_src
		self.path_dst = node.path_dst
		self.type_src = node.type_src
		self.type_dst = node.type_dst
		self.state    = node.state
		self.direction = node.direction
		self.action = node.action
		self._has_children = node.has_children()
		if self._has_children:
			assert isinstance(node, DirectoryComparisonNode)
			self.children = [SavedNode(c) for c in node.children]
			self._has_child_direction_been_changed = node.has_child_direction_been_changed()
		self._has_direction_been_changed = node.has_direction_been_changed()

	def has_children(self) -> bool:
		return self._has_children

	def has_direction_been_changed(self) -> bool:
		return self._has_direction_been_changed

	def has_child_direction_been_changed(self) -> bool:
		return self._has_child_direction_been_changed

	def __repr__(self) -> str:
		return '<%s object %s>' % (type(self).__name__, self.path_src)


def copy_node(node: ComparisonNode) -> SavedNode:
	return SavedNode(node)

def assert_unchanged(node_under_test: ComparisonNode, saved_node: SavedNode, *,
	except_for: typing.Mapping[typing.Union[ComparisonNode, str], typing.Dict[str, typing.Any]] = {},
	ignore_children: typing.Set[typing.Union[ComparisonNode, str]] = set(),
) -> None:
	ignore_children = {n.path_src if isinstance(n, ComparisonNode) else n for n in ignore_children}
	except_for = {n.path_src if isinstance(n, ComparisonNode) else n: values for n, values in except_for.items()}

	assert node_under_test.name == saved_node.name
	assert node_under_test.path_src == saved_node.path_src
	assert node_under_test.path_dst == saved_node.path_dst

	if node_under_test.path_src in except_for:
		values = except_for[node_under_test.path_src]
	else:
		values = {}

	assert node_under_test.type_src == saved_node.type_src
	assert node_under_test.type_dst == saved_node.type_dst
	assert node_under_test.state    == saved_node.state
	#if 'direction' in values:
	#	assert node_under_test.direction == values.pop('direction')
	#else:
	#	assert node_under_test.direction == saved_node.direction
	if 'action' in values:
		assert node_under_test.action == values.pop('action')
	else:
		assert node_under_test.action == saved_node.action
	assert node_under_test.has_children() == saved_node.has_children()

	if 'has_direction_been_changed' in values:
		assert node_under_test.has_direction_been_changed() == values.pop('has_direction_been_changed')
	else:
		assert node_under_test.has_direction_been_changed() == saved_node.has_direction_been_changed()

	if node_under_test.has_children():
		assert isinstance(node_under_test, DirectoryComparisonNode)
		assert len(node_under_test.children) == len(saved_node.children)
		for child_under_test, saved_child in zip(node_under_test.children, saved_node.children):
			assert child_under_test.name == saved_child.name
			assert child_under_test.path_src == saved_child.path_src
			assert child_under_test.path_dst == saved_child.path_dst
			if child_under_test.path_src in ignore_children:
				continue
			assert_unchanged(child_under_test, saved_child, except_for=except_for, ignore_children=ignore_children)

		if 'has_child_direction_been_changed' in values:
			assert node_under_test.has_child_direction_been_changed() == values.pop('has_child_direction_been_changed')
		else:
			assert node_under_test.has_child_direction_been_changed() == saved_node.has_child_direction_been_changed()

	if values:
		raise TypeError('invalid parameters: %s' % ', '.join(str(key) for key in values))


def assert_statistics(n: DirectoryComparisonNode, statistics: typing.Mapping[ACTION, int]) -> None:
	assert n.statistics.statistics == statistics


# ---------- unit tests ----------

def test_mappings() -> None:
	assert set(ACTION) - set(Statistics.ACTIONS_CHANGE_DESTINATION) - set(Statistics.ACTIONS_CHANGE_SOURCE) == {ACTION.IGNORE, ACTION.NONE}
	for s in set(STATE) - {STATE.MODIFIED_DIR}:
		assert s in ComparisonNode.state_direction_map
	for d in set(DIRECTION) - {DIRECTION.DEFAULT}:
		assert d in ComparisonNode.direction_state_action_map
		for s in set(STATE) - {STATE.MODIFIED_DIR}:
			assert s in ComparisonNode.direction_state_action_map[d]


def test__is_symlink_circle() -> None:
	create_dir(PATH_SRC, 'a')
	create_dir(PATH_SRC, 'a', '1')
	create_dir(PATH_SRC, 'b')
	create_dir(PATH_SRC, 'b', '2')
	create_link((PATH_SRC, 'a'), (PATH_SRC, 'b', 'a'))
	create_link((PATH_SRC, 'b'), (PATH_SRC, 'a', 'b'))

	assert DirectoryComparisonNode.is_symlink_circle(os.path.join(PATH_SRC, 'a', 'b', 'a'))
	assert DirectoryComparisonNode.is_symlink_circle(os.path.join(PATH_SRC, 'b', 'a', 'b', 'a'))

def test__is_symlink_circle__not() -> None:
	create_dir(PATH_SRC, 'a')
	create_dir(PATH_SRC, 'a', '1')
	create_dir(PATH_SRC, 'b')
	create_dir(PATH_SRC, 'b', '2')
	create_link((PATH_SRC, 'a'), (PATH_SRC, 'b', 'a'))
	create_link((PATH_SRC, 'b'), (PATH_SRC, 'a', 'b'))

	assert not DirectoryComparisonNode.is_symlink_circle(os.path.join(PATH_SRC, 'a', '1'))
	assert not DirectoryComparisonNode.is_symlink_circle(os.path.join(PATH_SRC, 'a', 'b', '2'))
	assert not DirectoryComparisonNode.is_symlink_circle(os.path.join(PATH_SRC, 'a', 'b', 'a', '1'))


# ---------- complete tests ----------

def test_files() -> None:
	create_file(PATH_DST, 'newer', content='this is the old version from dst' + data, older=True)
	create_file(PATH_SRC, 'older', content='this is the old version from src', older=True)

	fn = create_file(PATH_SRC, 'same', content='unchanged')
	copy_file(fn, PATH_DST, 'same')

	create_file(PATH_SRC, 'new', content='a new file')
	create_file(PATH_DST, 'deleted', content='a deleted file')

	create_file(PATH_SRC, 'newer', content='this is the new version from src')
	create_file(PATH_DST, 'older', content='this is the new version from dst' + data)


	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_file(n.children[0], 'deleted', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n.children[1], 'new', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	check_file(n.children[2], 'newer', state=STATE.NEWER, action=ACTION.UPDATE)
	check_file(n.children[3], 'older', state=STATE.OLDER, action=ACTION.DOWNGRADE)
	check_file(n.children[4], 'same', state=STATE.SAME, action=ACTION.NONE)

	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {
		ACTION.UPDATE : 1,
		ACTION.NONE : 1,
		ACTION.CREATE : 1,
		ACTION.DELETE : 1,
		ACTION.DOWNGRADE : 1,
	})


def test_dir_and_update() -> None:
	create_dir (PATH_SRC, 'changed-to-dir')
	create_file(PATH_SRC, 'changed-to-dir', 'f', content='this is now a file in a directory')
	create_file(PATH_DST, 'changed-to-dir', content='this used to be a file')

	create_file(PATH_SRC, 'changed-to-file', content='this is now a file')
	create_dir (PATH_DST, 'changed-to-file')
	create_file(PATH_DST, 'changed-to-file', 'f', content='this used to be a file in a directory')

	create_dir(PATH_SRC, 'empty')
	create_dir(PATH_DST, 'empty')

	fns = []
	p = create_dir(PATH_SRC, 'same')
	fns.append(p)
	fns.append(create_dir (p, 'subdir-a'))
	fns.append(create_file(p, 'subdir-a', 'f0', content='a0'))
	fns.append(create_file(p, 'subdir-a', 'f1', content='a1'))
	fns.append(create_file(p, 'subdir-a', 'f2', content='a2'))
	fns.append(create_dir (p, 'subdir-b'))
	fns.append(create_file(p, 'subdir-b', 'f0', content='b0'))
	fns.append(create_file(p, 'subdir-b', 'f1', content='b1'))
	fns.append(create_file(p, 'subdir-b', 'f2', content='b2'))

	p = create_dir (PATH_SRC, 'different')
	fns.append(p)
	fns.append(create_dir (p, 'subdir-a'))
	fns.append(create_file(p, 'subdir-a', 'f0', content='a0'))
	fns.append(create_file(p, 'subdir-a', 'f1', content='a1'))
	fns.append(create_file(p, 'subdir-a', 'f2', content='a2'))
	fns.append(create_dir (p, 'subdir-b'))
	fns.append(create_file(p, 'subdir-b', 'f0', content='b0'))
	fns.append(create_file(p, 'subdir-b', 'f1', content='b1'))
	fns.append(create_file(p, 'subdir-b', 'f2', content='b2'))
	fns.append(create_dir (p, 'subdir-different'))

	for fn in fns:
		fn_dst = PATH_DST + fn.removeprefix(PATH_SRC)
		if os.path.isdir(fn):
			create_dir(fn_dst)
		else:
			copy_file(fn, fn_dst)

	create_file(PATH_SRC, 'different', 'subdir-different', 'foo', content='foo')
	create_file(PATH_DST, 'different', 'subdir-different', 'bar', content='bar')


	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n.children[0], 'changed-to-dir', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_DESTINATION_TYPE)
	check_dir(n.children[1], 'changed-to-file', type_src=TYPE.FILE, type_dst=TYPE.DIRECTORY, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_DESTINATION_TYPE)

	child = n.children[2]
	child_different = child
	check_dir(child, 'different', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	for i, subdir in enumerate(('subdir-a', 'subdir-b')):
		check_dir(child.children[i], 'different', subdir, state=STATE.SAME, action=ACTION.NONE)
		for j, fn in enumerate(('f0', 'f1', 'f2')):
			check_file(child.children[i].children[j], 'different', subdir, fn, state=STATE.SAME, action=ACTION.NONE)
	child_different_subdir = child.children[i+1]
	check_dir(child_different_subdir, 'different', 'subdir-different', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	assert len(child_different_subdir.children) == 2
	child_bar = child_different_subdir.children[0]
	child_foo = child_different_subdir.children[1]
	check_file(child_bar, 'different', 'subdir-different', 'bar', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(child_foo, 'different', 'subdir-different', 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)

	check_dir(n.children[3], 'empty', state=STATE.SAME, action=ACTION.NONE)

	child = n.children[4]
	check_dir(child, 'same', state=STATE.SAME, action=ACTION.NONE)
	for i, subdir in enumerate(('subdir-a', 'subdir-b')):
		check_dir(child.children[i], 'same', subdir, state=STATE.SAME, action=ACTION.NONE)
		for j, fn in enumerate(('f0', 'f1', 'f2')):
			check_file(child.children[i].children[j], 'same', subdir, fn, state=STATE.SAME, action=ACTION.NONE)

	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {
		ACTION.CHANGE_DESTINATION_TYPE : 2,
		ACTION.NONE : 18,
		ACTION.CREATE : 2,
		ACTION.DELETE : 2,
		ACTION.DIR_CHANGE_DESTINATION : 2,
	})

	os.remove(child_bar.path_dst)
	shutil.copyfile(child_foo.path_src, child_foo.path_dst)

	child_different.update()

	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n.children[0], 'changed-to-dir', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_DESTINATION_TYPE)
	check_dir(n.children[1], 'changed-to-file', type_src=TYPE.FILE, type_dst=TYPE.DIRECTORY, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_DESTINATION_TYPE)

	child = n.children[2]
	child_different = child
	check_dir(child, 'different', state=STATE.SAME, action=ACTION.NONE)
	for i, subdir in enumerate(('subdir-a', 'subdir-b')):
		check_dir(child.children[i], 'different', subdir, state=STATE.SAME, action=ACTION.NONE)
		for j, fn in enumerate(('f0', 'f1', 'f2')):
			check_file(child.children[i].children[j], 'different', subdir, fn, state=STATE.SAME, action=ACTION.NONE)
	child_different_subdir = child.children[i+1]
	check_dir(child_different_subdir, 'different', 'subdir-different', state=STATE.SAME, action=ACTION.NONE)
	assert len(child_different_subdir.children) == 1
	child_foo = child_different_subdir.children[0]
	check_file(child_foo, 'different', 'subdir-different', 'foo', state=STATE.SAME, action=ACTION.NONE)

	check_dir(n.children[3], 'empty', state=STATE.SAME, action=ACTION.NONE)

	child = n.children[4]
	check_dir(child, 'same', state=STATE.SAME, action=ACTION.NONE)
	for i, subdir in enumerate(('subdir-a', 'subdir-b')):
		check_dir(child.children[i], 'same', subdir, state=STATE.SAME, action=ACTION.NONE)
		for j, fn in enumerate(('f0', 'f1', 'f2')):
			check_file(child.children[i].children[j], 'same', subdir, fn, state=STATE.SAME, action=ACTION.NONE)

	assert_statistics(n, {
		ACTION.CHANGE_DESTINATION_TYPE : 2,
		ACTION.CREATE : 1,
		ACTION.DELETE : 1,
		ACTION.NONE : 21,
	})



def test_statistics_of_parent_after_update() -> None:
	create_dir (PATH_SRC, 'dir')
	create_file(PATH_SRC, 'dir', 'a', content='content')
	create_dir (PATH_DST, 'dir')
	create_file(PATH_DST, 'dir', 'b', content='content')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {
		ACTION.DIR_CHANGE_DESTINATION : 1,
		ACTION.CREATE : 1,
		ACTION.DELETE : 1,
	})

	nd, = n.children

	os.rename(os.path.join(PATH_DST, 'dir', 'b'), os.path.join(PATH_DST, 'dir', 'a'))
	nd.update()
	assert_statistics(n, {
		# only 2 because the two files are now the same child
		ACTION.NONE : 2,
	})


def test_unreadable_directory() -> None:
	p = create_dir(PATH_SRC, 'lost+found')
	create_dir(PATH_DST, 'lost+found')
	os.chmod(p, 0)

	try:
		n = ComparisonNode('test', PATH_SRC, PATH_DST)
		n_u, = n.children
		assert isinstance(n, DirectoryComparisonNode)
		assert isinstance(n_u, DirectoryComparisonNode)
		check_dir(n_u, 'lost+found', state=STATE.UNKNOWN, action=ACTION.ERROR)
		assert_statistics(n, {
			ACTION.ERROR : 1,
		})

		n_u.ignore()
		check_dir(n_u, 'lost+found', state=STATE.UNKNOWN, action=ACTION.IGNORE, has_direction_been_changed=True)

		assert_statistics(n, {
			ACTION.IGNORE : 1,
		})

	finally:
		os.chmod(p, 0o777)

def test_parent_of_unreadable_directory() -> None:
	create_dir(PATH_SRC, 'dir')
	create_dir(PATH_DST, 'dir')
	p = create_dir(PATH_SRC, 'dir', 'lost+found')
	create_dir(PATH_DST, 'dir', 'lost+found')
	os.chmod(p, 0)

	try:
		n = ComparisonNode('test', PATH_SRC, PATH_DST)
		n_p, = n.children
		n_u, = n_p.children
		assert isinstance(n, DirectoryComparisonNode)
		assert isinstance(n_p, DirectoryComparisonNode)
		assert isinstance(n_u, DirectoryComparisonNode)
		check_dir(n_u, 'dir', 'lost+found', state=STATE.UNKNOWN, action=ACTION.ERROR)
		check_dir(n_p, 'dir', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH)
		assert_statistics(n, {
			ACTION.ERROR : 1,
			ACTION.DIR_CHANGE_BOTH : 1,
		})

		n_u.ignore()
		check_dir(n_u, 'dir', 'lost+found', state=STATE.UNKNOWN, action=ACTION.IGNORE, has_direction_been_changed=True)

		assert_statistics(n, {
			ACTION.IGNORE : 2,
		})

	finally:
		os.chmod(p, 0o777)


@pytest.mark.skipif(not filesystem_supports_symlinks(PATH_SRC), reason='file system does not support symlinks')
def test_error_symlink_not_supported(monkeypatch: pytest.MonkeyPatch) -> None:
	# I don't need to set virtual_symlinks=False because the mock are_symlinks_supported does not check that, anyway
	monkeypatch.setattr(model, 'are_symlinks_supported', lambda x: False)

	create_file(PATH_SRC, 'target')
	fn_link = os.path.join(PATH_SRC, 'link')
	os.symlink('target', fn_link)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt = n.children
	assert nl.action == ACTION.ERROR
	assert not nl.error_src
	assert nl.error_dst


def test_statistics_for_change_type() -> None:
	create_dir (PATH_SRC, 'changed-to-dir')
	create_file(PATH_SRC, 'changed-to-dir', 'f', content='this is now a file in a directory')
	create_file(PATH_DST, 'changed-to-dir', content='this used to be a file')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_changed, = n.children
	assert isinstance(n_changed, DirectoryComparisonNode)
	n_changed.set_expanded(True)

	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {
		ACTION.CHANGE_DESTINATION_TYPE : 1,
		ACTION.CREATE : 1,
	})

def test_statistics_for_change_type_without_expand() -> None:
	create_dir (PATH_DST, 'changed-to-file')
	create_file(PATH_DST, 'changed-to-file', 'f', content='this used to be a file in a directory')
	create_file(PATH_SRC, 'changed-to-file', content='this is now a file')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_changed, = n.children

	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {
		ACTION.CHANGE_DESTINATION_TYPE : 1,
		ACTION.DELETE : 1,
	})


def test_update_keeps_direction() -> None:
	path = create_dir(PATH_DST, 'parent')
	create_file(path, 'deleted', content='delted file')
	create_file(path, 'modified', content='dest version')

	path = create_dir(PATH_SRC, 'parent')
	create_file(path, 'new', content='new file')
	create_file(path, 'modified', content='src version')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_parent, = n.children
	n_deleted, n_modified, n_new = n_parent.children
	check_file(n_deleted, 'parent', 'deleted', type_src=TYPE.NOT_EXISTING, type_dst=TYPE.FILE, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_modified, 'parent', 'modified', type_src=TYPE.FILE, type_dst=TYPE.FILE, state=STATE.NEWER, direction=DIRECTION.SRC_TO_DST, action=ACTION.UPDATE)
	check_file(n_new, 'parent', 'new', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_deleted.toggle_direction()
	n_modified.ignore()

	check_file(n_deleted, 'parent', 'deleted', type_src=TYPE.NOT_EXISTING, type_dst=TYPE.FILE, state=STATE.DELETED, direction=DIRECTION.DST_TO_SRC, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_modified, 'parent', 'modified', type_src=TYPE.FILE, type_dst=TYPE.FILE, state=STATE.NEWER, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_new, 'parent', 'new', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n.update()
	n_parent, = n.children
	n_deleted, n_modified, n_new = n_parent.children
	check_file(n_deleted, 'parent', 'deleted', type_src=TYPE.NOT_EXISTING, type_dst=TYPE.FILE, state=STATE.DELETED, direction=DIRECTION.DST_TO_SRC, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_modified, 'parent', 'modified', type_src=TYPE.FILE, type_dst=TYPE.FILE, state=STATE.NEWER, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_new, 'parent', 'new', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)


def test_parent_state_after_changing_direction_and_updating_parent() -> None:
	create_file(PATH_SRC, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_a, = n.children
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)

	n_a.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.DST_TO_SRC, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)

	copy_file_from_src_to_dst('a')
	n.update()
	n_a, = n.children
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.FILE, state=STATE.SAME, action=ACTION.NONE, has_direction_been_changed=False)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE, has_child_direction_been_changed=False)

	create_file(PATH_SRC, 'b')
	n.update()
	n_a, n_b = n.children
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.FILE, state=STATE.SAME, direction=DIRECTION.DST_TO_SRC, action=ACTION.NONE)
	check_file(n_b, 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)

def test_parent_state_after_setting_ignore() -> None:
	create_file(PATH_SRC, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_a, = n.children
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)

	n_a.ignore()
	check_file(n_a, 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)




def test_update_children__empty() -> None:
	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert len(n.children) == 0

	n.update()
	assert len(n.children) == 0

def test_update_children__no_change() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b')
	create_file(PATH_SRC, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['a', 'b', 'c']

	n.update()
	assert [c.name for c in n.children] == ['a', 'b', 'c']

def test_update_children__append_new_nodes() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b')
	create_file(PATH_SRC, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['a', 'b', 'c']

	create_file(PATH_SRC, 'd')
	create_file(PATH_SRC, 'e')
	n.update()
	assert [c.name for c in n.children] == ['a', 'b', 'c', 'd', 'e']

def test_update_children__prepend_new_nodes() -> None:
	create_file(PATH_SRC, 'c')
	create_file(PATH_SRC, 'd')
	create_file(PATH_SRC, 'e')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['c', 'd', 'e']

	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b')
	n.update()
	assert [c.name for c in n.children] == ['a', 'b', 'c', 'd', 'e']

def test_update_children__insert_new_nodes() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['a', 'c']

	create_file(PATH_SRC, 'b')
	n.update()
	assert [c.name for c in n.children] == ['a', 'b', 'c']

def test_update_children__delete_nodes() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b')
	create_file(PATH_SRC, 'c')
	create_file(PATH_SRC, 'd')
	create_file(PATH_SRC, 'e')
	create_file(PATH_SRC, 'f')
	create_file(PATH_SRC, 'g')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['a', 'b', 'c', 'd', 'e', 'f', 'g']

	delete_file(PATH_SRC, 'a')
	delete_file(PATH_SRC, 'b')
	delete_file(PATH_SRC, 'd')
	delete_file(PATH_SRC, 'f')
	delete_file(PATH_SRC, 'g')
	n.update()
	assert [c.name for c in n.children] == ['c', 'e']

def test_update_children__replace_node() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b')
	create_file(PATH_SRC, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert [c.name for c in n.children] == ['a', 'b', 'c']

	delete_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'a2')
	delete_file(PATH_SRC, 'c')
	create_file(PATH_SRC, 'c2')
	n.update()
	assert [c.name for c in n.children] == ['a2', 'b', 'c2']


def test_update_error__reset_error_dst() -> None:
	create_file(PATH_SRC, 'target 1')
	create_symlink('target 1', os.path.join(PATH_SRC, 'link'), SYMLINK_TYPE.RELATIVE)
	create_symlink('target 2', os.path.join(PATH_DST, 'link'), SYMLINK_TYPE.RELATIVE)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt1 = n.children
	assert not nl.error_src
	assert nl.error_dst

	delete_file(PATH_SRC, 'target 1')
	create_file(PATH_DST, 'target 2')

	n.update()
	nl, nt2 = n.children
	assert nt1.name != nt2.name
	assert nl.error_src
	assert not nl.error_dst

def test_update_error__reset_error_src() -> None:
	create_file(PATH_DST, 'target 2')
	create_symlink('target 1', os.path.join(PATH_SRC, 'link'), SYMLINK_TYPE.RELATIVE)
	create_symlink('target 2', os.path.join(PATH_DST, 'link'), SYMLINK_TYPE.RELATIVE)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt1 = n.children
	assert nl.error_src
	assert not nl.error_dst

	delete_file(PATH_DST, 'target 2')
	create_file(PATH_SRC, 'target 1')

	n.update()
	nl, nt2 = n.children
	assert nt1.name != nt2.name
	assert not nl.error_src
	assert nl.error_dst


# =============== set_direction_recursively ===============

# ------- STATE.REPLACED_FILE_BY_DIRECTORY -------

def test_change_direction_under_changed_type__dir_to_file() -> None:
	# this is basically the same like test_change_direction_under_new_directory__src_to_dst
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)
	create_file(PATH_DST, 'foo')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_foo, = n.children
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_DESTINATION_TYPE)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_b.set_direction_recursively(DIRECTION.NONE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_DESTINATION_TYPE, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_c.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.DST_TO_SRC, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

def test_change_direction_under_changed_type__ignore() -> None:
	# this is basically the same like test_change_direction_under_new_directory__ignore
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)
	create_file(PATH_DST, 'foo')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.DIR_CHANGE_SOURCE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

def test_change_direction_under_changed_type__file_to_dir() -> None:
	# this is basically the same like test_change_direction_under_new_directory__dst_to_src
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)
	create_file(PATH_DST, 'foo')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.FILE, state=STATE.REPLACED_FILE_BY_DIRECTORY, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)


# ------- STATE.NEW (directory) -------

def test_change_direction_under_new_directory__src_to_dst() -> None:
	# this is basically the same like test_change_direction_under_changed_type__dir_to_file
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_foo, = n.children
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_b.set_direction_recursively(DIRECTION.NONE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)

	n_c.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.DIRECTORY, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.NONE, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.DST_TO_SRC, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

def test_change_direction_under_new_directory__ignore() -> None:
	# this is basically the same like test_change_direction_under_changed_type__ignore
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.DIR_CHANGE_SOURCE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

def test_change_direction_under_new_directory__dst_to_src() -> None:
	# this is basically the same like test_change_direction_under_changed_type__file_to_dir
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)




# ------- STATE.REPLACED_DIRECTORY_BY_FILE -------

def test_change_direction_under_directory_replaced_by_file__src_to_dst() -> None:
	# this is basically the same like test_change_direction_under_deleted_directory__src_to_dst
	create_file(PATH_SRC, 'foo')
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_foo, = n.children
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	with pytest.raises(CommandNotAllowed):
		n_b.set_direction_recursively(DIRECTION.NONE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	with pytest.raises(CommandNotAllowed):
		n_c.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, direction=DIRECTION.SRC_TO_DST, action=ACTION.CHANGE_DESTINATION_TYPE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

def test_change_direction_under_directory_replaced_by_file__ignore() -> None:
	# this is basically the same like test_change_direction_under_deleted_directory__ignore
	create_file(PATH_SRC, 'foo')
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

def test_change_direction_under_directory_replaced_by_file__dst_to_src() -> None:
	# this is basically the same like test_change_direction_under_deleted_directory__dst_to_src
	create_file(PATH_SRC, 'foo')
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_SOURCE_TYPE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.FILE, state=STATE.REPLACED_DIRECTORY_BY_FILE, action=ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)


# ------- STATE.DELETED (directory) -------

def test_change_direction_under_deleted_directory__src_to_dst() -> None:
	# this is basically the same like test_change_direction_under_directory_replaced_by_file__src_to_dst
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_foo, = n.children
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	with pytest.raises(CommandNotAllowed):
		n_b.set_direction_recursively(DIRECTION.NONE)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

	with pytest.raises(CommandNotAllowed):
		n_c.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)

def test_change_direction_under_deleted_directory__ignore() -> None:
	# this is basically the same like test_change_direction_under_directory_replaced_by_file__ignore
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	with pytest.raises(CommandNotAllowed):
		n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DIR_CHANGE_DESTINATION, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

def test_change_direction_under_deleted_directory__dst_to_src() -> None:
	# this is basically the same like test_change_direction_under_directory_replaced_by_file__dst_to_src
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c'):
		create_file(p, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True, has_child_direction_been_changed=LOAD_CHILDREN_AUTOMATICALLY)
	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_b.ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_c.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_BOTH, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n_foo.children
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)


# ------- STATE.MODIFIED_DIR -------

def test_change_direction_under_modified_directory__src_to_dst() -> None:
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c', 'd'):
		create_file(p, fn, content='dst')
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('c', 'd', 'e', 'f'):
		create_file(p, fn, content=fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_a, n_b, n_c, n_d, n_e, n_f = n_foo.children
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_dir(n_foo, 'foo', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, direction=DIRECTION.SRC_TO_DST, action=ACTION.DELETE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE,         state=STATE.NEWER, direction=DIRECTION.SRC_TO_DST, action=ACTION.UPDATE)
	check_file(n_d, 'foo', 'd', type_src=TYPE.FILE,         state=STATE.NEWER, direction=DIRECTION.SRC_TO_DST, action=ACTION.UPDATE)
	check_file(n_e, 'foo', 'e', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	check_file(n_f, 'foo', 'f', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, direction=DIRECTION.SRC_TO_DST, action=ACTION.CREATE)
	n_original = copy_node(n)

	assert isinstance(n_foo, DirectoryComparisonNode)
	n_foo.set_expanded(True)
	assert_unchanged(n, n_original)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_original)
	n_c.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_original)
	n_e.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_original)

	n_a.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_original, except_for = {
		n: dict(has_child_direction_been_changed=True),
		n_foo: dict(has_child_direction_been_changed=True),
		n_a: dict(action=ACTION.IGNORE, has_direction_been_changed=True),
	})
	n_last = copy_node(n)

	n_c.set_direction_recursively(DIRECTION.NONE)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE, state=STATE.NEWER, action=ACTION.IGNORE, has_direction_been_changed=True)
	assert_unchanged(n, n_last, ignore_children={n_c})
	n_last = copy_node(n)

	n_e.set_direction_recursively(DIRECTION.NONE)
	check_file(n_e, 'foo', 'e', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	assert_unchanged(n, n_last, ignore_children={n_e})
	n_last = copy_node(n)

	n_b.set_direction_recursively(DIRECTION.DST_TO_SRC)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_foo : dict(action=ACTION.DIR_CHANGE_BOTH),
	}, ignore_children={n_b})
	n_last = copy_node(n)

	n_d.toggle_direction()
	check_file(n_d, 'foo', 'd', type_src=TYPE.FILE, state=STATE.NEWER, action=ACTION.UNDO_UPDATE, has_direction_been_changed=True)
	assert_unchanged(n, n_last, ignore_children={n_d})
	n_last = copy_node(n)

	n_f.toggle_direction()
	check_file(n_f, 'foo', 'f', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_SOURCE),
		n_foo : dict(action=ACTION.DIR_CHANGE_SOURCE),
	}, ignore_children={n_f})

def test_change_direction_under_modified_directory__ignore() -> None:
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c', 'd'):
		create_file(p, fn, content='dst')
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('c', 'd', 'e', 'f'):
		create_file(p, fn, content=fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)

	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.NONE)

	n_a, n_b, n_c, n_d, n_e, n_f = n_foo.children
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE,         state=STATE.NEWER, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_d, 'foo', 'd', type_src=TYPE.FILE,         state=STATE.NEWER, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_e, 'foo', 'e', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_f, 'foo', 'f', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	n_last = copy_node(n)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_DESTINATION),
		n_foo : dict(action=ACTION.DIR_CHANGE_DESTINATION),
		n_a : dict(action=ACTION.DELETE, has_direction_been_changed=False),
	})
	n_last = copy_node(n)
	n_c.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={n_c:dict(action=ACTION.UPDATE, has_direction_been_changed=False)})
	n_last = copy_node(n)
	n_e.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={n_e:dict(action=ACTION.CREATE, has_direction_been_changed=False)})
	n_last = copy_node(n)

	n_b.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last)
	n_d.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last)
	n_f.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last)

	n_b.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_foo : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_b : dict(action=ACTION.UNDO_DELETE),
	})
	n_last = copy_node(n)
	n_d.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={n_d:dict(action=ACTION.UNDO_UPDATE)})
	n_last = copy_node(n)
	n_f.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={n_f:dict(action=ACTION.UNDO_CREATE)})

def test_change_direction_under_modified_directory__dst_to_src() -> None:
	p = create_dir(PATH_DST, 'foo')
	for fn in ('a', 'b', 'c', 'd'):
		create_file(p, fn, content='dst')
	p = create_dir(PATH_SRC, 'foo')
	for fn in ('c', 'd', 'e', 'f'):
		create_file(p, fn, content=fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)

	n_foo, = n.children
	n_foo.set_direction_recursively(DIRECTION.DST_TO_SRC)

	n_a, n_b, n_c, n_d, n_e, n_f = n_foo.children
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_dir(n_foo, 'foo', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	check_file(n_a, 'foo', 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_b, 'foo', 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)
	check_file(n_c, 'foo', 'c', type_src=TYPE.FILE,         state=STATE.NEWER, action=ACTION.UNDO_UPDATE, has_direction_been_changed=True)
	check_file(n_d, 'foo', 'd', type_src=TYPE.FILE,         state=STATE.NEWER, action=ACTION.UNDO_UPDATE, has_direction_been_changed=True)
	check_file(n_e, 'foo', 'e', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_f, 'foo', 'f', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	n_last = copy_node(n)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_foo : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_a : dict(action=ACTION.DELETE, has_direction_been_changed=False),
	})
	n_last = copy_node(n)
	n_c.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={n_c:dict(action=ACTION.UPDATE, has_direction_been_changed=False)})
	n_last = copy_node(n)
	n_e.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last, except_for={n_e:dict(action=ACTION.CREATE, has_direction_been_changed=False)})
	n_last = copy_node(n)

	n_b.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last, except_for={n_b:dict(action=ACTION.IGNORE)})
	n_last = copy_node(n)
	n_d.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last, except_for={n_d:dict(action=ACTION.IGNORE)})
	n_last = copy_node(n)
	n_f.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_DESTINATION),
		n_foo : dict(action=ACTION.DIR_CHANGE_DESTINATION),
		n_f : dict(action=ACTION.IGNORE),
	})
	n_last = copy_node(n)

	n_b.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={
		n : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_foo : dict(action=ACTION.DIR_CHANGE_BOTH),
		n_b : dict(action=ACTION.UNDO_DELETE),
	})
	n_last = copy_node(n)
	n_d.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={n_d:dict(action=ACTION.UNDO_UPDATE)})
	n_last = copy_node(n)
	n_f.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last, except_for={n_f:dict(action=ACTION.UNDO_CREATE)})


# ------- STATE.SAME -------

def test_change_direction_under_same_directory() -> None:
	p_dst = create_dir(PATH_DST, 'foo')
	p_src = create_dir(PATH_SRC, 'foo')
	for fn in ('a', 'b', 'c'):
		fn_dst = create_file(p_dst, fn)
		copy_file(fn_dst, p_src, fn)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_foo, = n.children
	n_a, n_b, n_c = n_foo.children
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)
	check_dir(n_foo, 'foo', state=STATE.SAME, action=ACTION.NONE)
	check_file(n_a, 'foo', 'a', state=STATE.SAME, action=ACTION.NONE)
	check_file(n_b, 'foo', 'b', state=STATE.SAME, action=ACTION.NONE)
	check_file(n_c, 'foo', 'c', state=STATE.SAME, action=ACTION.NONE)
	n_last = copy_node(n)

	n_a.set_direction_recursively(DIRECTION.SRC_TO_DST)
	assert_unchanged(n, n_last)

	n_a.set_direction_recursively(DIRECTION.NONE)
	assert_unchanged(n, n_last)

	n_a.set_direction_recursively(DIRECTION.DST_TO_SRC)
	assert_unchanged(n, n_last)


# ------- error symlink -------

@pytest.mark.skipif(not filesystem_supports_symlinks(PATH_SRC), reason='file system does not support symlinks')
def test_toggle_direction_on_error_symlink_not_supported(monkeypatch: pytest.MonkeyPatch) -> None:
	# I don't need to set virtual_symlinks=False because the mock are_symlinks_supported does not check that, anyway
	monkeypatch.setattr(model, 'are_symlinks_supported', lambda x: False)

	create_file(PATH_SRC, 'target')
	fn_link = os.path.join(PATH_SRC, 'link')
	os.symlink('target', fn_link)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt = n.children
	assert nl.action == ACTION.ERROR
	assert not nl.error_src
	assert nl.error_dst == 'file system does not support sym links'

	nl.toggle_direction()
	assert nl.action == ACTION.UNDO_CREATE

	nl.toggle_direction()
	assert nl.action == ACTION.ERROR

	nl.ignore()
	assert nl.action == ACTION.IGNORE


# ------- error broken symlink -------

def test_toggle_direction_on_error_broken_symlink_works_if_other_side_is_ok() -> None:
	fn_link = os.path.join(PATH_SRC, 'link')
	os.symlink('target', fn_link)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, = n.children
	assert nl.action == ACTION.ERROR
	assert nl.error_src == 'broken link'
	assert not nl.error_dst

	nl.toggle_direction()
	assert nl.action == ACTION.UNDO_CREATE

	nl.toggle_direction()
	assert nl.action == ACTION.ERROR

	nl.ignore()
	assert nl.action == ACTION.IGNORE
	assert n.action == ACTION.IGNORE

def test_toggle_direction_causes_error_if_other_side_is_broken_symlink() -> None:
	create_file(PATH_SRC, 'target1')
	os.symlink('target1', os.path.join(PATH_SRC, 'link'))
	os.symlink('target2', os.path.join(PATH_DST, 'link'))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt = n.children
	assert nl.action == ACTION.UPDATE
	assert not nl.error_src
	assert nl.error_dst == 'broken link'

	nl.toggle_direction()
	assert nl.action == ACTION.ERROR

	nl.toggle_direction()
	assert nl.action == ACTION.UPDATE

	nl.ignore()
	assert nl.action == ACTION.IGNORE

def test_toggle_direction_broken_link_is_ok_if_equal_link_on_other_side_is_existing() -> None:
	create_file(PATH_SRC, 'target')
	os.symlink('target', os.path.join(PATH_SRC, 'link'))
	os.symlink('target', os.path.join(PATH_DST, 'link'))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, nt = n.children
	assert nl.action == ACTION.NONE
	assert not nl.error_src
	assert not nl.error_dst

	nl.toggle_direction()
	assert nl.action == ACTION.NONE

	nl.toggle_direction()
	assert nl.action == ACTION.NONE

	nl.ignore()
	assert nl.action == ACTION.NONE

def test_toggle_direction_stays_on_error_if_both_sides_are_broken_links() -> None:
	os.symlink('target1', os.path.join(PATH_SRC, 'link'))
	os.symlink('target2', os.path.join(PATH_DST, 'link'))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, = n.children
	assert nl.action == ACTION.ERROR
	assert nl.error_src == 'broken link'
	assert nl.error_dst == 'broken link'

	nl.toggle_direction()
	assert nl.action == ACTION.ERROR

	nl.toggle_direction()
	assert nl.action == ACTION.ERROR

	nl.ignore()
	assert nl.action == ACTION.IGNORE
	assert nl.action == ACTION.IGNORE


def test_same_broken_link_in_dir(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)
	create_dir(PATH_SRC, 'd')
	create_dir(PATH_DST, 'd')
	create_symlink('target', os.path.join(PATH_SRC, 'd', 'link'), SYMLINK_TYPE.ABSOLUTE)
	create_symlink('target', os.path.join(PATH_DST, 'd', 'link'), SYMLINK_TYPE.ABSOLUTE)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nd, = n.children
	nl, = nd.children
	check_file(nl, 'd', 'link', type_src=TYPE.LINK, type_dst=TYPE.LINK, state=STATE.SAME, action=ACTION.ERROR)
	assert nl.error_src == 'broken link'
	assert nl.error_dst == 'broken link'

	n.update()
	nd, = n.children
	nl, = nd.children
	check_file(nl, 'd', 'link', type_src=TYPE.LINK, type_dst=TYPE.LINK, state=STATE.SAME, action=ACTION.ERROR)
	assert nl.error_src == 'broken link'
	assert nl.error_dst == 'broken link'


# =============== toggle_ignore ===============

def test__toggle_ignore__new_file__toggle_back_on_parent() -> None:
	create_file(PATH_SRC, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	n_original = copy_node(n)

	n_a.toggle_ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)

	n.toggle_ignore()
	assert_unchanged(n, n_original)

def test__toggle_ignore__deleted_directory__toggle_back_on_parent() -> None:
	p = create_dir(PATH_DST, 'a')
	create_file(p, 'f')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	assert isinstance(n_a, DirectoryComparisonNode)
	n_a.set_expanded(True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	n_original = copy_node(n)

	n_a.toggle_ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)

	n.toggle_ignore()
	assert_unchanged(n, n_original)

def test__toggle_ignore__new_file() -> None:
	create_file(PATH_SRC, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	n_original = copy_node(n)

	n_a.toggle_ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	n_ignore = copy_node(n)

	n_a.ignore()
	assert_unchanged(n, n_ignore)

	n_a.toggle_ignore()
	assert_unchanged(n, n_original)

	n_a.unignore()
	assert_unchanged(n, n_original)

def test__toggle_ignore__deleted_directory() -> None:
	p = create_dir(PATH_DST, 'a')
	create_file(p, 'f')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	assert isinstance(n_a, DirectoryComparisonNode)
	n_a.set_expanded(True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	n_original = copy_node(n)

	n_a.toggle_ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	n_ignore = copy_node(n)

	n_a.ignore()
	assert_unchanged(n, n_ignore)

	n_a.toggle_ignore()
	assert_unchanged(n, n_original)

	n_a.unignore()
	assert_unchanged(n, n_original)

def test__toggle_ignore__modified_dir() -> None:
	create_file(PATH_SRC, 'a')
	fn = create_file(PATH_SRC, 'b')
	copy_file(fn, PATH_DST, 'b')
	create_file(PATH_DST, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, n_b, n_c = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	check_file(n_b, 'b', state=STATE.SAME, action=ACTION.NONE)
	check_file(n_c, 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	n_original = copy_node(n)

	n.toggle_ignore()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.IGNORE, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.IGNORE, has_direction_been_changed=True)
	check_file(n_b, 'b', state=STATE.SAME, action=ACTION.NONE, has_direction_been_changed=False)
	check_file(n_c, 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.IGNORE, has_direction_been_changed=True)
	n_ignore = copy_node(n)

	n.ignore()
	assert_unchanged(n, n_ignore)

	n.toggle_ignore()
	assert_unchanged(n, n_original)

	n.unignore()
	assert_unchanged(n, n_original)



# =============== toggle_direction ===============

def test__toggle_direction__new_file() -> None:
	create_file(PATH_SRC, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	n_original = copy_node(n)

	n_a.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)

	n_a.toggle_direction()
	assert_unchanged(n, n_original)

def test__toggle_direction__deleted_directory() -> None:
	p = create_dir(PATH_DST, 'a')
	create_file(p, 'f')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	assert isinstance(n_a, DirectoryComparisonNode)
	n_a.set_expanded(True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	n_original = copy_node(n)

	n_a.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	n_a, = n.children
	check_dir(n_a, 'a', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True, has_child_direction_been_changed=True)
	n_a_f, = n_a.children
	check_file(n_a_f, 'a', 'f', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n_a.toggle_direction()
	assert_unchanged(n, n_original)

def test__toggle_direction__modified_dir() -> None:
	create_file(PATH_SRC, 'a')
	fn = create_file(PATH_SRC, 'b')
	copy_file(fn, PATH_DST, 'b')
	create_file(PATH_DST, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)
	n_a, n_b, n_c = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE)
	check_file(n_b, 'b', state=STATE.SAME, action=ACTION.NONE)
	check_file(n_c, 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE)
	n_original = copy_node(n)

	n.toggle_direction()
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_SOURCE, has_child_direction_been_changed=True)
	n_a, n_b, n_c = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.UNDO_CREATE, has_direction_been_changed=True)
	check_file(n_b, 'b', state=STATE.SAME, action=ACTION.NONE, has_direction_been_changed=False)
	check_file(n_c, 'c', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.UNDO_DELETE, has_direction_been_changed=True)

	n.toggle_direction()
	assert_unchanged(n, n_original)


# =============== is_expanded ===============

def test__expand_level_0() -> None:
	ComparisonNode.expand_level.value = 0
	for path in (PATH_SRC, PATH_DST):
		path = create_dir(path, 'a')
		path = create_dir(path, 'b')
		path = create_dir(path, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)
	assert n.is_expanded == False

	n_a, = n.children
	check_dir(n_a, 'a', state=STATE.SAME, action=ACTION.NONE)
	assert n_a.is_expanded == False

	n_b, = n_a.children
	check_dir(n_b, 'a', 'b', state=STATE.SAME, action=ACTION.NONE)
	assert n_b.is_expanded == False

	n_c, = n_b.children
	check_dir(n_c, 'a', 'b', 'c', state=STATE.SAME, action=ACTION.NONE)
	assert n_c.is_expanded == False

def test__expand_level_default() -> None:
	for path in (PATH_SRC, PATH_DST):
		path = create_dir(path, 'a')
		path = create_dir(path, 'b')
		path = create_dir(path, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)
	assert n.is_expanded == True

	n_a, = n.children
	check_dir(n_a, 'a', state=STATE.SAME, action=ACTION.NONE)
	assert n_a.is_expanded == False

	n_b, = n_a.children
	check_dir(n_b, 'a', 'b', state=STATE.SAME, action=ACTION.NONE)
	assert n_b.is_expanded == False

	n_c, = n_b.children
	check_dir(n_c, 'a', 'b', 'c', state=STATE.SAME, action=ACTION.NONE)
	assert n_c.is_expanded == False

def test__expand_level_2() -> None:
	ComparisonNode.expand_level.value = 2
	for path in (PATH_SRC, PATH_DST):
		path = create_dir(path, 'a')
		path = create_dir(path, 'b')
		path = create_dir(path, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)
	assert n.is_expanded == True

	n_a, = n.children
	check_dir(n_a, 'a', state=STATE.SAME, action=ACTION.NONE)
	assert n_a.is_expanded == True

	n_b, = n_a.children
	check_dir(n_b, 'a', 'b', state=STATE.SAME, action=ACTION.NONE)
	assert n_b.is_expanded == False

	n_c, = n_b.children
	check_dir(n_c, 'a', 'b', 'c', state=STATE.SAME, action=ACTION.NONE)
	assert n_c.is_expanded == False

def test__expand_level_inf() -> None:
	ComparisonNode.expand_level.value = -1
	for path in (PATH_SRC, PATH_DST):
		path = create_dir(path, 'a')
		path = create_dir(path, 'b')
		path = create_dir(path, 'c')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)
	assert n.is_expanded == True

	n_a, = n.children
	check_dir(n_a, 'a', state=STATE.SAME, action=ACTION.NONE)
	assert n_a.is_expanded == True

	n_b, = n_a.children
	check_dir(n_b, 'a', 'b', state=STATE.SAME, action=ACTION.NONE)
	assert n_b.is_expanded == True

	n_c, = n_b.children
	check_dir(n_c, 'a', 'b', 'c', state=STATE.SAME, action=ACTION.NONE)
	assert n_c.is_expanded == True


# =============== meta node ===============

def test_meta_node() -> None:
	create_file(PATH_SRC, 'a')
	create_file(PATH_DST, 'b')

	mn = model.MetaNode()
	mn.load([(MultiConfig.default_config_id, PATH_SRC, PATH_DST)])
	assert mn.action is ACTION.DIR_CHANGE_DESTINATION

	n, = mn.children
	check_dir(n, name=os.path.split(PATH_SRC)[0], state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION, realpath=True)
	n_a, n_b = n.children
	check_file(n_a, 'a', type_dst=TYPE.NOT_EXISTING, state=STATE.NEW, action=ACTION.CREATE, realpath=True)
	check_file(n_b, 'b', type_src=TYPE.NOT_EXISTING, state=STATE.DELETED, action=ACTION.DELETE, realpath=True)


# =============== compare mode ===============

def test__files_with_different_content_but_same_size_and_same_timestamp__compare_mode_deep() -> None:
	ComparisonNode.compare_mode.value = CMP.DEEP

	create_file(PATH_SRC, 'm', content='a')
	create_file(PATH_DST, 'm', content='b')
	dt_epoch = time.time()
	os.utime(os.path.join(PATH_SRC, 'm'), (dt_epoch, dt_epoch))
	os.utime(os.path.join(PATH_DST, 'm'), (dt_epoch, dt_epoch))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.MODIFIED_DIR, action=ACTION.DIR_CHANGE_DESTINATION)

	n_a, = n.children
	check_file(n_a, 'm', state=STATE.NEWER, action=ACTION.UPDATE)

def test__files_with_different_content_but_same_size_and_same_timestamp__compare_mode_mixed() -> None:
	ComparisonNode.compare_mode.value = CMP.MIXED

	create_file(PATH_SRC, 'm', content='a')
	create_file(PATH_DST, 'm', content='b')
	dt_epoch = time.time()
	os.utime(os.path.join(PATH_SRC, 'm'), (dt_epoch, dt_epoch))
	os.utime(os.path.join(PATH_DST, 'm'), (dt_epoch, dt_epoch))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)

	n_a, = n.children
	check_file(n_a, 'm', state=STATE.SAME, action=ACTION.NONE)

def test__files_with_different_content_but_same_size_and_same_timestamp__compare_mode_shallow() -> None:
	ComparisonNode.compare_mode.value = CMP.SHALLOW

	create_file(PATH_SRC, 'm', content='a')
	create_file(PATH_DST, 'm', content='b')
	dt_epoch = time.time()
	os.utime(os.path.join(PATH_SRC, 'm'), (dt_epoch, dt_epoch))
	os.utime(os.path.join(PATH_DST, 'm'), (dt_epoch, dt_epoch))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)

	n_a, = n.children
	check_file(n_a, 'm', state=STATE.SAME, action=ACTION.NONE)


# =============== binary files ===============

def test_binary_files_dont_cause_crash() -> None:
	with open(os.path.join(PATH_SRC, 'bin'), 'wb') as f:
		f.write(bytes([255,255,255,255,255]))
	with open(os.path.join(PATH_DST, 'bin'), 'wb') as f:
		f.write(bytes([255,255,255,255,255]))

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	check_dir(n, name='test', state=STATE.SAME, action=ACTION.NONE)

	n_a, = n.children
	check_file(n_a, 'bin', state=STATE.SAME, action=ACTION.NONE)
