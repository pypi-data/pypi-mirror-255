#!../venv/bin/pytest -s

from udsync.ui import time_difference_to_str

def test__time_difference_to_str__seconds() -> None:
	assert time_difference_to_str(0.5) == '0.50s'
	assert time_difference_to_str(59) == '59.00s'
	assert time_difference_to_str(59.99) == '59.99s'

def test__time_difference_to_str__minutes() -> None:
	assert time_difference_to_str(60) == '1:00min'
	assert time_difference_to_str(62) == '1:02min'
	assert time_difference_to_str(3599) == '59:59min'

def test__time_difference_to_str__hours() -> None:
	assert time_difference_to_str(3600) == '1:00h'
	assert time_difference_to_str(3629) == '1:00h'
	assert time_difference_to_str(3660) == '1:01h'
	assert time_difference_to_str(48*3600) == '48:00h'
