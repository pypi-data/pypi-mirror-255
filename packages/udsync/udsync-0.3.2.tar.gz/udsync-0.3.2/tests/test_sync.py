#!../venv/bin/pytest -s

import os
import time
import logging
import pathlib
import typing

import pytest

from udsync.model import ComparisonNode, DirectoryComparisonNode, TYPE, STATE, ACTION
from udsync.sync import Synchronizer, get_mount_point, PREFERRED_SYMLINK_TYPE
from udsync.symlink import SYMLINK_TYPE, create_symlink, is_symlink, read_symlink, abspath, config_change_abs_internal_symlink_to_target

from test_model import PATH_SRC, PATH_DST, create_test_dir, create_dir, create_file, copy_file, assert_statistics



@pytest.fixture
def tmppath(tmp_path: pathlib.Path) -> str:
	return str(tmp_path)


def assert_file(*path: str, content: str) -> None:
	ffn = os.path.sep.join(path)
	assert os.path.isfile(ffn)
	with open(ffn, 'rt') as f:
		assert f.read() == content

def assert_no_file(*path: str) -> None:
	ffn = os.path.sep.join(path)
	assert not os.path.exists(ffn)

def assert_dir(*path: str) -> None:
	ffn = os.path.sep.join(path)
	assert os.path.isdir(ffn)

assert_no_dir = assert_no_file



class AssertNoErrorHandler(logging.Handler):

	def emit(self, record: logging.LogRecord) -> None:
		if record.levelno >= logging.WARNING:
			assert False, record

@pytest.fixture(autouse=True, scope='session')
def assert_no_errors_in_log() -> None:
	logging.root.addHandler(AssertNoErrorHandler(level=logging.WARNING))



class MockHandler(logging.Handler):

	def __init__(self, log: typing.List[str]) -> None:
		super().__init__()
		self.log = log

	def emit(self, record: logging.LogRecord) -> None:
		if record.levelno >= logging.ERROR:
			self.log.append(record.getMessage())

def get_test_logger() -> typing.Tuple[logging.Logger, typing.Sequence[str]]:
	log: typing.List[str] = []
	logger = logging.getLogger('test')
	logger.propagate = False
	logger.handlers.clear()
	logger.addHandler(MockHandler(log))
	return logger, log


class startswith:

	def __init__(self, prefix: str) -> None:
		self.prefix = prefix

	def __eq__(self, other: typing.Any) -> bool:
		if isinstance(other, str):
			return other.startswith(self.prefix)
		return NotImplemented

	def __repr__(self) -> str:
		return f'{type(self).__name__}({self.prefix!r})'

class contains:

	def __init__(self, infix: str) -> None:
		self.infix = infix

	def __eq__(self, other: typing.Any) -> bool:
		if isinstance(other, str):
			return self.infix in other
		return NotImplemented

	def __repr__(self) -> str:
		return f'{type(self).__name__}({self.infix!r})'


# ------- src -> dst -------

def test_files() -> None:
	data = ''
	create_file(PATH_DST, 'newer', content='this is the old version from dst' + data, older=True)
	create_file(PATH_SRC, 'older', content='this is the old version from src', older=True)

	fn = create_file(PATH_SRC, 'same', content='unchanged')
	copy_file(fn, PATH_DST, 'same')

	create_file(PATH_SRC, 'new', content='a new file')
	create_file(PATH_DST, 'deleted', content='a deleted file')

	create_file(PATH_SRC, 'newer', content='this is the new version from src')
	create_file(PATH_DST, 'older', content='this is the new version from dst' + data)


	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert n.state == STATE.MODIFIED_DIR
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert_file(PATH_SRC, 'newer', content='this is the new version from src')
	assert_file(PATH_DST, 'newer', content='this is the new version from src')

	assert_file(PATH_SRC, 'older', content='this is the old version from src')
	assert_file(PATH_DST, 'older', content='this is the old version from src')

	assert_file(PATH_SRC, 'same', content='unchanged')
	assert_file(PATH_DST, 'same', content='unchanged')

	assert_file(PATH_SRC, 'new', content='a new file')
	assert_file(PATH_DST, 'new', content='a new file')

	assert_no_file(PATH_SRC, 'deleted')
	assert_no_file(PATH_DST, 'deleted')



def test_dir() -> None:
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
	assert n.state == STATE.MODIFIED_DIR
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert_file(PATH_SRC, 'different', 'subdir-different', 'foo', content='foo')
	assert_file(PATH_DST, 'different', 'subdir-different', 'foo', content='foo')
	assert_no_file(PATH_SRC, 'different', 'subdir-different', 'bar')
	assert_no_file(PATH_DST, 'different', 'subdir-different', 'bar')

def test__changed_to_dir__after_expand() -> None:
	create_dir (PATH_SRC, 'changed-to-dir')
	create_file(PATH_SRC, 'changed-to-dir', 'f', content='this is now a file in a directory')
	create_file(PATH_DST, 'changed-to-dir', content='this used to be a file')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert n.state == STATE.MODIFIED_DIR
	nc, = n.children
	assert isinstance(nc, DirectoryComparisonNode)
	nc.set_expanded(True)
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	create_file(PATH_SRC, 'changed-to-dir', 'f', content='this is now a file in a directory')
	create_file(PATH_DST, 'changed-to-dir', 'f', content='this is now a file in a directory')


def test__create_directory() -> None:
	p = create_dir (PATH_SRC, 'new-dir')
	p = create_dir (p, 'new-sub-dir')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nd, = n.children
	assert nd.action is ACTION.CREATE

	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME


def test__create_directory_but_delete_some_children() -> None:
	p = create_dir (PATH_SRC, 'new-dir')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	nb.toggle_direction()
	assert nb.action == ACTION.UNDO_CREATE
	assert na.action == ACTION.CREATE
	assert nd.action == ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN
	assert n.action == ACTION.DIR_CHANGE_BOTH
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'new-dir', 'a', content='a')
		assert_no_file(p, 'new-dir', 'b')

def test__change_destination_type_but_delete_some_children() -> None:
	create_file(PATH_DST, 'changed-to-dir')
	p = create_dir (PATH_SRC, 'changed-to-dir')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	nb.toggle_direction()
	assert nb.action == ACTION.UNDO_CREATE
	assert na.action == ACTION.CREATE
	assert nd.action == ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN
	assert n.action == ACTION.DIR_CHANGE_BOTH
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'changed-to-dir', 'a', content='a')
		assert_no_file(p, 'changed-to-dir', 'b')

def test__change_destination_type() -> None:
	create_file(PATH_SRC, 'changed-to-file', content='this is a file')
	p = create_dir (PATH_DST, 'changed-to-file')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	assert nb.action == ACTION.DELETE
	assert na.action == ACTION.DELETE
	assert nd.action == ACTION.CHANGE_DESTINATION_TYPE
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'changed-to-file', content='this is a file')


# ------- ignore -------

def test__ignore() -> None:
	create_file(PATH_SRC, 'a', content='a file')
	create_file(PATH_SRC, 'b', content='b file')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert n.state == STATE.MODIFIED_DIR
	na, nb = n.children
	nb.ignore()
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.MODIFIED_DIR
	na, nb = n.children
	assert na.state == STATE.SAME
	assert nb.state == STATE.NEW

	assert_file(PATH_SRC, 'a', content='a file')
	create_file(PATH_DST, 'a', content='a file')
	assert_file(PATH_SRC, 'b', content='b file')
	assert_no_file(PATH_DST, 'b')


# ------- dst -> src -------

def test__dst_to_src__file() -> None:
	data = ''
	create_file(PATH_DST, 'newer', content='this is the old version from dst' + data, older=True)
	create_file(PATH_SRC, 'older', content='this is the old version from src', older=True)

	fn = create_file(PATH_SRC, 'same', content='unchanged')
	copy_file(fn, PATH_DST, 'same')

	create_file(PATH_SRC, 'new', content='a new file')
	create_file(PATH_DST, 'deleted', content='a deleted file')

	create_file(PATH_SRC, 'newer', content='this is the new version from src')
	create_file(PATH_DST, 'older', content='this is the new version from dst' + data)


	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	assert n.state == STATE.MODIFIED_DIR
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert_file(PATH_SRC, 'newer', content='this is the old version from dst' + data)
	assert_file(PATH_DST, 'newer', content='this is the old version from dst' + data)

	assert_file(PATH_SRC, 'older', content='this is the new version from dst' + data)
	assert_file(PATH_DST, 'older', content='this is the new version from dst' + data)

	assert_file(PATH_SRC, 'same', content='unchanged')
	assert_file(PATH_DST, 'same', content='unchanged')

	assert_no_file(PATH_SRC, 'new')
	assert_file(PATH_DST, 'deleted', content='a deleted file')



def test__dst_to_src__dir() -> None:
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
	n.toggle_direction()
	assert n.state == STATE.MODIFIED_DIR
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert_file(PATH_SRC, 'different', 'subdir-different', 'bar', content='bar')
	assert_file(PATH_DST, 'different', 'subdir-different', 'bar', content='bar')
	assert_no_file(PATH_SRC, 'different', 'subdir-different', 'foo')
	assert_no_file(PATH_DST, 'different', 'subdir-different', 'foo')

def test__dst_to_src__changed_to_dir__after_expand() -> None:
	create_dir (PATH_SRC, 'changed-to-dir')
	create_file(PATH_SRC, 'changed-to-dir', 'f', content='this is now a file in a directory')
	create_file(PATH_DST, 'changed-to-dir', content='this used to be a file')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	assert n.state == STATE.MODIFIED_DIR
	nc, = n.children
	assert isinstance(nc, DirectoryComparisonNode)
	nc.set_expanded(True)
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	create_file(PATH_SRC, 'changed-to-dir', content='this used to be a file')
	create_file(PATH_DST, 'changed-to-dir', content='this used to be a file')


def test__undo_delete_directory_but_delete_some_children() -> None:
	p = create_dir (PATH_DST, 'new-dir')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	nb.toggle_direction()
	assert nb.action == ACTION.DELETE
	assert na.action == ACTION.UNDO_DELETE
	assert nd.action == ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN
	assert n.action == ACTION.DIR_CHANGE_BOTH
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'new-dir', 'a', content='a')
		assert_no_file(p, 'new-dir', 'b')

def test__change_source_type_but_delete_some_children() -> None:
	create_file(PATH_SRC, 'changed-to-file')
	p = create_dir(PATH_DST, 'changed-to-file')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	nb.toggle_direction()
	assert nb.action == ACTION.DELETE
	assert na.action == ACTION.UNDO_DELETE
	assert nd.action == ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN
	assert n.action == ACTION.DIR_CHANGE_BOTH
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'changed-to-file', 'a', content='a')
		assert_no_file(p, 'changed-to-file', 'b')

def test__change_source_type() -> None:
	create_file(PATH_DST, 'changed-to-dir', content='this is a file')
	p = create_dir(PATH_SRC, 'changed-to-dir')
	create_file(p, 'a', content='a')
	create_file(p, 'b', content='b')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	nd, = n.children
	assert isinstance(nd, DirectoryComparisonNode)
	nd.set_expanded(True)
	na, nb = nd.children
	assert nb.action == ACTION.UNDO_CREATE
	assert na.action == ACTION.UNDO_CREATE
	assert nd.action == ACTION.CHANGE_SOURCE_TYPE
	assert n.action == ACTION.DIR_CHANGE_SOURCE
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		assert_file(p, 'changed-to-dir', content='this is a file')


# ------- ACTION.ERROR -------

def test__action_error_src() -> None:
	create_dir(PATH_SRC, 'dir')
	create_dir(PATH_DST, 'dir')
	p = create_dir(PATH_SRC, 'dir', 'lost+found')
	create_file(p, 'a')
	os.chmod(p, 0)

	try:
		n = ComparisonNode('test', PATH_SRC, PATH_DST)
		n_p, = n.children
		n_u, = n_p.children
		assert n.action is ACTION.DIR_CHANGE_BOTH
		assert n_p.action is ACTION.DIR_CHANGE_BOTH
		assert n_u.action is ACTION.ERROR

		logger, log = get_test_logger()
		s = Synchronizer(logger)
		s.sync(n)

		assert log == [
			'ignoring %s (UNKNOWN) because an exception has occured' % p,
			startswith('    error src'),
		]
		assert_dir(PATH_SRC, 'dir', 'lost+found')
		assert_no_dir(PATH_DST, 'dir', 'lost+found')
		assert_dir(PATH_DST, 'dir')

	finally:
		os.chmod(p, 0o777)

def test__action_error_dst() -> None:
	create_dir(PATH_SRC, 'dir')
	create_dir(PATH_DST, 'dir')
	p = create_dir(PATH_DST, 'dir', 'lost+found')
	create_file(p, 'a')
	os.chmod(p, 0)

	try:
		n = ComparisonNode('test', PATH_SRC, PATH_DST)
		n_p, = n.children
		n_u, = n_p.children
		assert n.action is ACTION.DIR_CHANGE_BOTH
		assert n_p.action is ACTION.DIR_CHANGE_BOTH
		assert n_u.action is ACTION.ERROR

		logger, log = get_test_logger()
		s = Synchronizer(logger)
		s.sync(n)

		assert log == [
			'ignoring %s (UNKNOWN) because an exception has occured' % os.path.join(PATH_SRC, 'dir', 'lost+found'),
			startswith('    error dst: '),
		]
		assert_dir(PATH_DST, 'dir', 'lost+found')
		assert_no_dir(PATH_SRC, 'dir', 'lost+found')
		assert_dir(PATH_SRC, 'dir')

	finally:
		os.chmod(p, 0o777)


# ------- error -------

def test__error__sync_deleted_file() -> None:
	content = 'foo'
	create_file(PATH_SRC, 'a')
	create_file(PATH_SRC, 'b', content=content)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n_a, n_b = n.children
	n_a.action == ACTION.CREATE
	n_b.action == ACTION.CREATE

	os.remove(os.path.join(PATH_SRC, 'a'))

	logger, log = get_test_logger()
	s = Synchronizer(logger)
	s.sync(n)

	assert log == [
		contains("No such file or directory: 'autotest/src/a'"),
	]  # type: ignore [comparison-overlap]

	assert_file(PATH_SRC, 'b', content=content)
	assert_file(PATH_DST, 'b', content=content)

	n.update()
	n_b, = n.children
	assert n.state == STATE.SAME


# ------- get_preferred_symlink_type -------

def test__get_mount_point() -> None:
	path = get_mount_point('any path')
	assert os.path.ismount(path)

def test__get_preferred_link_type__abs(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.ABSOLUTE)

	s = Synchronizer()
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE

def test__get_preferred_link_type__rel(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.RELATIVE)

	s = Synchronizer()
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.RELATIVE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.RELATIVE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.RELATIVE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.RELATIVE

def test__get_preferred_link_type__same(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.SAME)

	s = Synchronizer()
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=True, new_link='any new link') is SYMLINK_TYPE.RELATIVE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.RELATIVE

def test__get_preferred_link_type__auto_abs(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)

	s = Synchronizer()
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=False, new_link='any new link') is SYMLINK_TYPE.ABSOLUTE

def test__get_preferred_link_type__auto_rel(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)

	s = Synchronizer()
	mount_point = os.path.abspath(PATH_DST)
	monkeypatch.setattr(os.path, 'ismount', lambda p: p == mount_point)
	monkeypatch.setattr(s, '_mountpoints', {mount_point})
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.ABSOLUTE, is_internal=True, new_link=os.path.join(PATH_DST, 'new link')) is SYMLINK_TYPE.RELATIVE
	assert s.get_preferred_symlink_type(SYMLINK_TYPE.RELATIVE, is_internal=True, new_link=os.path.join(PATH_DST, 'new link')) is SYMLINK_TYPE.RELATIVE


# ------- sym links auto -------

def test_abs_external_sym_link(monkeypatch: pytest.MonkeyPatch, tmppath: str) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)
	target = create_file(create_dir(tmppath, 'opt'), 'a')
	fn_link = os.path.join(PATH_SRC, 'link')
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nl, = n.children
	assert nl.action == ACTION.CREATE
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (PATH_SRC, PATH_DST):
		l = os.path.join(p, 'link')
		assert is_symlink(l)
		assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, target)

def test_abs_external_sym_link__src_and_dst_have_different_depth(monkeypatch: pytest.MonkeyPatch, tmppath: str) -> None:
	path_src = PATH_SRC
	path_dst = os.path.join(PATH_DST, 'dst')

	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)
	target = create_file(create_dir(tmppath, 'opt'), 'a')
	fn_link = os.path.join(path_src, 'link')
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)

	n = ComparisonNode('test', path_src, path_dst)
	nl, = n.children
	assert nl.action == ACTION.CREATE
	assert n.action == ACTION.CREATE
	Synchronizer().sync(n)

	n.update()
	assert n.state == STATE.SAME

	for p in (path_src, path_dst):
		l = os.path.join(p, 'link')
		assert is_symlink(l)
		assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, target)

def test_rel_internal_sym_link(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)
	monkeypatch.setattr(os.path, 'ismount', lambda p: p == os.path.abspath(PATH_DST))

	create_dir(PATH_SRC, 'wallpaper')
	create_dir(PATH_DST, 'wallpaper')
	fn_link = os.path.join(PATH_SRC, 'wallpaper', '1')
	create_file(create_dir(PATH_SRC, 'nature'), 'ocean.jpg')
	target = os.path.join('..', 'nature', 'ocean.jpg')
	create_symlink(target, fn_link, SYMLINK_TYPE.RELATIVE)
	create_file(PATH_DST, 'wallpaper', '1', older=True)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nt, nd = n.children
	nl, = nd.children
	assert nl.action == ACTION.UPDATE
	assert nd.action == ACTION.DIR_CHANGE_DESTINATION
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	s = Synchronizer()
	monkeypatch.setattr(s, '_mountpoints', {os.path.abspath(PATH_DST)})
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	l = os.path.join(PATH_SRC, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target)

	l = os.path.join(PATH_DST, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target)

def test_abs_internal_sym_link_to_rel(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)
	monkeypatch.setattr(os.path, 'ismount', lambda p: p == os.path.abspath(PATH_DST))

	create_dir(PATH_SRC, 'wallpaper')
	create_dir(PATH_DST, 'wallpaper')
	fn_link = os.path.join(PATH_SRC, 'wallpaper', '1')
	create_file(create_dir(PATH_SRC, 'nature'), 'ocean.jpg')
	target = os.path.join('..', 'nature', 'ocean.jpg')
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)
	create_file(PATH_DST, 'wallpaper', '1', older=True)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nt, nd = n.children
	nl, = nd.children
	assert nl.action == ACTION.UPDATE
	assert nd.action == ACTION.DIR_CHANGE_DESTINATION
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	s = Synchronizer()
	monkeypatch.setattr(s, '_mountpoints', {os.path.abspath(PATH_DST)})
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	l = os.path.join(PATH_SRC, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, abspath(target, link=l))

	l = os.path.join(PATH_DST, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target)

def test_abs_internal_sym_link_to_abs(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.AUTO)
	monkeypatch.setattr(config_change_abs_internal_symlink_to_target, 'value', True)

	create_dir(PATH_SRC, 'wallpaper')
	create_dir(PATH_DST, 'wallpaper')
	fn_link = os.path.join(PATH_SRC, 'wallpaper', '1')
	create_file(create_dir(PATH_SRC, 'nature'), 'ocean.jpg')
	target = os.path.join('..', 'nature', 'ocean.jpg')
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nt, nd = n.children
	nl, = nd.children
	assert nl.action == ACTION.CREATE
	assert nd.action == ACTION.DIR_CHANGE_DESTINATION
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	s = Synchronizer()
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	l = os.path.join(PATH_SRC, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, abspath(target, link=l))

	l = os.path.join(PATH_DST, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, abspath(target, link=l))


# ------- update sym links -------

def test_update_symlink_pointing_to_existing_dir() -> None:
	src = create_dir(PATH_SRC, 'src')
	dst = create_dir(PATH_DST, 'dst')
	create_symlink(os.path.join('..', 'target'), os.path.join(dst, 'link'), SYMLINK_TYPE.ABSOLUTE)
	create_symlink(os.path.join('..', 'target'), os.path.join(src, 'link'), SYMLINK_TYPE.ABSOLUTE)
	create_file(PATH_SRC, 'target', content='src target')

	n = ComparisonNode('test', src, dst)
	nl, = n.children
	assert nl.action is ACTION.UPDATE

	s = Synchronizer()
	s.sync(n)

	assert_file(PATH_SRC, 'target', content='src target')
	assert_no_file(PATH_DST, 'target')

	n.update()
	nl, = n.children
	assert nl.action is ACTION.NONE

def test_update_symlink_pointing_to_not_existing_dir() -> None:
	src = create_dir(PATH_SRC, 'src')
	dst = create_dir(PATH_DST, 'dst')
	create_symlink(os.path.join('..', 'target', 't'), os.path.join(dst, 'link'), SYMLINK_TYPE.ABSOLUTE)
	create_symlink(os.path.join('..', 'target', 't'), os.path.join(src, 'link'), SYMLINK_TYPE.ABSOLUTE)
	create_file(create_dir(PATH_SRC, 'target'), 't', content='src target')

	n = ComparisonNode('test', src, dst)
	nl, = n.children
	assert nl.action is ACTION.UPDATE

	s = Synchronizer()
	s.sync(n)

	assert_file(PATH_SRC, 'target', 't', content='src target')
	assert_no_dir(PATH_DST, 'target')

	n.update()
	nl, = n.children
	assert nl.action is ACTION.NONE


# ------- sym links same -------

def test_same_symlink_internal(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.SAME)
	monkeypatch.setattr(Synchronizer.change_abs_internal_symlink_to_target, 'value', False)

	create_dir(PATH_SRC, 'wallpaper')
	create_dir(PATH_DST, 'wallpaper')
	fn_link_rel = os.path.join(PATH_SRC, 'wallpaper', '1')
	fn_link_abs = os.path.join(PATH_SRC, 'wallpaper', '2')
	create_file(create_dir(PATH_SRC, 'nature'), 'ocean.jpg')
	target_rel = os.path.join('..', 'nature', 'ocean.jpg')
	target_abs = os.path.abspath(create_file(PATH_SRC, 'nature', 'forest.jpg'))
	create_symlink(target_rel, fn_link_rel, SYMLINK_TYPE.RELATIVE)
	create_symlink(target_abs, fn_link_abs, SYMLINK_TYPE.ABSOLUTE)
	create_file(PATH_DST, 'wallpaper', '1', older=True)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nt, nd = n.children
	nlr, nla = nd.children
	assert nlr.action == ACTION.UPDATE
	assert nla.action == ACTION.CREATE
	assert nd.action == ACTION.DIR_CHANGE_DESTINATION
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	s = Synchronizer()
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert is_symlink(fn_link_rel)
	assert read_symlink(fn_link_rel) == (SYMLINK_TYPE.RELATIVE, target_rel)

	assert is_symlink(fn_link_abs)
	assert read_symlink(fn_link_abs) == (SYMLINK_TYPE.ABSOLUTE, target_abs)

	l = os.path.join(PATH_DST, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target_rel)
	l = os.path.join(PATH_DST, 'wallpaper', '2')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, target_abs)

def test_same_symlink_internal__dst_on_removable_device(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.SAME)
	monkeypatch.setattr(Synchronizer.change_abs_internal_symlink_to_target, 'value', False)
	monkeypatch.setattr(os.path, 'ismount', lambda p: p == os.path.abspath(PATH_DST))

	create_dir(PATH_SRC, 'wallpaper')
	create_dir(PATH_DST, 'wallpaper')
	fn_link_rel = os.path.join(PATH_SRC, 'wallpaper', '1')
	fn_link_abs = os.path.join(PATH_SRC, 'wallpaper', '2')
	create_file(create_dir(PATH_SRC, 'nature'), 'ocean.jpg')
	target_rel = os.path.join('..', 'nature', 'ocean.jpg')
	target_abs = os.path.abspath(create_file(PATH_SRC, 'nature', 'forest.jpg'))
	create_symlink(target_rel, fn_link_rel, SYMLINK_TYPE.RELATIVE)
	create_symlink(target_abs, fn_link_abs, SYMLINK_TYPE.ABSOLUTE)
	create_file(PATH_DST, 'wallpaper', '1', older=True)

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	nt, nd = n.children
	nlr, nla = nd.children
	assert nlr.action == ACTION.UPDATE
	assert nla.action == ACTION.CREATE
	assert nd.action == ACTION.DIR_CHANGE_DESTINATION
	assert n.action == ACTION.DIR_CHANGE_DESTINATION
	s = Synchronizer()
	monkeypatch.setattr(s, '_mountpoints', {os.path.abspath(PATH_DST)})
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert is_symlink(fn_link_rel)
	assert read_symlink(fn_link_rel) == (SYMLINK_TYPE.RELATIVE, target_rel)

	assert is_symlink(fn_link_abs)
	assert read_symlink(fn_link_abs) == (SYMLINK_TYPE.ABSOLUTE, target_abs)

	l = os.path.join(PATH_DST, 'wallpaper', '1')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target_rel)
	l = os.path.join(PATH_DST, 'wallpaper', '2')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, target_abs)

def test_same_symlink_external(monkeypatch: pytest.MonkeyPatch, tmppath: str) -> None:
	monkeypatch.setattr(Synchronizer.preferred_symlink_type, 'value', PREFERRED_SYMLINK_TYPE.SAME)
	monkeypatch.setattr(Synchronizer.change_abs_internal_symlink_to_target, 'value', False)

	create_dir(PATH_SRC, 'bin')
	create_file(PATH_SRC, '.local', 'bin', 'gitl', makedirs=True)
	target_rel = os.path.join('..', '.local', 'bin', 'gitl')
	target_abs = create_file(tmppath, 'opt', 'crandr', makedirs=True)

	fn_link_rel = os.path.join(PATH_SRC, 'bin', 'gitl')
	fn_link_abs = os.path.join(PATH_SRC, 'bin', 'crandr')
	create_symlink(target_rel, fn_link_rel, SYMLINK_TYPE.RELATIVE)
	create_symlink(target_abs, fn_link_abs, SYMLINK_TYPE.ABSOLUTE)

	n = ComparisonNode('test', os.path.join(PATH_SRC, 'bin'), os.path.join(PATH_DST, 'bin'))
	assert n.action == ACTION.CREATE
	s = Synchronizer()
	s.sync(n)

	n.update()
	assert n.state == STATE.SAME

	assert is_symlink(fn_link_rel)
	assert read_symlink(fn_link_rel) == (SYMLINK_TYPE.RELATIVE, target_rel)

	assert is_symlink(fn_link_abs)
	assert read_symlink(fn_link_abs) == (SYMLINK_TYPE.ABSOLUTE, target_abs)

	l = os.path.join(PATH_DST, 'bin', 'gitl')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.RELATIVE, target_rel)
	l = os.path.join(PATH_DST, 'bin', 'crandr')
	assert is_symlink(l)
	assert read_symlink(l) == (SYMLINK_TYPE.ABSOLUTE, target_abs)


# ------- sym link change type -------

def test_sym_link_change_type(monkeypatch: pytest.MonkeyPatch) -> None:
	create_dir(PATH_SRC, 'data')
	create_dir(PATH_SRC, '.config')
	create_symlink(os.path.join('..', '.config'), os.path.join(PATH_SRC, 'data', 'config'), SYMLINK_TYPE.ABSOLUTE)
	create_dir(PATH_DST, 'data', 'config', multiple=True)

	# same file
	create_file(PATH_SRC, '.config', 'bashrc', content='alias cd...=\'cd ../..\'')
	create_file(PATH_DST, 'data', 'config', 'bashrc', content='alias cd...=\'cd ../..\'')

	# changed file
	create_file(PATH_SRC, '.config', 'vimrc', content='set mouse=r')
	create_file(PATH_DST, 'data', 'config', 'vimrc', content='set spell')

	n = ComparisonNode('test', os.path.join(PATH_SRC, 'data'), os.path.join(PATH_DST, 'data'))
	nc, = n.children
	assert isinstance(nc, DirectoryComparisonNode)
	assert not nc.error_src
	assert not nc.error_dst
	assert nc.type_src is TYPE.LINK
	assert nc.type_dst is TYPE.DIRECTORY
	assert nc.action is ACTION.CHANGE_DESTINATION_TYPE
	assert not nc.has_direction_been_changed()
	assert not nc.has_child_direction_been_changed()
	assert_statistics(nc, {ACTION.DELETE : 2})

	s = Synchronizer()
	s.sync(n)

	n.update()
	assert n.action is ACTION.NONE
	nc, = n.children
	assert isinstance(nc, ComparisonNode)
	assert not nc.error_src
	assert not nc.error_dst
	assert nc.type_src is TYPE.LINK
	assert nc.type_dst is TYPE.LINK
	assert nc.action is ACTION.NONE
	assert not nc.has_direction_been_changed()

	assert_file(PATH_SRC, '.config', 'bashrc', content='alias cd...=\'cd ../..\'')
	assert_file(PATH_SRC, '.config', 'vimrc', content='set mouse=r')
	assert is_symlink(os.path.join(PATH_SRC, 'data', 'config'))
	assert is_symlink(os.path.join(PATH_DST, 'data', 'config'))

def test_sym_link_change_type_with_error(monkeypatch: pytest.MonkeyPatch) -> None:
	create_dir(PATH_SRC, 'data')
	create_dir(PATH_SRC, '.config')
	create_symlink(os.path.join('..', '.config'), os.path.join(PATH_SRC, 'data', 'config'), SYMLINK_TYPE.ABSOLUTE)
	create_dir(PATH_DST, 'data', 'config', multiple=True)

	# broken link to create an error, src only
	create_dir(PATH_SRC, '.config', 'ranger')
	create_symlink('myrangerconfig', os.path.join(PATH_SRC, '.config', 'ranger', 'rc.conf'), SYMLINK_TYPE.RELATIVE)

	# dst only
	create_file(create_dir(PATH_DST, 'data', 'config', 'imv'), 'config')

	# directory existing on both sides, trying to provoke has_direction_been_changed()
	# because direction of MODIFIED_DIR should always be NONE but passed down is SRC_TO_DST
	create_file(create_dir(PATH_SRC, '.config', 'sway'), 'config', content='sway config')
	create_file(create_dir(PATH_DST, 'data', 'config', 'sway'), 'config', content='i3 config')

	n = ComparisonNode('test', os.path.join(PATH_SRC, 'data'), os.path.join(PATH_DST, 'data'))
	nc, = n.children
	assert isinstance(nc, DirectoryComparisonNode)
	assert not nc.error_src
	assert not nc.error_dst
	assert nc.type_src is TYPE.LINK
	assert nc.type_dst is TYPE.DIRECTORY
	assert nc.action is ACTION.CHANGE_DESTINATION_TYPE
	assert not nc.has_direction_been_changed()
	assert not nc.has_child_direction_been_changed()
	assert_statistics(nc, {ACTION.DELETE : 4})

	s = Synchronizer()
	s.sync(n)

	n.update()
	assert n.action is ACTION.NONE
	nc, = n.children
	assert isinstance(nc, ComparisonNode)
	assert not nc.error_src
	assert not nc.error_dst
	assert nc.type_src is TYPE.LINK
	assert nc.type_dst is TYPE.LINK
	assert nc.action is ACTION.NONE
	assert not nc.has_direction_been_changed()

	assert_file(PATH_SRC, '.config', 'sway', 'config', content='sway config')
	assert is_symlink(os.path.join(PATH_SRC, '.config', 'ranger', 'rc.conf'))
	assert is_symlink(os.path.join(PATH_SRC, 'data', 'config'))
	assert is_symlink(os.path.join(PATH_DST, 'data', 'config'))
