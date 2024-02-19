#!../venv/bin/pytest -s

import pytest
import typing

from confattr import Config, MultiConfig, ConfigFile
import confattr.state

from defs import fn_config, ui_callback

from udsync.urwid_colors import Color, ColorConfig, ColorStr
from udsync.urwid_multi_key_support import UrwidConfigFileArgparseCommand


class COLOR:

	# ------- foreground -------

	FG_DEFAULT       = 'default'

	FG_BLACK         = 'black'
	FG_RED           = 'dark red'
	FG_GREEN         = 'dark green'
	FG_YELLOW        = 'brown'
	FG_BLUE          = 'dark blue'
	FG_MAGENTA       = 'dark magenta'
	FG_CYAN          = 'dark cyan'
	FG_WHITE         = 'light gray'

	FG_BRIGHT_BLACK   = 'dark gray'
	FG_BRIGHT_RED     = 'light red'
	FG_BRIGHT_GREEN   = 'light green'
	FG_BRIGHT_YELLOW  = 'yellow'
	FG_BRIGHT_BLUE    = 'light blue'
	FG_BRIGHT_MAGENTA = 'light magenta'
	FG_BRIGHT_CYAN    = 'light cyan'
	FG_BRIGHT_WHITE   = 'white'


	# ------- background -------

	BG_DEFAULT = 'default'

	BG_BLACK   = 'black'
	BG_RED     = 'dark red'
	BG_GREEN   = 'dark green'
	BG_YELLOW  = 'brown'
	BG_BLUE    = 'dark blue'
	BG_MAGENTA = 'dark magenta'
	BG_CYAN    = 'dark cyan'
	BG_WHITE   = 'light gray'

	BG_BRIGHT_BLACK   = 'dark gray'
	BG_BRIGHT_RED     = 'light red'
	BG_BRIGHT_GREEN   = 'light green'
	BG_BRIGHT_YELLOW  = 'yellow'
	BG_BRIGHT_BLUE    = 'light blue'
	BG_BRIGHT_MAGENTA = 'light magenta'
	BG_BRIGHT_CYAN    = 'light cyan'
	BG_BRIGHT_WHITE   = 'white'

class EMPH:

	'''usage: COLOR.FG_* + EMPH.BOLD'''

	BOLD      = ',bold'
	UNDERLINE = ',underline'
	STANDOUT  = ',standout'


@pytest.fixture(autouse=True)
def reset_config() -> None:
	Config.instances.clear()
	MultiConfig.config_ids.clear()
	ColorConfig.color_configs.clear()
	confattr.state.has_config_file_been_instantiated = False
	confattr.state.has_any_config_file_been_instantiated = False

def create_config_file() -> ConfigFile:
	config_exporter = ConfigFile(appname='test', ignore_commands=[UrwidConfigFileArgparseCommand])
	config_exporter.set_ui_callback(ui_callback)
	return config_exporter


# ------- Color -------

def test__fg_color_only() -> None:
	assert Color('yellow').to_palette_tuple() == ('yellow/default', COLOR.FG_YELLOW, COLOR.BG_DEFAULT)
	assert Color('default').to_palette_tuple() == ('default/default', COLOR.FG_DEFAULT, COLOR.BG_DEFAULT)

def test__fg_color_and_emph() -> None:
	assert Color('yellow,standout').to_palette_tuple() == ('yellow,standout/default', COLOR.FG_YELLOW + EMPH.STANDOUT, COLOR.BG_DEFAULT)

def test__fg_color_and_two_emph() -> None:
	assert Color('yellow,bold,underline').to_palette_tuple() == ('yellow,bold,underline/default', COLOR.FG_YELLOW + EMPH.BOLD + EMPH.UNDERLINE, COLOR.BG_DEFAULT)

def test__fg_bg() -> None:
	assert Color('black/white').to_palette_tuple() == ('black/white', COLOR.FG_BLACK, COLOR.BG_WHITE)
	assert Color('cyan/default').to_palette_tuple() == ('cyan/default', COLOR.FG_CYAN, COLOR.BG_DEFAULT)

def test__fg_emph_bg() -> None:
	assert Color('red,bold/yellow').to_palette_tuple() == ('red,bold/yellow', COLOR.FG_RED + EMPH.BOLD, COLOR.BG_YELLOW)

def test__specific_attr_name() -> None:
	assert Color('blue', attr_name='myattr').to_palette_tuple() == ('myattr', COLOR.FG_BLUE, COLOR.BG_DEFAULT)


def test__recreate_color() -> None:
	c1 = Color('magenta,strikethrough/green')
	c2 = Color(str(c1))
	assert c1.str_repr == c2.str_repr
	assert c1.fg == c2.fg
	assert c1.bg == c2.bg


# ------- ColorConfig -------

def test__reference__full() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green')
		cr = ColorConfig('color.ref', '{color.original}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == co.bg
	assert cr.str_repr == co.str_repr

def test__reference__implicit_fg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green')
		cr = ColorConfig('color.ref', '{color.original}/blue')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == COLOR.BG_BLUE

def test__reference__implicit_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/blue')
		cr = ColorConfig('color.ref', 'yellow/{color.original}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == COLOR.FG_YELLOW
	assert cr.bg == co.bg

def test__reference__fg_only() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', '{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.fg
	assert cr.bg == COLOR.BG_DEFAULT

def test__reference__fg_as_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', 'default/{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == COLOR.FG_DEFAULT
	assert cr.bg == co.fg

def test__reference__bg_as_fg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'red')
		co = ColorConfig('color.original', 'green/yellow')
		cr = ColorConfig('color.ref', '{color.original.bg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.bg
	assert cr.bg == COLOR.BG_DEFAULT

def test__reference__swap_fg_bg() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'default')
		co = ColorConfig('color.original', 'magenta/cyan')
		cr = ColorConfig('color.ref', '{color.original.bg}/{color.original.fg}')

	co = Test.co.color
	cr = Test.cr.color

	assert cr.fg == co.bg
	assert cr.bg == co.fg

def test__reference__mix_colors() -> None:
	class Test:
		c1 = ColorConfig('color.1', 'default')
		co1 = ColorConfig('color.original-1', 'magenta/cyan')
		co2 = ColorConfig('color.original-2', 'yellow/blue')
		cr1 = ColorConfig('color.ref-1', '{color.original-1.fg}/{color.original-2.bg}')
		cr2 = ColorConfig('color.ref-2', '{color.original-2.fg}/{color.original-1.bg}')

	co1 = Test.co1.color
	co2 = Test.co2.color
	cr1 = Test.cr1.color
	cr2 = Test.cr2.color

	assert cr1.fg == co1.fg
	assert cr1.bg == co2.bg
	assert cr2.fg == co2.fg
	assert cr2.bg == co1.bg


# ------- invalid Color -------

def test__invalid_fg() -> None:
	with pytest.raises(ValueError):
		Color('not existing color')

def test__invalid_emph() -> None:
	with pytest.raises(ValueError):
		Color('default,bold,invalid/default')

def test__invalid_bg() -> None:
	with pytest.raises(ValueError):
		Color('yellow/invalid')


# ------- Color.standout() -------

def test_emphasize() -> None:
	assert Color('default').standout() == 'default,standout/default'
	assert Color('yellow/red').standout() == 'yellow,standout/red'

def test_emphasize_config() -> None:
	class TitleWidget:
		color_title = ColorConfig('color.title', 'yellow/cyan')
		color_title_focus = color_title.focus

	w = TitleWidget()
	assert w.color_title == 'color.title'
	assert w.color_title_focus == 'color.title-focus'

	assert type(w).color_title.color.fg == COLOR.FG_YELLOW
	assert type(w).color_title.color.bg == COLOR.BG_CYAN
	assert type(w).color_title_focus.color.fg == COLOR.FG_YELLOW + EMPH.STANDOUT
	assert type(w).color_title_focus.color.bg == COLOR.BG_CYAN


# ------- ColorStr -------

@pytest.fixture
def registered_colors() -> typing.Set[str]:
	out = set()
	ColorStr.set_register_color(lambda c: out.add(c.str_repr))
	return out

def test_colored_str_to_markup_empty(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('') == ''
	assert set() == registered_colors

def test_colored_str_to_markup_str(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('abc') == 'abc'
	assert set() == registered_colors

def test_colored_str_to_markup_one_color(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('hello <color=red>world</color>') == ['hello ', ('red/default', 'world')]
	assert {'red/default',
		'red,standout/default'} == registered_colors

def test_colored_str_to_markup_nested_colors(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('<color=green>hello <color=red>world</color></color>') == ('green/default', ['hello ', ('red/default', 'world')])
	assert {'green/default', 'red/default',
		'green,standout/default', 'red,standout/default'} == registered_colors

def test_colored_str_to_markup_chained_colors(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('a<color=yellow>b<color=red>c</color>d<color=green>e</color>f</color>g') == ['a', ('yellow/default', ['b', ('red/default', 'c'), 'd', ('green/default', 'e'), 'f']), 'g']
	assert {'yellow/default', 'red/default', 'green/default',
		'yellow,standout/default', 'red,standout/default', 'green,standout/default'} == registered_colors

def test_colored_str_to_markup_missing_closing_tag(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('hello <color=red>world') == ['hello ', ('red/default', 'world')]
	assert {'red/default',
		'red,standout/default'} == registered_colors

def test_colored_str_to_markup_missing_two_closing_tags(registered_colors: typing.Set[str]) -> None:
	assert ColorStr.to_markup('<color=red>hello <color=green>world') == ('red/default', ['hello ', ('green/default', 'world')])
	assert {'red/default', 'green/default',
		'red,standout/default', 'green,standout/default'} == registered_colors

def test_colored_str_to_markup_reference_other_color(registered_colors: typing.Set[str]) -> None:
	ColorConfig('title', 'black/yellow')
	assert ColorStr.to_markup('<color=red>hello <color={title}>world') == ('red/default', ['hello ', ('black/yellow', 'world')])
	assert {'black/yellow', 'red/default',
		'black,standout/yellow', 'red,standout/default',} == registered_colors

def test_colored_str_to_markup_with_format(registered_colors: typing.Set[str]) -> None:
	ColorConfig('O', 'black')
	ColorConfig('I', 'red')
	ColorConfig('II', 'green')
	assert ColorStr.to_markup('{O}<color={I}>{I}<color={II}>{II}</color>{I}', format={'O':'blk', 'I':'red', 'II':'grn'}) == ['blk', ('red/default', ['red', ('green/default', 'grn'), 'red'])]
	assert {'red/default', 'green/default',
		'red,standout/default', 'green,standout/default'} == registered_colors

def test_colored_str_to_markup_with_format_where_values_are_color_str(registered_colors: typing.Set[str]) -> None:
	ColorConfig('O', 'black')
	ColorConfig('I', 'red')
	ColorConfig('II', 'green')
	assert ColorStr.to_markup('{O}<color={I}>{I}<color={II}>{II}</color>{I}', format={'O':'blk', 'I':'r<color=default/red>e</color>d', 'II':'g<color=default/green>r</color>n'}, values_are_color_str=True) \
		== ['blk', ('red/default', [['r', ('default/red', 'e'), 'd'], ('green/default', ['g', ('default/green', 'r'), 'n']), ['r', ('default/red', 'e'), 'd']])]
	assert {'red/default', 'green/default', 'default/red', 'default/green',
		'red,standout/default', 'green,standout/default', 'default,standout/red', 'default,standout/green'} == registered_colors


# ------- simplify_markup -------

def test_simplify_markup__empty_str() -> None:
	assert ColorStr.simplify_markup('') == ''

def test_simplify_markup__non_empty_str() -> None:
	assert ColorStr.simplify_markup('abc') == 'abc'

def test_simplify_markup__easy_tuple() -> None:
	assert ColorStr.simplify_markup(('red', 'abc')) == ('red', 'abc')

def test_simplify_markup__nested_empty_lists() -> None:
	assert ColorStr.simplify_markup([[[]]]) == ''

def test_simplify_markup__nested_and_listed_lists() -> None:
	assert ColorStr.simplify_markup(['a', ['b'], ['c', 'd']]) == ['abcd']

def test_simplify_markup__tuples() -> None:
	assert ColorStr.simplify_markup(['a', [('red', 'b')], [('green', 'c'), 'd']]) == ['a', ('red', 'b'), ('green', 'c'), 'd']

def test_simplify_markup__bug1() -> None:
	color_key = 'red/bright black'
	color_cmd = 'default/bright black'
	color_cmd_sep = 'black/bright black'
	color_key_sep = 'default/bright black'
	markup_in = [
		[(color_key, '<enter> '), (color_cmd, 'browse')],
		(color_cmd_sep, ' │ '),
		[(color_key, ['<tab>', (color_key_sep, '/'), '<ctrl n> ']), (color_cmd, 'focus next')],
		(color_cmd_sep, ' │ '),
		[(color_key, ['<shift tab>', (color_key_sep, '/'), '<ctrl p> ']), (color_cmd, 'focus previous')]
	]
	markup_expected = [
		(color_key, '<enter> '),
		(color_cmd, 'browse'),
		(color_cmd_sep, ' │ '),
		(color_key, '<tab>'),
		(color_key_sep, '/'),
		(color_key, '<ctrl n> '),
		(color_cmd, 'focus next'),
		(color_cmd_sep, ' │ '),
		(color_key, '<shift tab>'),
		(color_key_sep, '/'),
		(color_key, '<ctrl p> '),
		(color_cmd, 'focus previous'),
	]
	assert ColorStr.simplify_markup(markup_in) == markup_expected


# ------- save config -------

def test_save_ignore_default_focus(fn_config: str) -> None:
	class MyTestClass:
		a = ColorConfig('a', 'red')

	config_exporter = create_config_file()
	config_exporter.save_file(fn_config, comments=False)

	with open(fn_config, 'rt') as f:
		assert f.read() == '''\
set a = red/default
'''

def test_save_dont_ignore_default_focus(fn_config: str) -> None:
	class MyTestClass:
		a = ColorConfig('a', 'red', focus='yellow')

	config_exporter = create_config_file()
	config_exporter.save_file(fn_config, comments=False)

	with open(fn_config, 'rt') as f:
		assert f.read() == '''\
set a = red/default
set a-focus = yellow/default
'''


# ------- load config -------

def test_load_set_focus_color(fn_config: str) -> None:
	a = ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(fn_config, 'wt') as f:
		f.write('''
			set a-focus = red
		''')

	config_exporter = create_config_file()
	config_exporter.load_file(fn_config)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'red/default')

def test_load_update_focus_color(fn_config: str) -> None:
	a = ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(fn_config, 'wt') as f:
		f.write('''
			set a = cyan
		''')

	config_exporter = create_config_file()
	config_exporter.load_file(fn_config)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'cyan,standout/default')


def test_load_dont_update_focus_color_if_it_was_given_in_init(fn_config: str) -> None:
	a = ColorConfig('a', 'default', focus='black/yellow')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'black/yellow')

	with open(fn_config, 'wt') as f:
		f.write('''
			set a = cyan
		''')

	config_exporter = create_config_file()
	config_exporter.load_file(fn_config)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'black/yellow')

def test_load_dont_update_focus_color_if_it_was_set_explicitly_in_config_file(fn_config: str) -> None:
	a = ColorConfig('a', 'default')
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'default/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'default,standout/default')

	with open(fn_config, 'wt') as f:
		f.write('''
			set a-focus = magenta/cyan
			set a = cyan
		''')

	config_exporter = create_config_file()
	config_exporter.load_file(fn_config)
	assert (a.color.attr_name, a.color.str_repr) == ('a', 'cyan/default')
	assert (a.focus.color.attr_name, a.focus.color.str_repr) == ('a-focus', 'magenta/cyan')


# ------- save and load config -------

def test_save_and_load_color(fn_config: str) -> None:
	class MyTestClass:
		color = ColorConfig('mycolor', 'default')

	t = MyTestClass()
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'default/default'

	type(t).color.set_value(None, 'red/yellow')
	config_exporter = create_config_file()
	config_exporter.save_file(fn_config)
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'red/yellow'

	type(t).color.set_value(None, 'yellow/blue')
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'yellow/blue'

	config_exporter.load_file(fn_config)
	assert t.color == 'mycolor'
	assert type(t).color.color.str_repr == 'red/yellow'

def test_save_and_load_color_str(fn_config: str) -> None:
	class MyTestClass:
		fmt = Config('fmt', ColorStr('hello world'))

	t = MyTestClass()
	assert t.fmt == 'hello world'

	t.fmt = ColorStr('<color=green>hello</color> <color=blue>world</color>')
	config_exporter = create_config_file()
	config_exporter.save_file(fn_config)
	assert t.fmt == '<color=green>hello</color> <color=blue>world</color>'

	t.fmt = ColorStr('123')
	assert t.fmt == '123'

	config_exporter.load_file(fn_config)
	assert t.fmt == '<color=green>hello</color> <color=blue>world</color>'
