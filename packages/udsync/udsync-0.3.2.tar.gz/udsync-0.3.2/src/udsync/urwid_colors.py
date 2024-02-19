#!./runmodule.sh

import re
import typing

from confattr import Config, ConfigId, UiNotifier, Primitive, ConfigFile

URWID_TYPE_MARKUP = typing.Any
TYPE_FORMAT = typing.Optional[typing.Mapping[str, typing.Any]]


focus_map: typing.Dict[str, str] = {}


class Color:

	ALLOWED_EMPHASIS = ('standout', 'bold', 'underline', 'italics', 'blink', 'strikethrough')

	foreground_colors = {
		'default' : 'default',

		'black'   : 'black',
		'red'     : 'dark red',
		'green'   : 'dark green',
		'yellow'  : 'brown',
		'blue'    : 'dark blue',
		'magenta' : 'dark magenta',
		'cyan'    : 'dark cyan',
		'white'   : 'light gray',

		'bright black'   : 'dark gray',
		'bright red'     : 'light red',
		'bright green'   : 'light green',
		'bright yellow'  : 'yellow',
		'bright blue'    : 'light blue',
		'bright magenta' : 'light magenta',
		'bright cyan'    : 'light cyan',
		'bright white'   : 'white',
	}

	background_colors = {
		'default' : 'default',

		'black'   : 'black',
		'red'     : 'dark red',
		'green'   : 'dark green',
		'yellow'  : 'brown',
		'blue'    : 'dark blue',
		'magenta' : 'dark magenta',
		'cyan'    : 'dark cyan',
		'white'   : 'light gray',

		'bright black'   : 'dark gray',
		'bright red'     : 'light red',
		'bright green'   : 'light green',
		'bright yellow'  : 'yellow',
		'bright blue'    : 'light blue',
		'bright magenta' : 'light magenta',
		'bright cyan'    : 'light cyan',
		'bright white'   : 'white',
	}

	type_name = 'foreground[,emphases][/background]'
	type_article = None
	help = f'''
	Allowed values for foreground: {', '.join(foreground_colors)}

	Allowed values for background: {', '.join(background_colors)}

	emphases is a comma separated list of: {', '.join(ALLOWED_EMPHASIS)}

	Not all features are supported by all terminals, see
	https://urwid.org/manual/displayattributes.html#foreground-and-background-settings

	You can use {{other-color}}, {{other-color.fg}} or {{other-color.bg}} to use the value of another setting.
	The referenced value is inserted immediately so if you change it later on this color does not change.
	'''

	# separator between foreground and background color in the config file
	SEP_COLOR = '/'

	# separator between foreground color and emphasis in the config file
	SEP_EMPH = ','

	reo_reference = re.compile(r'\{(?P<key>.*?)(.(?P<attr>fg|bg))?\}')

	# ------- init -------

	def __init__(self, str_repr: str, *, attr_name: typing.Optional[str] = None) -> None:
		if self.SEP_COLOR in str_repr:
			fg, bg = str_repr.split(self.SEP_COLOR, 1)
			fg = self.reo_reference.sub(self._replace_references('fg'), fg, 1)
			bg = self.reo_reference.sub(self._replace_references('bg'), bg, 1)
		else:
			str_repr = self.reo_reference.sub(self._replace_references('str_repr'), str_repr, 1)
			if self.SEP_COLOR in str_repr:
				fg, bg = str_repr.split(self.SEP_COLOR, 1)
			else:
				fg = str_repr
				bg = self.background_colors['default']

		self._fg = fg
		self._bg = bg
		self.str_repr = fg + self.SEP_COLOR + bg

		if not attr_name:
			attr_name = self.str_repr

		self.fg = self._convert_fg_to_urwid(fg)
		self.bg = self._convert_bg_to_urwid(bg)
		self.attr_name = attr_name

	def _replace_references(self, default_attr: str) -> typing.Callable[[re.Match[str]], str]:
		def out(m: re.Match[str]) -> str:
			attr = m.group('attr')
			if attr is None:
				attr = default_attr

			key = m.group('key')
			try:
				col = next(cc.color for cc in ColorConfig.color_configs if cc.key == key)
			except StopIteration:
				raise ValueError('undefined color config %r' % key)

			if attr == 'fg':
				return col._fg
			elif attr == 'bg':
				return col._bg
			elif attr == 'str_repr':
				return col.str_repr
			else:
				assert False

		return out


	def _convert_fg_to_urwid(self, fg: str) -> str:
		col_emph = fg.split(self.SEP_EMPH)
		urwid_color_name = self.foreground_colors.get(col_emph[0], None)
		if urwid_color_name is None:
			raise ValueError('invalid foreground color %r' % col_emph[0])
		for i in range(1, len(col_emph)):
			if col_emph[i] not in self.ALLOWED_EMPHASIS:
				raise ValueError('invalid emphasis %r' % col_emph[i])

		col_emph[0] = urwid_color_name
		return ','.join(col_emph)

	def _convert_bg_to_urwid(self, bg: str) -> str:
		urwid_color_name = self.foreground_colors.get(bg, None)
		if urwid_color_name is None:
			raise ValueError('invalid background color %r' % bg)
		return urwid_color_name

	# ------- getters -------

	def __str__(self) -> str:
		return self.str_repr

	def __repr__(self) -> str:
		return '%s(%r, attr_name=%r)' % (type(self).__name__, self.str_repr, self.attr_name)

	def get_attr_name(self) -> str:
		return self.attr_name

	def to_palette_tuple(self) -> typing.Tuple[str, str, str]:
		return (self.attr_name, self.fg, self.bg)

	# ------- generators -------

	def standout(self) -> str:
		return self.toggle_emphasis('standout')

	def toggle_emphasis(self, emph: str) -> str:
		if emph not in self.ALLOWED_EMPHASIS:
			raise ValueError('invalid emph: %r, expected one of %s' % (emph, ', '.join(self.ALLOWED_EMPHASIS)))
		emph = self.SEP_EMPH + emph
		if self.SEP_COLOR in self.str_repr:
			fg, bg = self.str_repr.split(self.SEP_COLOR, 1)
		else:
			fg = self.str_repr
			bg = self.background_colors['default']
		if emph in fg:
			fg = fg.replace(emph, '')
		else:
			fg += emph
		return fg + self.SEP_COLOR + bg


class ColorStr(str):

	type_name = 'str with color markup'
	help = f'''
	A string which can be colored with color tags.
	For example 'hello <color=green>world</color>' would mean 'hello world' with world in green letters.
	Where green could be any value of the form {Color.type_name}.
	'''

	_reo_color_tag = re.compile(r'<color=([^>]*)>|</color>')


	register_color: typing.Optional[typing.Callable[[Color], None]] = None
	logger: typing.Optional[UiNotifier] = None

	@classmethod
	def set_register_color(cls, register_color: typing.Callable[[Color], None]) -> None:
		cls.register_color = register_color

	@classmethod
	def set_logger(cls, logger: UiNotifier) -> None:
		cls.logger = logger

	@classmethod
	def to_markup(cls, color_str: str, *, format: TYPE_FORMAT = None, values_are_color_str: bool = False) -> URWID_TYPE_MARKUP:
		# >>> colored_str_to_markup('hello <color=red>world</color>')
		# l = ['hello ', 'red', 'world', None, '']
		l = cls._reo_color_tag.split(color_str)
		n = len(l)
		out: typing.List[URWID_TYPE_MARKUP] = []

		cls._handle_text(l[0], format, values_are_color_str, out)

		i = 1
		while i < n:
			i = cls._handle_color_tag(l, i, n, format, values_are_color_str, out)
			assert i % 2 == 1

			if i >= n:
				break

			i += 1
			cls._handle_text(l[i], format, values_are_color_str, out)

			i += 1

		if not out:
			return ''

		if len(out) == 1:
			return out[0]

		return out

	@classmethod
	def _handle_color_tag(cls, l: typing.Sequence[typing.Union[str, None]], i: int, n: int, format: TYPE_FORMAT, values_are_color_str: bool, out: typing.List[URWID_TYPE_MARKUP]) -> int:
		color_name = l[i]
		assert isinstance(color_name, str)

		subout: URWID_TYPE_MARKUP
		subout = []

		while i < n:
			assert i % 2 == 1

			i += 1
			cls._handle_text(l[i], format, values_are_color_str, subout)

			i += 1
			if i >= n or l[i] is None:
				break
			else:
				i = cls._handle_color_tag(l, i, n, format, values_are_color_str, subout)

		if subout:
			if len(subout) == 1:
				subout = subout[0]
			try:
				color = Color(color_name)
			except ValueError as e:
				if cls.logger:
					cls.logger.show_error(e)
					out.append(subout)
				else:
					raise e
			else:
				if cls.register_color:
					color_focus = Color(color.standout())
					cls.register_color(color)
					cls.register_color(color_focus)
					focus_map[color.attr_name] = color_focus.attr_name
				out.append((color.get_attr_name(), subout))

		return i

	@classmethod
	def _handle_text(cls, text: typing.Union[str, None], format: TYPE_FORMAT, values_are_color_str: bool, out: typing.List[URWID_TYPE_MARKUP]) -> None:
		assert isinstance(text, str)

		if text:
			if format:
				text = text.format(**format)
				if values_are_color_str:
					markup = cls.to_markup(text)
				else:
					markup = text
			else:
				markup = text
			out.append(markup)


	@classmethod
	def simplify_markup(cls, markup: URWID_TYPE_MARKUP) -> URWID_TYPE_MARKUP:
		out: typing.List[URWID_TYPE_MARKUP] = []
		cls._simplify_markup(out, None, markup)

		if not out:
			return ''

		if len(out) == 1:
			return out[0]

		return cls._merge_markup(out)

	@classmethod
	def _simplify_markup(cls, out: typing.List[URWID_TYPE_MARKUP], attr: typing.Optional[str], markup: URWID_TYPE_MARKUP) -> None:
		if not markup:
			pass
		elif isinstance(markup, str):
			if attr is None:
				out.append(markup)
			else:
				out.append((attr, markup))
		elif isinstance(markup, tuple):
			attr, markup = markup
			cls._simplify_markup(out, attr, markup)
		elif isinstance(markup, list):
			for m in markup:
				cls._simplify_markup(out, attr, m)
		else:
			assert False

	@classmethod
	def _merge_markup(cls, markup: URWID_TYPE_MARKUP) -> URWID_TYPE_MARKUP:
		if isinstance(markup, str):
			return markup
		if isinstance(markup, tuple):
			return markup

		out: typing.List[URWID_TYPE_MARKUP] = []
		last: typing.Optional[URWID_TYPE_MARKUP] = None
		for m in markup:
			if isinstance(m, str) and isinstance(last, str):
				out[-1] += m
			elif isinstance(m, tuple) and isinstance(last, tuple) and m[0] == last[0]:
				out[-1] = (last[0], last[1] + m[1])
			else:
				out.append(m)
			last = m

		return out


class ColorConfigHelp(Primitive[str]):

	def __init__(self) -> None:
		super().__init__(str, type_name = Color.type_name)

	def get_help(self, config_file: 'ConfigFile') -> str:
		return Color.help


class ColorConfig(Config[str]):

	KEY_SUFFIX_FOCUS = '-focus'

	color_configs: typing.List['ColorConfig'] = []

	register_color: typing.Optional[typing.Callable[[Color], None]] = None

	@classmethod
	def set_register_color(cls, register_color: typing.Callable[[Color], None]) -> None:
		cls.register_color = register_color

		for obj in cls.color_configs:
			register_color(obj.color)


	def __init__(self, key: str, color: str, focus: typing.Optional[str] = None) -> None:
		# The value is the attribute name I pass to urwid, not the color str
		super().__init__(key, key, type=ColorConfigHelp())
		self.color = Color(color, attr_name=self.value)
		if self.register_color:
			self.register_color(self.color)
		type(self).color_configs.append(self)
		self.init_focus(focus)

	def init_focus(self, color: typing.Optional[str]) -> None:
		self.focus = FocusColorConfig(self, self.value + self.KEY_SUFFIX_FOCUS, color)
		focus_map[self.value] = self.focus.value

	def set_value(self, config_id: typing.Optional[ConfigId], value: str) -> None:
		self.color = Color(value, attr_name=self.value)
		if self.register_color:
			self.register_color(self.color)
		self.update_focus(config_id)

	def update_focus(self, config_id: typing.Optional[ConfigId]) -> None:
		if self.focus.is_auto_generated:
			self.focus.set_value(config_id, self.color.standout())

	def get_value(self, config_id: typing.Optional[ConfigId]) -> str:
		return self.color.str_repr

class FocusColorConfig(ColorConfig):

	def __init__(self, parent: ColorConfig, key: str, color: typing.Optional[str]) -> None:
		if color is None:
			self.is_auto_generated = True
			color = parent.color.standout()
		else:
			self.is_auto_generated = False
		super().__init__(key, color)

	def init_focus(self, color: typing.Optional[str]) -> None:
		pass

	def update_focus(self, config_id: typing.Optional[ConfigId]) -> None:
		pass

	def set_value(self, config_id: typing.Optional[ConfigId], value: str) -> None:
		super().set_value(config_id, value)
		self.is_auto_generated = False

	def wants_to_be_exported(self) -> bool:
		return not self.is_auto_generated


if __name__ == '__main__':
	import urwid

	def input_handler(key: str) -> typing.Optional[str]:
		if key == 'q' or key == 'enter':
			raise urwid.ExitMainLoop()

		return key

	exp_text_1 = '  hello '
	exp_text_2 = 'world  '
	pattern = '<color={fg}/{bg}>%s</color><color={fg_bright}/{bg}>%s</color>' % (exp_text_1, exp_text_2)
	width = len(exp_text_1 + exp_text_2)

	fg_colors = [col for col in Color.foreground_colors if not col.startswith('bright') and col != 'default']
	fg_colors_bright = [col for col in Color.foreground_colors if col.startswith('bright')]
	bg_colors = [col for col in Color.background_colors if not col.startswith('bright') and col != 'default']
	bg_colors_bright = [col for col in Color.background_colors if col.startswith('bright')]

	palette = []
	ColorStr.set_register_color(lambda col: palette.append(col.to_palette_tuple()))

	widgets = [urwid.Text([''.ljust(width+1)] + [bg.center(width) for bg in bg_colors])] \
		+ [urwid.Text([''.ljust(width+1)] + [bg.center(width) for bg in bg_colors_bright])] \
		+ [urwid.Text(['─' * (width+1)] + ['─' * width for bg in bg_colors_bright])] \
		+ [
			urwid.Text(['%s│' % fg.ljust(width), *[ColorStr.to_markup(pattern.format(fg=fg, fg_bright=fg_light, bg=bg)) for bg in bg_cols]])
			for bg_cols in (bg_colors, bg_colors_bright)
			for fg, fg_light in zip(fg_colors, fg_colors_bright)]

	listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
	urwid.MainLoop(listbox, palette=palette, unhandled_input=input_handler, handle_mouse=False).run()
