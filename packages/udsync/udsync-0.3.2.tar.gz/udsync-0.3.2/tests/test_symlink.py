#!../venv/bin/pytest -s

import os

import pytest

from udsync.symlink import SYMLINK_TYPE, is_symlink, create_symlink, read_symlink, abspath, filesystem_supports_symlinks, is_internal_link

from test_model import PATH_SRC, PATH_DST, create_test_dir, create_dir, create_file, copy_file


def mock_symlink(src: str, dst: str) -> None:
	raise OSError()


@pytest.mark.skipif(not filesystem_supports_symlinks(PATH_SRC), reason='requires a file system which supports symlinks')
def test_real_symlink_abs() -> None:
	target = os.path.abspath(create_file(PATH_SRC, 'a'))
	fn_link = os.path.join(PATH_SRC, 'l')

	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)

	assert os.path.islink(fn_link)
	assert os.path.isabs(os.readlink(fn_link))
	assert is_symlink(fn_link)

	content = '9kX379I6umpeMlbQdWHDXvcn1GYcoafZ8dYUb4Bd'
	with open(target, 'wt') as f:
		f.write(content)

	with open(fn_link, 'rt') as f:
		assert f.read() == content

	linktype, linktarget = read_symlink(fn_link)
	assert linktype is SYMLINK_TYPE.ABSOLUTE
	assert os.path.samefile(target, linktarget)

@pytest.mark.skipif(not filesystem_supports_symlinks(PATH_SRC), reason='requires a file system which supports symlinks')
def test_real_symlink_rel() -> None:
	target = os.path.abspath(create_file(PATH_SRC, 'a'))
	fn_link = os.path.join(PATH_SRC, 'l')

	create_symlink(target, fn_link, SYMLINK_TYPE.RELATIVE)

	assert os.path.islink(fn_link)
	assert not os.path.isabs(os.readlink(fn_link))
	assert is_symlink(fn_link)

	content = '9kX379I6umpeMlbQdWHDXvcn1GYcoafZ8dYUb4Bd'
	with open(target, 'wt') as f:
		f.write(content)

	with open(fn_link, 'rt') as f:
		assert f.read() == content

	linktype, linktarget = read_symlink(fn_link)
	assert linktype is SYMLINK_TYPE.RELATIVE
	linktarget = abspath(linktarget, link=fn_link)
	assert os.path.samefile(target, linktarget)


def test_virtual_symlink_rel(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(os, 'symlink', mock_symlink)

	target = os.path.abspath(create_file(PATH_SRC, 'a'))
	fn_link = os.path.join(PATH_SRC, 'l')

	create_symlink(target, fn_link, SYMLINK_TYPE.RELATIVE)

	assert not os.path.islink(fn_link)
	assert is_symlink(fn_link)

	linktype, linktarget = read_symlink(fn_link)
	assert linktype is SYMLINK_TYPE.RELATIVE
	linktarget = abspath(linktarget, link=fn_link)
	assert os.path.samefile(target, linktarget)

def test_virtual_symlink_abs(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(os, 'symlink', mock_symlink)

	target = os.path.abspath(create_file(PATH_SRC, 'a'))
	fn_link = os.path.join(PATH_SRC, 'l')

	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)

	assert not os.path.islink(fn_link)
	assert is_symlink(fn_link)

	linktype, linktarget = read_symlink(fn_link)
	assert linktype is SYMLINK_TYPE.ABSOLUTE
	assert os.path.samefile(target, linktarget)


# ------- create_symlink and read_symlink -------

def test__create_symlink__abs_to_abs() -> None:
	target = '/opt/a'
	fn_link = os.path.join(PATH_SRC, 'link')
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)
	linktype, linktarget = read_symlink(fn_link)
	assert linktarget == target
	assert abspath(linktarget, link=fn_link) == target
	assert linktype is SYMLINK_TYPE.ABSOLUTE

def test__create_symlink__abs_to_rel() -> None:
	target = '/opt/a'
	fn_link = os.path.join(PATH_SRC, 'link')
	create_symlink(target, fn_link, SYMLINK_TYPE.RELATIVE)
	linktype, linktarget = read_symlink(fn_link)
	assert linktarget != target
	assert abspath(linktarget, link=fn_link) == target
	assert linktype is SYMLINK_TYPE.RELATIVE

def test__create_symlink__rel_to_abs() -> None:
	wallpaper = create_dir(PATH_SRC, 'wallpaper')
	fn_link = os.path.join(wallpaper, '1')
	target = '../nature/1'
	create_symlink(target, fn_link, SYMLINK_TYPE.ABSOLUTE)
	linktype, linktarget = read_symlink(fn_link)
	assert linktarget != target
	assert linktarget == abspath(target, link=fn_link)
	assert linktype is SYMLINK_TYPE.ABSOLUTE

def test__create_symlink__rel_to_rel() -> None:
	wallpaper = create_dir(PATH_SRC, 'wallpaper')
	fn_link = os.path.join(wallpaper, '1')
	target = '../nature/1'
	create_symlink(target, fn_link, SYMLINK_TYPE.RELATIVE)
	linktype, linktarget = read_symlink(fn_link)
	assert linktarget == target
	assert linktype is SYMLINK_TYPE.RELATIVE


# ------- is_internal_link -------

def test__is_internal_link__rel_true() -> None:
	root = os.path.expanduser('~')
	link = os.path.join(root, 'wallpaper', '1.jpg')
	target = os.path.join('..', 'nature', '1.jpg')
	assert is_internal_link(link=link, target=target, root=root)

def test__is_internal_link__abs_true() -> None:
	root = os.path.expanduser('~')
	link = os.path.join(root, 'wallpaper', '1.jpg')
	target = os.path.join(root, 'nature', '1.jpg')
	assert is_internal_link(link=link, target=target, root=root)

def test__is_internal_link__false() -> None:
	root = os.path.expanduser('~')
	link = os.path.join(root, 'bin', 'git-viewer')
	target = os.path.join('/', 'opt', 'git-viewer')
	assert not is_internal_link(link=link, target=target, root=root)
