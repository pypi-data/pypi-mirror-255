#!./runmodule.sh

import abc
import typing
import urwid

from confattr import Config

from . import urwid_multi_key_support
from .urwid_colors import ColorConfig

URWID_TYPE_SIZE = typing.Union[typing.Tuple[int], typing.Tuple[int, int]]
URWID_TYPE_KEY = str
URWID_TYPE_COMMAND_MAP = typing.Mapping[URWID_TYPE_KEY, str]

NEXT_SELECTABLE = 'next selectable'
PREV_SELECTABLE = 'prev selectable'
CANCEL = 'cancel'

T = typing.TypeVar('T')


UNIT_HALF_WIDTH_CHAR = ''


urwid.command_map['esc'] = CANCEL


class View:

	@abc.abstractmethod
	def get_box_widget(self) -> urwid.Widget:
		raise NotImplementedError()

	@abc.abstractmethod
	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		raise NotImplementedError()



class ColorButton(urwid.WidgetWrap):

	signals = urwid.Button.signals

	color_button = ColorConfig('button.color', 'default')
	color_button_focus = color_button.focus

	def __init__(self, label: str, on_press: typing.Optional[typing.Callable[['ColorButton'], None]] = None, user_data: typing.Any = None):
		if on_press is None:
			on_press = lambda btn: None
		self._btn = urwid.Button(label, on_press, user_data)
		widget = urwid.AttrMap(self._btn, self.color_button, self.color_button_focus)
		super().__init__(widget)
		setattr(self, urwid.Signals._signal_attr, getattr(self._btn, urwid.Signals._signal_attr))

	@property
	def base_widget(self) -> urwid.Widget:
		return self._w.base_widget

	# ------- urwid.Button methods -------

	def set_label(self, label: str) -> None:
		self._btn.set_label(label)

	def get_label(self) -> str:
		return typing.cast(str, self._btn.get_label())

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		return typing.cast(typing.Optional[URWID_TYPE_KEY], self._btn.keypress(size, key))


	# ------- custom methods -------

	def calc_required_width(self) -> int:
		out = 4  # button_left + button_right + 2*divdechars
		# I am not measuring button_left and button_right because urwid does not do that either
		# https://github.com/urwid/urwid/blob/master/urwid/wimp.py#L478

		text = self.get_label()
		out += urwid.calc_width(text, 0, len(text))

		return out

class TabAwareEnumeratedContainer:

	'''
	Mixin class for urwid container widgets like Columns and Pile
	'''

	# the urwid container widget is expected to have the following attributes:
	focus_position: int
	contents: typing.List[typing.Tuple[urwid.Widget, typing.Any]]
	_command_map: URWID_TYPE_COMMAND_MAP


	def __init__(self, *l: typing.Any, **kw: typing.Any) -> None:
		self.cycle_focus = kw.pop('cycle_focus', True)
		super().__init__(*l, **kw)

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not super().keypress(size, key):  # type: ignore [misc]  # keypress is defined by other parent class
			return None

		cmd = self._command_map[key]
		if cmd == NEXT_SELECTABLE:
			if not self.focus_next(self.focus_position + 1):
				return key
		elif cmd == PREV_SELECTABLE:
			if not self.focus_prev(self.focus_position - 1):
				return key
		else:
			return key

		return None

	def focus_next(self, i: int) -> bool:
		n = len(self.contents)
		for _j in range(n):
			if i >= n:
				if self.cycle_focus:
					i = 0
				else:
					return False

			if self.contents[i][0].selectable():
				break

			i += 1

		self.focus_position = i

		widget = self.contents[i][0].base_widget
		if hasattr(widget, 'focus_first'):
			widget.focus_first()

		return True

	def focus_prev(self, i: int) -> bool:
		n = len(self.contents)
		for _j in range(n):
			if i < 0:
				if self.cycle_focus:
					i = n - 1
				else:
					return False

			if self.contents[i][0].selectable():
				break

			i -= 1

		self.focus_position = i
		widget = self.contents[i][0].base_widget
		if hasattr(widget, 'focus_last'):
			widget.focus_last()

		return True

	def focus_first(self) -> bool:
		return self.focus_next(0)

	def focus_last(self) -> bool:
		return self.focus_prev(len(self.contents)-1)

class TabAwarePile(TabAwareEnumeratedContainer, urwid.Pile):

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not super().keypress(size, key):
			return None

		cmd = self._command_map[key]
		if cmd == CANCEL:
			for i, (widget, options) in enumerate(self.contents):
				if isinstance(widget, ButtonsFrame):
					widget.focus_cancel_button()
					self.focus_position = i
					break
			else:
				return key
		else:
			return key

		return None

class TabAwareColumns(TabAwareEnumeratedContainer, urwid.Columns):
	pass


class ButtonsFrame(urwid.delegate_to_widget_mixin('_original_widget'), urwid.WidgetDecoration):  # type: ignore [misc]  # silence "Unsupported dynamic base class"

	BUTTON_PADDING = Config('button.padding', 1, unit=UNIT_HALF_WIDTH_CHAR, help='a margin added inside of a button left and right of the text')
	WIDTH_BETWEEN_BUTTONS = Config('button.distance', 0, unit=UNIT_HALF_WIDTH_CHAR, help='the distance between two buttons side by side')

	def __init__(self, *buttons: ColorButton, cycle_focus: bool = False, cancel_button: typing.Optional[int] = -1) -> None:
		btn_width = max(btn.calc_required_width() for btn in buttons)
		btn_width += 2 * self.BUTTON_PADDING
		n = len(buttons)
		total_width = n*btn_width + (n-1)*self.WIDTH_BETWEEN_BUTTONS
		cols = [(btn_width, btn) for btn in buttons]
		out = TabAwareColumns(cols, self.WIDTH_BETWEEN_BUTTONS, cycle_focus=cycle_focus)
		self.button_columns = out
		out = urwid.Padding(out, urwid.CENTER, total_width)

		if cancel_button is not None and cancel_button < 0:
			cancel_button += len(cols)
		self.cancel_button_position = cancel_button
		super().__init__(out)

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not super().keypress(size, key):
			return None

		cmd = self._command_map[key]
		if cmd == CANCEL and self.cancel_button_position:
			cancel_button = self.button_columns.contents[self.cancel_button_position][0]
			urwid.emit_signal(cancel_button, 'click', cancel_button)
		else:
			return key

		return None

	def focus_cancel_button(self) -> None:
		if self.cancel_button_position:
			self.button_columns.focus_position = self.cancel_button_position


class Dialog(urwid.WidgetWrap, urwid_multi_key_support.MultiKeySupport, View):

	MAX_TEXT_WIDTH = 80

	help_bar_content = Config('dialog.help-bar', [
		urwid_multi_key_support.HelpItem('activate', 'click button'),
		urwid_multi_key_support.HelpItem('next selectable', 'focus next'),
		urwid_multi_key_support.HelpItem('prev selectable', 'focus previous'),
	])

	def __init__(self,
		pressed_keys_opener: urwid_multi_key_support.OverlayPressedKeysOpener,
		question: typing.Union[str, urwid.Widget],
		answers: typing.Mapping[str, typing.Callable[[], None]],
		key_handler: typing.Optional[typing.Callable[[urwid_multi_key_support.SubCommandMap, URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]],
		cancel: typing.Optional[typing.Callable[[], None]] = None,
		add_commands: typing.Optional[typing.Mapping[str, typing.Callable[[], None]]] = None,
	) -> None:
		self.pressed_keys_opener = pressed_keys_opener
		if isinstance(question, str):
			self.text = urwid.Text(question.strip() + '\n')
		else:
			self.text = question
		self.key_handler = key_handler
		self.cancel_callback = cancel
		self.add_commands = add_commands

		text_width = self.text.pack((self.MAX_TEXT_WIDTH,))[0]
		buttons = [ColorButton(lbl, self.strip_arg(func)) for lbl, func in answers.items()]
		widget = ButtonsFrame(*buttons, cycle_focus=True)
		widget = urwid.Pile([self.text, widget])
		widget = urwid.Filler(widget)
		widget = urwid.Padding(widget, urwid.CENTER, text_width)
		super().__init__(widget)
		self.init_multi_key_support(pressed_keys_opener)

	def strip_arg(self, func: typing.Callable[[], T]) -> typing.Callable[[typing.Any], T]:
		return lambda x: func()

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None

		if self.cancel_callback is not None and self._command_map[key] == CANCEL:
			self.cancel_callback()
			self.reset_command_map()
			return None

		if super().keypress(size, key) is None:
			self.reset_command_map()
			return None

		if self.add_commands:
			cmd = self._command_map[key]
			if cmd is not None:
				assert isinstance(cmd, str)
				if cmd in self.add_commands:
					self.add_commands[cmd]()
					return None

		if self.key_handler:
			out = self.key_handler(self._command_map, size, key)
			self.reset_command_map()
			return out

		self.reset_command_map()
		return key

	# ------- View methods -------

	def get_box_widget(self) -> urwid.Widget:
		return self

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self._default_command_map, self.pressed_keys_opener.get_ui_notifier(), edit_context=False)

	# ------- debugging -------

	def __repr__(self) -> str:
		if isinstance(self.text, urwid.text):
			return '<%s %s>' % (type(self).__name__, self.text.text)
		return typing.cast(str, super().__repr__())


class YesNoDialog(Dialog):

	BTN_YES = 'yes'
	BTN_NO = 'no'

	def __init__(self,
		pressed_keys_opener: urwid_multi_key_support.OverlayPressedKeysOpener,
		question: str,
		yes: typing.Callable[[], None],
		no: typing.Callable[[], None],
		key_handler: typing.Optional[typing.Callable[[urwid_multi_key_support.SubCommandMap, URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]],
	) -> None:
		super().__init__(pressed_keys_opener, question, {self.BTN_YES: yes, self.BTN_NO: no}, key_handler)
