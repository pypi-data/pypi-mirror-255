#!../venv/bin/pytest -s -vv

import os
import shutil
import abc
import typing
from collections.abc import Sequence

from confattr import Config, UiNotifier, NotificationLevel, ConfigFileCommand
import confattr.state

import pytest
from defs import ui_callback

from udsync import urwid_multi_key_support as sut

import urwid
urwid.command_map['h'] = urwid.CURSOR_LEFT
urwid.command_map['l'] = urwid.CURSOR_RIGHT

PATH_ROOT = 'autotest'
FN_CONFIG = os.path.join(PATH_ROOT, 'key-mappings')

if typing.TYPE_CHECKING:
	from typing_extensions import Unpack, NotRequired

	class CreateConfigFileParams(typing.TypedDict):
		command_maps: 'NotRequired[dict[str, sut.SubCommandMap]|sut.SubCommandMap]'
		reference_command_map: 'NotRequired[sut.SubCommandMap]'



@pytest.fixture()
def create_test_dir() -> None:
	if os.path.exists(PATH_ROOT):
		shutil.rmtree(PATH_ROOT)
	os.mkdir(PATH_ROOT)

@pytest.fixture()
def reset_config() -> None:
	Config.instances.clear()
	confattr.state.has_config_file_been_instantiated = False
	confattr.state.has_any_config_file_been_instantiated = False

def create_config_file(*, commands: 'Sequence[type[ConfigFileCommand]|abc.ABCMeta]|None' = None, **kw: 'Unpack[CreateConfigFileParams]') -> sut.UrwidConfigFile:
	kw.setdefault('command_maps', sut.SubCommandMap())
	out = sut.UrwidConfigFile(
		appname = 'test',
		notification_level = NotificationLevel.ERROR,   # type: ignore [arg-type]  # I haven't typed this possibility because I don't want to use this in production code
		commands = commands,
		**kw,
	)
	out.set_ui_callback(ui_callback)
	return out


class SutKeyMapper(sut.KeyMapper):

	def __init__(self, command_map: 'sut.SubCommandMap|None' = None):
		if command_map is None:
			command_map = urwid.command_map.copy()
		ui_notifier = UiNotifier()
		ui_notifier.set_ui_callback(ui_callback)
		self.init_key_mapper(ui_notifier, command_map)


# ------- parse_keys -------

def test__parse_keys__single_normal() -> None:
	assert sut.MultiKeySupport.parse_keys('a') == ['a']
	assert sut.MultiKeySupport.parse_keys('9') == ['9']
	assert sut.MultiKeySupport.parse_keys(']') == [']']

def test__parse_keys__single_multi_letter() -> None:
	assert sut.MultiKeySupport.parse_keys('<f5>') == ['f5']
	assert sut.MultiKeySupport.parse_keys('<esc>') == ['esc']
	assert sut.MultiKeySupport.parse_keys('<ctrl o>') == ['ctrl o']

def test__parse_keys__single_special() -> None:
	assert sut.MultiKeySupport.parse_keys('<space>') == [' ']
	assert sut.MultiKeySupport.parse_keys('<less>') == ['<']
	assert sut.MultiKeySupport.parse_keys('<greater>') == ['>']

def test__parse_keys__sequence() -> None:
	assert sut.MultiKeySupport.parse_keys('abc') == ['a', 'b', 'c']
	assert sut.MultiKeySupport.parse_keys(']]') == [']', ']']
	assert sut.MultiKeySupport.parse_keys('<ctrl w><ctrl w>') == ['ctrl w', 'ctrl w']
	assert sut.MultiKeySupport.parse_keys('y<less>p') == ['y', '<', 'p']

def test__parse_keys__less_symbol() -> None:
	assert sut.MultiKeySupport.parse_keys('<') == ['<']
	assert sut.MultiKeySupport.parse_keys('<y') == ['<', 'y']

def test__parse_keys__greater_symbol() -> None:
	assert sut.MultiKeySupport.parse_keys('>') == ['>']
	assert sut.MultiKeySupport.parse_keys('>y') == ['>', 'y']

def test__parse_keys__ctrl_space() -> None:
	assert sut.MultiKeySupport.parse_keys('<<0>>') == ['<0>']


# ------- format_keys -------

def test__format_keys__single_normal() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('a')) == 'a'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('9')) == '9'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys(']')) == ']'

def test__format_keys__single_multi_letter() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<f5>')) == '<f5>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<esc>')) == '<esc>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<ctrl o>')) == '<ctrl o>'

def test__format_keys__single_special() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<space>')) == '<space>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<less>')) == '<less>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<greater>')) == '<greater>'

def test__format_keys__sequence() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('abc')) == 'abc'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys(']]')) == ']]'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<ctrl w><ctrl w>')) == '<ctrl w><ctrl w>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('y<less>p')) == 'y<less>p'

def test__format_keys__less_symbol() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<')) == '<less>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<y')) == '<less>y'

def test__format_keys__greater_symbol() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('>')) == '<greater>'
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('>y')) == '<greater>y'

def test__format_keys__ctrl_space() -> None:
	assert sut.MultiKeySupport.format_keys(sut.MultiKeySupport.parse_keys('<<0>>')) == '<<0>>'


# ------- bind_key, unbind_key etc -------

def test__bind_and_unbind_one_key() -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	w.bind_key('a', 'foo')
	assert w._default_command_map['a'] == 'foo'

	w.unbind_key('a')
	assert w._default_command_map['a'] == None

def test__unbind_all() -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	bound_keys = tuple(sut.iter_commandmap_keys(w._default_command_map))
	assert len(bound_keys) > 0

	w.unbind_key(w.KEY_ALL)

	bound_keys = tuple(sut.iter_commandmap_keys(w._default_command_map))
	assert len(bound_keys) == 0

def test__bind_sequence() -> None:
	w = SutKeyMapper(urwid.command_map.copy())
	w.bind_key('ab', 'bar')

	cmdmap = w._default_command_map['a']
	assert cmdmap is not None
	assert not isinstance(cmdmap, str)
	assert list(sut.iter_commandmap_keys(cmdmap)) == ['b']
	assert list(sut.iter_commandmap_values(cmdmap)) == ['bar']
	assert list(sut.iter_commandmap_items(cmdmap)) == [('b', 'bar')]

def test__replace_command() -> None:
	w = SutKeyMapper(urwid.command_map.copy())
	assert w._default_command_map['left'] == urwid.CURSOR_LEFT
	assert w._default_command_map['h'] == urwid.CURSOR_LEFT
	assert w._default_command_map['right'] == urwid.CURSOR_RIGHT

	sut.replace_command(w._default_command_map, urwid.CURSOR_LEFT, 'collapse')
	assert w._default_command_map['left'] == 'collapse'
	assert w._default_command_map['h'] == 'collapse'

	assert w._default_command_map['right'] == urwid.CURSOR_RIGHT

def test__replace_command__key_sequence() -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	w.bind_key('}', 'foo')
	w.bind_key(']]', 'foo')
	w.bind_key('<ctrl w><ctrl w>', 'foo')
	sut.replace_command(w._default_command_map, 'foo', 'bar')

	assert w._default_command_map['}'] == 'bar'
	assert isinstance(w._default_command_map[']'], sut.SubCommandMap)
	assert w._default_command_map[']'][']'] == 'bar'
	assert isinstance(w._default_command_map['ctrl w'], sut.SubCommandMap)
	assert w._default_command_map['ctrl w']['ctrl w'] == 'bar'


# ------- save and load command maps -------

def test__save1(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())
	w.mapclear()
	assert len(tuple(w.iter_commands_unsorted(w._default_command_map))) == 0

	w.bind_key('a', 'foo')
	w.bind_key('bcd', 'bar baz')

	exporter = create_config_file(command_maps=w._default_command_map, commands=[sut.UrwidConfigFileArgparseCommand])
	exporter.save_file(FN_CONFIG, comments=False)

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
mapclear

map bcd 'bar baz'
map a foo
'''

def test__save__reference_command_map(create_test_dir: None) -> None:
	refmap = sut.SubCommandMap()
	refmap['left'] = urwid.CURSOR_LEFT
	refmap['right'] = urwid.CURSOR_RIGHT
	refmap['up'] = urwid.CURSOR_UP
	refmap['down'] = urwid.CURSOR_DOWN

	diff = SutKeyMapper(refmap.copy())
	edit = SutKeyMapper(refmap.copy())
	menu = SutKeyMapper(refmap.copy())

	diff.bind_key('<left>', 'collapse')
	diff.bind_key('<right>', 'expand')
	diff.bind_key('i', 'diff')

	edit.bind_key('<ctrl u>', 'delete before cursor')
	edit.bind_key('<ctrl k>', 'delete after cursor')
	edit.unbind_key('<up>')
	edit.unbind_key('<down>')

	menu.bind_key('m', 'mount')
	menu.bind_key('u', 'unmount')

	command_maps = dict(diff=diff._default_command_map, edit=edit._default_command_map, menu=menu._default_command_map)
	exporter = create_config_file(command_maps=command_maps, reference_command_map=refmap)
	exporter.save_file(FN_CONFIG, commands=[sut.UrwidConfigFileArgparseCommand])

	with open(FN_CONFIG, 'rt') as f:
		assert f.read() == '''\
mapclear

map '<down>' 'cursor down'
map '<left>' 'cursor left'
map '<right>' 'cursor right'
map '<up>' 'cursor up'

map diff '<left>' collapse
map diff i diff
map diff '<right>' expand

map edit '<ctrl k>' 'delete after cursor'
map edit '<ctrl u>' 'delete before cursor'
unmap edit '<up>'
unmap edit '<down>'

map menu m mount
map menu u unmount
'''



def test__load__map(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())
	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

	with open(FN_CONFIG, 'wt') as f:
		f.write('''\
map a foo
map bcd 'bar baz'
''')

	exporter = create_config_file(command_maps=w._default_command_map)
	exporter.load_file(FN_CONFIG)
	assert w._default_command_map['a'] == 'foo'
	assert isinstance(w._default_command_map['b'], sut.SubCommandMap)
	assert isinstance(w._default_command_map['b']['c'], sut.SubCommandMap)
	assert w._default_command_map['b']['c']['d'] == 'bar baz'
	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

def test__load__map_specific(create_test_dir: None) -> None:
	a = SutKeyMapper()
	b = SutKeyMapper()
	c = SutKeyMapper()
	assert a._default_command_map['left'] == urwid.CURSOR_LEFT
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert a._default_command_map['f'] is None
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['f'] is None
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert c._default_command_map['f'] is None

	with open(FN_CONFIG, 'wt') as f:
		f.write('''\
map  a    <left>  foo
map  a,b  foo     'bar baz'
''')

	command_maps = dict(a=a._default_command_map, b=b._default_command_map, c=c._default_command_map)
	exporter = create_config_file(command_maps=command_maps)
	exporter.load_file(FN_CONFIG)
	assert a._default_command_map['left'] == 'foo'
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT

	assert a._default_command_map['f']['o']['o'] == 'bar baz'  # type: ignore [index]
	assert b._default_command_map['f']['o']['o'] == 'bar baz'  # type: ignore [index]
	assert c._default_command_map['f'] is None

	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT

def test__load__unmap(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

	with open(FN_CONFIG, 'wt') as f:
		f.write('unmap <left>')

	exporter = create_config_file(command_maps=w._default_command_map)
	exporter.load_file(FN_CONFIG)
	assert w._default_command_map['left'] is None

def test__load__unmap_specific(create_test_dir: None) -> None:
	a = SutKeyMapper()
	b = SutKeyMapper()
	c = SutKeyMapper()
	assert a._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT

	with open(FN_CONFIG, 'wt') as f:
		f.write('unmap b,c <left>')

	command_maps = dict(a=a._default_command_map, b=b._default_command_map, c=c._default_command_map)
	exporter = create_config_file(command_maps=command_maps)
	exporter.load_file(FN_CONFIG)
	assert a._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['left'] is None  # mypy does not understand that this value has been changed by exporter.load_file
	assert c._default_command_map['left'] is None  # type: ignore [unreachable]
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT

def test__load__mapclear(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	assert w._default_command_map['left'] == urwid.CURSOR_LEFT
	assert len(tuple(w.iter_commands_unsorted(w._default_command_map))) > 0

	with open(FN_CONFIG, 'wt') as f:
		f.write('mapclear')

	exporter = create_config_file(command_maps=w._default_command_map)
	exporter.load_file(FN_CONFIG)
	assert w._default_command_map['left'] is None  # mypy does not understand that this value has been changed by exporter.load_file
	assert len(tuple(w.iter_commands_unsorted(w._default_command_map))) == 0  # type: ignore [unreachable]

def test__load__mapclear_specific(create_test_dir: None) -> None:
	a = SutKeyMapper()
	b = SutKeyMapper()
	c = SutKeyMapper()
	for m in (a, b, c):
		assert m._default_command_map['left'] == urwid.CURSOR_LEFT
		assert len(tuple(m.iter_commands_unsorted(m._default_command_map))) > 0

	with open(FN_CONFIG, 'wt') as f:
		f.write('mapclear c345,a123')

	command_maps = dict(a123=a._default_command_map, b234=b._default_command_map, c345=c._default_command_map)
	exporter = create_config_file(command_maps=command_maps)
	exporter.load_file(FN_CONFIG)
	for m in (a, c):
		assert m._default_command_map['left'] is None
		assert len(tuple(m.iter_commands_unsorted(m._default_command_map))) == 0

	for m in (b,):
		assert m._default_command_map['left'] == urwid.CURSOR_LEFT
		assert len(tuple(m.iter_commands_unsorted(m._default_command_map))) > 0



def test__save_and_load_default_command(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

	exporter = create_config_file(command_maps=w._default_command_map)
	exporter.save_file(FN_CONFIG)
	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

	w.mapclear()
	assert w._default_command_map['left'] is None

	exporter.load_file(FN_CONFIG)  # type: ignore [unreachable]
	assert w._default_command_map['left'] == urwid.CURSOR_LEFT

def test__save_and_load_undo_bind_key(create_test_dir: None) -> None:
	w = SutKeyMapper(urwid.command_map.copy())

	exporter = create_config_file(command_maps=w._default_command_map)
	exporter.save_file(FN_CONFIG)
	assert w._default_command_map['a'] is None

	w.bind_key('a', 'foo')
	assert w._default_command_map['a'] == 'foo'

	exporter.load_file(FN_CONFIG)
	assert w._default_command_map['a'] is None

def test__save_and_load_multiple_command_maps(create_test_dir: None) -> None:
	a = SutKeyMapper()
	b = SutKeyMapper()
	c = SutKeyMapper()
	assert a._default_command_map['left'] == urwid.CURSOR_LEFT
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert a._default_command_map['f'] is None
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['f'] is None
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert c._default_command_map['f'] is None

	a.bind_key('<left>', 'foo a')
	assert a._default_command_map['left'] == 'foo a'
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT

	b.bind_key('f', 'foo b')
	assert b._default_command_map['f'] == 'foo b'
	assert a._default_command_map['f'] is None

	c.unbind_key('<right>')
	assert c._default_command_map['right'] is None  # it seems mypy does not understand that c.unbind_key has changed this value
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT  # type: ignore [unreachable]

	command_maps = dict(a123=a._default_command_map, b234=b._default_command_map, c345=c._default_command_map)
	exporter = create_config_file(command_maps=command_maps)
	exporter.save_file(FN_CONFIG)
	assert a._default_command_map['left'] == 'foo a'
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert a._default_command_map['f'] is None
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['f'] == 'foo b'
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['right'] is None
	assert c._default_command_map['f'] is None

	a.mapclear()
	assert len(tuple(a.iter_commands_unsorted(a._default_command_map))) == 0
	assert len(tuple(b.iter_commands_unsorted(b._default_command_map))) > 0

	b.bind_key('<right>', 'foo tmp b')
	assert b._default_command_map['right'] == 'foo tmp b'

	c.bind_key('<right>', urwid.CURSOR_RIGHT)
	assert c._default_command_map['right'] == urwid.CURSOR_RIGHT

	exporter.load_file(FN_CONFIG)
	assert a._default_command_map['left'] == 'foo a'
	assert a._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert a._default_command_map['f'] is None
	assert b._default_command_map['left'] == urwid.CURSOR_LEFT
	assert b._default_command_map['right'] == urwid.CURSOR_RIGHT
	assert b._default_command_map['f'] == 'foo b'
	assert c._default_command_map['left'] == urwid.CURSOR_LEFT
	assert c._default_command_map['right'] is None
	assert c._default_command_map['f'] is None


# ------- save and load config -------

def test_save_and_load_help_item(reset_config: None, create_test_dir: None) -> None:
	CURSOR_LEFT = 'cursor left'
	CURSOR_RIGHT = 'cursor right'

	class MyTestClass:
		help_content = Config('fmt', [
			sut.HelpItem(CURSOR_LEFT, 'left'),
			sut.HelpItem(CURSOR_RIGHT, 'right'),
		])

	t = MyTestClass()
	exporter = create_config_file()
	exporter.save_file(FN_CONFIG)
	assert t.help_content == [
		sut.HelpItem(CURSOR_LEFT, 'left'),
		sut.HelpItem(CURSOR_RIGHT, 'right'),
	]

	t.help_content.clear()
	assert t.help_content == []

	exporter.load_file(FN_CONFIG)
	assert t.help_content == [
		sut.HelpItem(CURSOR_LEFT, 'left'),
		sut.HelpItem(CURSOR_RIGHT, 'right'),
	]

def test_save_and_load_help_item_with_alternative_commands(reset_config: None, create_test_dir: None) -> None:
	QUIT = ['quit', 'quit --ask', 'quit --ask-if-long-startup']
	HELP = 'help'

	class MyTestClass:
		help_content = Config('fmt', [
			sut.HelpItem(QUIT, 'quit'),
			sut.HelpItem(HELP, 'help'),
		])

	t = MyTestClass()
	exporter = create_config_file()
	exporter.save_file(FN_CONFIG)
	assert t.help_content == [
		sut.HelpItem(QUIT, 'quit'),
		sut.HelpItem(HELP, 'help'),
	]

	t.help_content.clear()
	assert t.help_content == []

	exporter.load_file(FN_CONFIG)
	assert t.help_content == [
		sut.HelpItem(QUIT, 'quit'),
		sut.HelpItem(HELP, 'help'),
	]



# ------- HelpBar -------

def test_help_bar_is_key_mapped__true_single_command() -> None:
	keymapper = SutKeyMapper()
	keymapper.bind_key('hello', 'hello world')
	assert sut.HelpBar.is_key_mapped('hello', keymapper._default_command_map)

def test_help_bar_is_key_mapped__true_group() -> None:
	keymapper = SutKeyMapper()
	keymapper.bind_key('hellow', 'hello world')
	keymapper.bind_key('hellot', 'hello there')
	assert sut.HelpBar.is_key_mapped('hello', keymapper._default_command_map)


def test_help_bar_is_key_mapped__false_undefed() -> None:
	keymapper = SutKeyMapper()
	assert not sut.HelpBar.is_key_mapped('hello', keymapper._default_command_map)

def test_help_bar_is_key_mapped__false_too_many_keys() -> None:
	keymapper = SutKeyMapper()
	keymapper.bind_key('hel', 'hello world')
	assert not sut.HelpBar.is_key_mapped('hello', keymapper._default_command_map)
