#!/usr/bin/env python3

import pytest
import pathlib

from confattr import Message, NotificationLevel, UiNotifier

def ui_callback(msg: Message) -> None:
	if msg.notification_level >= NotificationLevel.ERROR:
		raise ParseError(msg)

class ParseError(ValueError):
	pass


@pytest.fixture()
def fn_config(tmp_path: pathlib.Path) -> str:
	return str(tmp_path / 'config')
