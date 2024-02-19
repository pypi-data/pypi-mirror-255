#!../venv/bin/pytest -s


from udsync.model import ACTION, TYPE
from udsync.ui import ComparisonWidget, FileWidget, StatisticsWidget


def test_all_actions_have_a_symbol() -> None:
	for a in ACTION:
		assert a in ComparisonWidget.action_symbol

def test_all_actions_have_a_format() -> None:
	for a in ACTION:
		assert a in ComparisonWidget.action_format

def test_actions_displayed_in_statistics_widget() -> None:
	assert set(ACTION) - set(StatisticsWidget.actions.value) == {ACTION.DIR_CHANGE_DESTINATION, ACTION.DIR_CHANGE_BOTH, ACTION.DIR_CHANGE_SOURCE}

def test_all_types_have_a_symbol_and_color() -> None:
	FileWidget.update_symbols()
	for t in TYPE:
		FileWidget('test', t, t, error='', expanded=False, indent_cols=2)
