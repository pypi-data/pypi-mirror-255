#!../venv/bin/pytest -s

import os
import typing

import pytest

from udsync.model import ComparisonNode, DirectoryComparisonNode, CMP, STATE, ACTION
from udsync.sync import TimeStampSynchronizer

from test_model import PATH_SRC, PATH_DST, create_test_dir, create_dir, create_file, copy_file, assert_statistics


def get_mtime(*path: str) -> float:
	return os.path.getmtime(os.path.join(*path))

def get_atime(*path: str) -> float:
	return os.path.getatime(os.path.join(*path))


@pytest.fixture(autouse=True)
def config() -> typing.Iterator[None]:
	tmp = ComparisonNode.compare_mode.value
	ComparisonNode.compare_mode.value = CMP.SHALLOW
	yield None
	ComparisonNode.compare_mode.value = tmp


# ------- sets -------

def test_all_actions_considered() -> None:
	EMPTY: typing.Set[ACTION] = set()
	assert set(ACTION) - TimeStampSynchronizer.ACTIONS_CHANGE_DST_FILE - TimeStampSynchronizer.ACTIONS_CHANGE_SRC_FILE \
		- TimeStampSynchronizer.ACTIONS_NO_CHANGE - TimeStampSynchronizer.ACTIONS_ONLY_ONE_FILE_EXISTING - TimeStampSynchronizer.ACTIONS_DIR == EMPTY
	assert TimeStampSynchronizer.ACTIONS_CHANGE_DST_FILE.intersection(TimeStampSynchronizer.ACTIONS_CHANGE_SRC_FILE) == EMPTY


# ------- src-to-dst -------

def test_update_older_dst() -> None:
	content = 'foo'
	create_file(PATH_SRC, 'a', content=content)
	create_file(PATH_DST, 'a', content=content, older=True)

	mtime_src = get_mtime(PATH_SRC, 'a')
	mtime_dst = get_mtime(PATH_DST, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {ACTION.UPDATE : 1})

	TimeStampSynchronizer().sync(n)

	assert get_mtime(PATH_SRC, 'a') == mtime_src
	assert get_mtime(PATH_DST, 'a') == mtime_src

	n.update()
	assert_statistics(n, {ACTION.NONE : 1})

def test_update_newer_dst() -> None:
	content = 'foo'
	create_file(PATH_SRC, 'a', content=content, older=True)
	create_file(PATH_DST, 'a', content=content)

	mtime_src = get_mtime(PATH_SRC, 'a')
	mtime_dst = get_mtime(PATH_DST, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {ACTION.DOWNGRADE : 1})

	TimeStampSynchronizer().sync(n)

	assert get_mtime(PATH_SRC, 'a') == mtime_src
	assert get_mtime(PATH_DST, 'a') == mtime_src

	n.update()
	assert_statistics(n, {ACTION.NONE : 1})


# ------- dst-to-src -------

def test_update_newer_src() -> None:
	content = 'foo'
	create_file(PATH_SRC, 'a', content=content)
	create_file(PATH_DST, 'a', content=content, older=True)

	mtime_src = get_mtime(PATH_SRC, 'a')
	mtime_dst = get_mtime(PATH_DST, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {ACTION.UNDO_UPDATE : 1})

	TimeStampSynchronizer().sync(n)

	assert get_mtime(PATH_SRC, 'a') == mtime_dst
	assert get_mtime(PATH_DST, 'a') == mtime_dst

	n.update()
	assert_statistics(n, {ACTION.NONE : 1})

def test_update_older_src() -> None:
	content = 'foo'
	create_file(PATH_SRC, 'a', content=content, older=True)
	create_file(PATH_DST, 'a', content=content)

	mtime_src = get_mtime(PATH_SRC, 'a')
	mtime_dst = get_mtime(PATH_DST, 'a')

	n = ComparisonNode('test', PATH_SRC, PATH_DST)
	n.toggle_direction()
	assert isinstance(n, DirectoryComparisonNode)
	assert_statistics(n, {ACTION.UNDO_DOWNGRADE : 1})

	TimeStampSynchronizer().sync(n)

	assert get_mtime(PATH_SRC, 'a') == mtime_dst
	assert get_mtime(PATH_DST, 'a') == mtime_dst

	n.update()
	assert_statistics(n, {ACTION.NONE : 1})
