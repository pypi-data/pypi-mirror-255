#!../venv/bin/pytest -s

from udsync import human_bytes

def test__original_values() -> None:
	# the example values from https://stackoverflow.com/a/63839503
	assert human_bytes.format(2251799813685247) == '2.0 PiB'
	assert human_bytes.format(2000000000000000, metric=True) == '2.0 PB'
	assert human_bytes.format(1024**4) == '1.0 TiB'
	assert human_bytes.format(1e12, metric=True) == '1.0 TB'
	assert human_bytes.format(1e9, metric=True) == '1.0 GB'
	assert human_bytes.format(4318498233, precision=3) == '4.022 GiB'
	assert human_bytes.format(4318498233, metric=True, precision=3) == '4.318 GB'
	assert human_bytes.format(-4318498233, precision=2) == '-4.02 GiB'
