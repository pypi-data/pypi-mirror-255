#!/usr/bin/env python3

import subprocess
import time
import random
import typing

N = 50

def iter_test_functions(fn: str) -> typing.Iterator[str]:
	with open(fn) as f:
		for ln in f:
			if not ln.startswith('def '):
				continue

			ln = ln[4:].strip()
			func_name, _ = ln.split('(', 1)
			func_name = func_name.strip()

			if func_name.startswith('test_'):
				yield func_name

def run_tests(fn: str) -> None:
	func_names = list(iter_test_functions(fn))
	width = max(len(name) for name in func_names)
	for name in func_names:
		name = name.ljust(width)
		run_test(fn, name)

def run_test(fn: str, func_name: str) -> bool:
	t0 = time.time()
	for i in range(N):
		p = subprocess.run(['pytest', fn, '-k', func_name.strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
		if p.returncode != 0:
			print(f'!{func_name}  failed  in {i}th try')
			return False
		time.sleep(1.5 / random.randint(1, 20))
	else:
		t = time.time() - t0
		print(f' {func_name}  ok  in {t:1.1f}s')
		return True


if __name__ == '__main__':
	run_tests('test_model.py')
