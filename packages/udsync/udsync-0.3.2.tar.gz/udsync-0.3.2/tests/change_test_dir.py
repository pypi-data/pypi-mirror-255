#!/usr/bin/env python3

'''
a script to modify the test directory in order to test the update functionality in ui.py
'''

import os
import shutil

ROOT = os.path.split(__file__)[0]
PATH_SRC = os.path.join(ROOT, 'test', 'src')
PATH_DST = os.path.join(ROOT, 'test', 'dst')

def exists(*path: str) -> bool:
	fn = os.path.sep.join(path)
	return os.path.exists(fn)

def mkdir(*path: str) -> None:
	dn = os.path.sep.join(path)
	print('mkdir %r' % dn)
	os.mkdir(dn)

def touch(*path: str) -> None:
	fn = os.path.sep.join(path)
	print('touch %r' % fn)
	with open(fn, 'wt') as f:
		f.write(fn)

def create(*path: str) -> None:
	if not exists(*path[:-1]):
		mkdir(*path[:-1])
	touch(*path)

def copy_from_src_to_dst(*path: str) -> None:
	if not exists(PATH_DST, *path[:-1]):
		mkdir(PATH_DST, *path[:-1])
	src = os.path.join(PATH_SRC, *path)
	dst = os.path.join(PATH_DST, *path)
	print('cp %r %r' % (src, dst))
	shutil.copyfile(src, dst)

def rm(*path: str) -> None:
	fn = os.path.sep.join(path)
	print('rm %r' % fn)
	os.remove(fn)

def rm_r(*path: str) -> None:
	dn = os.path.sep.join(path)
	print('rm -r %r' % dn)
	for fn in os.listdir(dn):
		rm(*path, fn)
	os.rmdir(dn)

def test() -> None:
	for dn in ('d0', 'd1'):
		test_1(dn, 'changing')

def test_1(*path: str) -> None:
	if not exists(PATH_SRC, *path):
		mkdir(PATH_SRC, *path)
		if not exists(PATH_DST, *path):
			mkdir(PATH_DST, *path)
		else:
			print('%r exists already' % os.path.join(PATH_DST, *path))
		touch(PATH_SRC, *path, 'a')
	elif not exists(PATH_DST, *path, 'a'):
		copy_from_src_to_dst(*path, 'a')
		create(PATH_SRC, *path, 'b')
	elif not exists(PATH_DST, *path, 'b'):
		copy_from_src_to_dst(*path, 'b')
		create(PATH_SRC, *path, 'c')
	elif not exists(PATH_DST, *path, 'c'):
		copy_from_src_to_dst(*path, 'c')
		create(PATH_SRC, *path, 'd')
	else:
		rm_r(PATH_SRC, *path)
		if exists(PATH_DST, *path):
			rm_r(PATH_DST, *path)
		else:
			print('%r did not exist' % os.path.join(PATH_DST, *path))


if __name__ == '__main__':
	test()
