#!/usr/bin/env python3

import mimetypes
import typing

try:
	import magic
	HAS_MAGIC = True
except ImportError:
	HAS_MAGIC = False


def get_mime_type(fn: str) -> str:
	if HAS_MAGIC:
		try:
			return magic.from_file(fn, mime=True)
		except magic.MagicException as e:
			pass

	mime_type, mime_encoding = mimetypes.guess_type(fn)
	if mime_type is not None:
		return mime_type

	return ''


if __name__ == '__main__':
	print(get_mime_type(__file__))
