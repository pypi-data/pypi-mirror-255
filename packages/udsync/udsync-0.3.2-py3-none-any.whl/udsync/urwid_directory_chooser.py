#!./runmodule.sh

import os
import enum
import abc
import typing

import urwid
from confattr import Config, UiNotifier

from . import urwid_dialog
from . import urwid_multi_key_support
from .lsblk import lsblk, mounter, Device, SubprocessException
from .urwid_colors import ColorConfig

HelpItem = urwid_multi_key_support.HelpItem

URWID_TYPE_SIZE = typing.Union[typing.Tuple[int], typing.Tuple[int, int]]
URWID_TYPE_KEY = str

CURSOR_MAX_UP = urwid_multi_key_support.CURSOR_MAX_UP
CURSOR_MAX_DOWN = urwid_multi_key_support.CURSOR_MAX_DOWN
NEXT_SELECTABLE = urwid_dialog.NEXT_SELECTABLE
PREV_SELECTABLE = urwid_dialog.PREV_SELECTABLE
MOUNT = 'mount'
UNMOUNT = 'umount'
DELETE_BEFORE_CURSOR = 'delete before cursor'
DELETE_AFTER_CURSOR = 'delete after cursor'
DELETE_ALL = 'delete all'
RELOAD = 'reload'


urwid.command_map['g'] = urwid_multi_key_support.SubCommandMap()
urwid.command_map['g']['g'] = CURSOR_MAX_UP
urwid.command_map['G'] = CURSOR_MAX_DOWN


T = typing.TypeVar('T')


View = urwid_dialog.View

class App(urwid_multi_key_support.OverlayPressedKeysOpener):

	@abc.abstractmethod
	def password_screen(self) -> typing.ContextManager[None]:
		raise NotImplementedError()

	@abc.abstractmethod
	def open_view(self, view: View) -> None:
		raise NotImplementedError()

	@abc.abstractmethod
	def show_help_bar(self, help_bar: urwid_multi_key_support.HelpBar) -> None:
		raise NotImplementedError()

	@abc.abstractmethod
	def save_view(self) -> View:
		raise NotImplementedError()


class ExtendedEdit(urwid.WidgetWrap):

	_command_map = urwid.command_map.copy()
	_command_map['ctrl u'] = DELETE_BEFORE_CURSOR
	_command_map['ctrl k'] = DELETE_AFTER_CURSOR
	_command_map['ctrl d'] = DELETE_ALL
	_command_map.implemented_commands = {
		urwid.CURSOR_LEFT,
		urwid.CURSOR_RIGHT,
		urwid.CURSOR_MAX_LEFT,
		urwid.CURSOR_MAX_RIGHT,
		DELETE_BEFORE_CURSOR,
		DELETE_AFTER_CURSOR,
		DELETE_ALL,
	}

	color_normal = ColorConfig('edit.color.normal', 'default', focus='default')
	color_normal_focus = color_normal.focus
	color_invalid = ColorConfig('edit.color.invalid', 'default/red', focus='default/red')
	color_invalid_focus = color_invalid.focus

	def __init__(self, caption: str = '', edit_text: str = '', **kw: typing.Any) -> None:
		self.caption = urwid.Text(caption)
		self.edit = urwid.Edit('', edit_text, **kw)
		self.edit_attr_map = urwid.AttrMap(self.edit, self.color_normal, self.color_normal_focus)
		widget = urwid.Columns(((urwid.PACK, self.caption), self.edit_attr_map))
		super().__init__(widget)

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not super().keypress(size, key):
			return None

		cmd = self._command_map[key]
		if cmd == DELETE_BEFORE_CURSOR:
			self.set_edit_text(self.edit_text[self.edit_pos:])
			self.set_edit_pos(0)
		elif cmd == DELETE_AFTER_CURSOR:
			self.set_edit_text(self.edit_text[:self.edit_pos])
			self.set_edit_pos(len(self.edit_text))
		elif cmd == DELETE_ALL:
			self.set_edit_text('')
			self.set_edit_pos(0)
		else:
			return key

		assert cmd in self._command_map.implemented_commands
		return None

	def invalid(self) -> None:
		self.edit_attr_map.set_attr_map({None:self.color_invalid})
		self.edit_attr_map.set_focus_map({None:self.color_invalid_focus})

	def valid(self) -> None:
		self.edit_attr_map.set_attr_map({None:self.color_normal})
		self.edit_attr_map.set_focus_map({None:self.color_normal_focus})

	def __getattr__(self, name: str) -> typing.Any:
		return getattr(self.edit, name)


class PseudoDevice(Device):

	def __init__(self, name: str, path: str) -> None:
		self.label = name
		self.mountpoint = path
		self.uuid = ''
		self.fstype = ''

	def mount(self) -> typing.NoReturn:
		raise SubprocessException('%r is not a device to be mounted' % self.mountpoint)

	def unmount(self) -> typing.NoReturn:
		raise SubprocessException('%r is not a device to be unmounted' % self.mountpoint)

class DirectoryChooser(urwid.WidgetWrap, urwid_multi_key_support.MultiKeySupport, View):

	BTN_SELECT = 'select'
	BTN_CANCEL = 'cancel'

	use_pile = Config('directory-chooser.leave-widget-group-with-arrow-keys', True, help={
		True: 'If you are on the bottom most entry in the list and trigger `cursor down` the focus switches to the buttons.',
		False: 'You need `next selectable`/`prev selectable` to move the focus between listbox and buttons.'})

	DEV_ROOT = PseudoDevice('root', '/')
	DEV_HOME = PseudoDevice('home', os.path.expanduser('~'))
	DEV_CWD = PseudoDevice('cwd', os.getcwd())

	help_bar_content = Config('directory-chooser.help-bar', [
		HelpItem(urwid_dialog.NEXT_SELECTABLE, 'select buttons'),
		HelpItem([urwid.ACTIVATE, urwid.CURSOR_RIGHT], 'open'),
		HelpItem(urwid.CURSOR_LEFT, 'back'),
		HelpItem(RELOAD, 'reload'),
	])
	help_bar_content_menu = Config('directory-chooser.help-bar.devices-list', [
		HelpItem(urwid_dialog.NEXT_SELECTABLE, 'select buttons'),
		HelpItem(MOUNT, 'mount'),
		HelpItem(UNMOUNT, 'unmount'),
		HelpItem([urwid.ACTIVATE, urwid.CURSOR_RIGHT], 'open'),
		HelpItem(RELOAD, 'reload'),
	])

	# ------- init -------

	def __init__(self,
		app: App,
		select: typing.Callable[[str], None],
		cancel: typing.Callable[[], None],
		start_path: str = '',
		show_hidden: bool = False,
		key_handler: typing.Optional[typing.Callable[[urwid_multi_key_support.SubCommandMap, URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]] = None,
	) -> None:
		self.app = app
		self.ui_notifier = app.get_ui_notifier()
		self.show_hidden = show_hidden
		self.name_of_last_focused_directory: typing.Dict[str, str] = {}
		self.cancel = cancel
		self.key_handler = key_handler

		self.text_path = ExtendedEdit('')
		self.listwalker = urwid.SimpleListWalker([])
		self.listbox = urwid.ListBox(self.listwalker)
		self.init_path(start_path)

		self.listbox.keypress = self.keypress_listbox
		self.text_path.keypress = self.keypress_path  # type: ignore [method-assign]  # This is a bug in mypy https://github.com/python/mypy/issues/2427

		self.help_bar = urwid_multi_key_support.HelpBar(self.help_bar_content, MenuWidget._command_map, self.ui_notifier, edit_context=False)
		self.help_bar_menu = urwid_multi_key_support.HelpBar(self.help_bar_content_menu, MenuWidget._command_map, self.ui_notifier, edit_context=False)

		btn_select = urwid_dialog.ColorButton(self.BTN_SELECT, lambda btn: select(self.text_path.text))
		btn_cancel = urwid_dialog.ColorButton(self.BTN_CANCEL, lambda btn: cancel())

		self.buttons_frame = urwid_dialog.ButtonsFrame(btn_select, btn_cancel)
		self.button_columns = self.buttons_frame.button_columns
		if self.use_pile:
			self.pile = urwid_dialog.TabAwarePile([
				(urwid.PACK, self.text_path),
				self.listbox,
				(urwid.PACK, self.buttons_frame),
			])
			self.pile.focus_position = 1
			widget = self.pile
		else:
			self.frame = urwid.Frame(self.listbox,
				header = self.text_path,
				footer = self.align_buttons(btn_select, btn_cancel),
			)
			widget = self.frame
		super().__init__(widget)
		self.init_multi_key_support(app)
		self.was_device_focused = self.is_device_focused()

	def init_path(self, start_path: str) -> None:
		self.path_selected_in_menu = ''
		self.path_selected_in_menu_len = 0
		self.mountpoint_for_path_selected_in_menu = ''
		if start_path:
			try:
				dev = mounter.mount_path_if_necessary(start_path, self.app.password_screen())
			except SubprocessException as e:
				self.ui_notifier.show_error(e)
				self.set_path('')
				return

			if not dev:
				start_path = os.path.expanduser(start_path)
				start_path = os.path.abspath(start_path)
				dev = self.get_closest_pseudo_device(start_path)
			self.path_selected_in_menu = dev.get_uuid_based_path()
			self.path_selected_in_menu_len = len(self.path_selected_in_menu)
			self.mountpoint_for_path_selected_in_menu = dev.mountpoint
			self.name_of_last_focused_directory[''] = dev.get_name()
		self.set_path(start_path)

	def get_closest_pseudo_device(self, path: str) -> PseudoDevice:
		len_mountpoint = 0
		out: PseudoDevice
		for dev in (self.DEV_ROOT, self.DEV_HOME, self.DEV_CWD):
			if path.startswith(dev.mountpoint):
				n = len(dev.mountpoint)
				if n > len_mountpoint:
					out = dev
		return out

	# ------- update -------

	def go(self, path: str, directory: str) -> None:
		self.name_of_last_focused_directory[path] = self.listbox.focus.name
		last_directory: typing.Optional[str]
		if directory == os.path.pardir:
			if path == self.path_selected_in_menu:
				path = ''
				last_directory = self.name_of_last_focused_directory.get(path, None)
			else:
				path, last_directory = os.path.split(path)
		else:
			path = os.path.join(path, directory)
			last_directory = self.name_of_last_focused_directory.get(path, None)
		self.set_path_and_focus(path, last_directory)

	def go_from_menu(self, path: str, mountpoint: str, name: str) -> None:
		self.path_selected_in_menu = path
		self.path_selected_in_menu_len = len(path)
		self.mountpoint_for_path_selected_in_menu = mountpoint
		self.name_of_last_focused_directory[''] = name
		self.set_path(path)

	def update_menu(self, focused_device: typing.Optional[Device] = None) -> None:
		self.name_of_last_focused_directory[''] = focused_device.get_name() if focused_device else self.listbox.focus.name
		self.set_path('')

	def set_path(self, path: str) -> None:
		last_directory = self.name_of_last_focused_directory.get(path, None)
		self.set_path_and_focus(path, last_directory)

	def set_path_and_focus(self, path: str, last_directory: typing.Optional[str]) -> None:
		self.text_path.set_edit_text(path)
		self.text_path.set_edit_pos(len(path))
		self.listwalker.contents.clear()
		self.listwalker.contents.extend(self.get_content_widgets(path))
		self._last_path = path

		if last_directory:
			for i, dir_widget in enumerate(self.listwalker.contents):
				if hasattr(dir_widget, 'name') and dir_widget.name == last_directory:
					self.listbox.set_focus(i)
					return

		try:
			self.listbox.focus_position = 1
		except IndexError:
			pass

	def get_content_widgets(self, path: str) -> typing.Sequence[urwid.Widget]:
		if not path:
			return list(self.iter_menu_widgets(path))

		# I need to check that because user can enter any path in the Edit widget
		uuid_based_path = path
		if path.startswith(self.path_selected_in_menu):
			path = self.mountpoint_for_path_selected_in_menu + path[self.path_selected_in_menu_len:]

		if os.path.isdir(path):
			try:
				directory_names = [fn for fn in os.listdir(path) if os.path.isdir(os.path.join(path, fn))]
			except PermissionError as e:
				return [ErrorWidget(self, uuid_based_path, e)]
			if not self.show_hidden:
				directory_names = [dn for dn in directory_names if not self.is_hidden(dn)]
			directory_names.sort()
		else:
			directory_names = []
			self.ui_notifier.show_error('Directory does not exist: %r' % path)
		directory_names.insert(0, os.path.pardir)
		return [DirectoryWidget(self, uuid_based_path, dn) for dn in directory_names]

	def iter_menu_widgets(self, path: str) -> typing.Iterator[urwid.Widget]:
		dev: Device
		for dev in (self.DEV_ROOT, self.DEV_HOME, self.DEV_CWD):
			yield MenuWidget(self, dev)

		try:
			devices = list(lsblk.iter_interesting_devices())
		except SubprocessException as e:
			self.ui_notifier.show_error(e)
			devices = []
		mounted_devices = [dev for dev in devices if dev.is_mounted()]
		unmounted_devices = [dev for dev in devices if not dev.is_mounted()]

		if mounted_devices:
			yield SectionHeaderWidget('mounted devices')
			for dev in mounted_devices:
				yield MenuWidget(self, dev)

		if unmounted_devices:
			yield SectionHeaderWidget('unmounted devices')
			for dev in unmounted_devices:
				yield MenuWidget(self, dev)

	def is_hidden(self, path: str) -> bool:
		return path.startswith('.')

	# ------- update help bar -------

	def is_device_focused(self) -> bool:
		w = self._w
		while hasattr(w, 'focus'):
			if isinstance(w, MenuWidget):
				return not isinstance(w.device, PseudoDevice)
			w = w.base_widget.focus

		return False

	def update_help_bar(self, is_device_focused: bool) -> None:
		if is_device_focused:
			self.app.show_help_bar(self.help_bar_menu)
		else:
			self.app.show_help_bar(self.help_bar)
		self.was_device_focused = is_device_focused

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		out = super().keypress(size, key)
		if not out and self.is_device_focused() != self.was_device_focused:
			self.update_help_bar(not self.was_device_focused)
		return typing.cast(typing.Optional[URWID_TYPE_KEY], out)

	# ------- events -------

	def keypress_listbox(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None
		if not urwid.ListBox.keypress(self.listbox, size, key):
			return None

		cmd = self._command_map[key]
		if cmd == CURSOR_MAX_UP:
			self.listbox.set_focus(0)
		elif cmd == CURSOR_MAX_DOWN:
			self.listbox.set_focus(len(self.listbox.body)-1)
		elif self.key_handler and not self.key_handler(self._command_map, size, key):
			pass
		else:
			self.reset_command_map()
			return key

		self.reset_command_map()
		return None

	def keypress_path(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not ExtendedEdit.keypress(self.text_path, size, key):
			path = self.text_path.text
			if path != self._last_path:
				if not path or os.path.isdir(path):
					self.set_path(path)
			return None

		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE:
			self.focus_btn_select()
		elif self.key_handler and not self.key_handler(self._command_map, size, key):
			pass
		else:
			return key
		return None

	# ------- focus -------

	def focus_btn_select(self) -> None:
		self.button_columns.focus_position = 0
		self.focus_buttons()

	def focus_buttons(self) -> None:
		if self.use_pile:
			self.pile.focus_position = 2
		else:
			self.frame.focus_position = 'footer'

	# ------- View methods -------

	def get_box_widget(self) -> urwid.Widget:
		return self

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		if self.is_device_focused():
			return self.help_bar_menu
		return self.help_bar


class ErrorWidget(urwid.WidgetWrap):

	color = ColorConfig('directory-chooser.color.error', 'red', 'red')
	color_focus = color.focus

	def __init__(self, directory_chooser: DirectoryChooser, path: str, e: Exception) -> None:
		msg = str(e)
		self.directory_chooser = directory_chooser
		self.path = path
		self.name = ''
		widget = urwid.Text(msg)
		widget = urwid.AttrMap(widget, self.color, self.color_focus)
		super().__init__(widget)

	def selectable(self) -> bool:
		return True

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE or cmd == urwid.CURSOR_LEFT:
			self.directory_chooser.go(self.path, os.path.pardir)
		else:
			return key
		return None

class DirectoryWidget(urwid.WidgetWrap):

	color_directory = ColorConfig('directory-chooser.color.directory', 'yellow')
	color_directory_focus = color_directory.focus

	def __init__(self, directory_chooser: DirectoryChooser, path: str, name: str) -> None:
		self.directory_chooser = directory_chooser
		self.path = path
		self.name = name
		widget = urwid.Text(name)
		widget = urwid.AttrMap(widget, self.color_directory, self.color_directory_focus)
		super().__init__(widget)

	def selectable(self) -> bool:
		return True

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE or cmd == urwid.CURSOR_RIGHT:
			self.directory_chooser.go(self.path, self.name)
		elif cmd == urwid.CURSOR_LEFT:
			self.directory_chooser.go(self.path, os.path.pardir)
		else:
			return key
		return None

class MenuWidget(urwid.WidgetWrap):

	_command_map = urwid.command_map.copy()
	_command_map['m'] = MOUNT
	_command_map['u'] = UNMOUNT
	_command_map['f5'] = RELOAD
	_command_map.implemented_commands = {
		MOUNT,
		UNMOUNT,
		RELOAD,
		urwid.ACTIVATE,
		urwid.CURSOR_RIGHT,
	}

	color_directory = DirectoryWidget.color_directory
	color_directory_focus = color_directory.focus
	type(lsblk).device_paths_to_be_ignored.key = 'directory-chooser.' + type(lsblk).device_paths_to_be_ignored.key
	type(lsblk).file_system_types_to_be_ignored.key = 'directory-chooser.' + type(lsblk).file_system_types_to_be_ignored.key

	def __init__(self, directory_chooser: DirectoryChooser, device: Device) -> None:
		self.directory_chooser = directory_chooser
		self.app = directory_chooser.app
		self.name = device.get_name()
		self.device = device
		widget = urwid.Text(self.name)
		widget = urwid.AttrMap(widget, self.color_directory, self.color_directory_focus)
		super().__init__(widget)

	def selectable(self) -> bool:
		return True

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE or cmd == urwid.CURSOR_RIGHT:
			dev = self.unlock_and_mount()
			if dev:
				self.directory_chooser.go_from_menu(dev.get_uuid_based_path(), dev.mountpoint, dev.get_name())
		elif cmd == urwid.CURSOR_LEFT:
			return None
		elif cmd == MOUNT:
			dev = self.unlock_and_mount()
			self.directory_chooser.update_menu(dev)
		elif cmd == UNMOUNT:
			dev = self.unmount_and_lock()
			self.directory_chooser.update_menu(dev)
		elif cmd == RELOAD:
			self.directory_chooser.update_menu()
		else:
			assert cmd not in self._command_map.implemented_commands
			return key

		assert cmd in self._command_map.implemented_commands
		return None

	def unlock_and_mount(self) -> typing.Optional[Device]:
		if self.device.is_encrypted():
			try:
				with self.app.password_screen():
					dev = self.device.unlock()
			except SubprocessException as exc:
				self.ui_notifier.show_error(exc)
				return None
		else:
			dev = self.device

		if not dev.is_mounted():
			dev.mount()

		return dev

	def unmount_and_lock(self) -> Device:
		try:
			if self.device.is_mounted():
				self.device.unmount()

			backing_device = self.device.get_crypto_backing_device()
			if backing_device:
				backing_device.lock()
				return backing_device

		except SubprocessException as e:
			self.ui_notifier.show_error(e)

		return self.device


class SectionHeaderWidget(urwid.Text):

	def __init__(self, text: str) -> None:
		text = '\n' + text
		super().__init__(text)


class PathEdit(urwid.WidgetWrap):

	help_bar_content = Config('path-edit.help-bar', [
		urwid_multi_key_support.HelpItem(urwid.ACTIVATE, 'browse'),
		urwid_multi_key_support.HelpItem(urwid_dialog.NEXT_SELECTABLE, 'focus next'),
		urwid_multi_key_support.HelpItem(urwid_dialog.PREV_SELECTABLE, 'focus previous'),
	])

	def __init__(self,
		app: App,
		label: str,
		start_path: str,
		key_handler: typing.Optional[typing.Callable[[urwid_multi_key_support.SubCommandMap, URWID_TYPE_SIZE, URWID_TYPE_KEY], typing.Optional[URWID_TYPE_KEY]]] = None,
	) -> None:
		self.app = app
		self.edit = ExtendedEdit(label, start_path)
		self.has_opened_directory_chooser = False
		self.key_handler = key_handler
		super().__init__(self.edit)

	def on_browse(self) -> None:
		self.has_opened_directory_chooser = True
		self.last_view = self.app.save_view()
		self.app.open_view(DirectoryChooser(self.app, self.on_select, self.on_cancel, start_path=self.get_path(), key_handler=self.key_handler))

	def on_select(self, path: str) -> None:
		self.has_opened_directory_chooser = False
		self.edit.set_edit_text(path)
		self.edit.set_edit_pos(len(path))
		self.app.open_view(self.last_view)

	def on_cancel(self) -> None:
		self.has_opened_directory_chooser = False
		self.app.open_view(self.last_view)


	def get_invalid_path(self) -> 'list[tuple[str, bool]]':
		'''
		:return: list of one or zero (expanded path, can be created) tuples, empty list means the path is an existing directory
		'''
		path = self.get_path()
		password_entry_context = self.app.password_screen()
		try:
			path = mounter.expand_path(path, password_entry_context)
		except SubprocessException:
			self.edit.invalid()
			return [(path, False)]

		if not os.path.isdir(path):
			self.edit.invalid()
			return [(path, True)]

		self.edit.valid()
		return []

	def get_path(self) -> str:
		return typing.cast(str, self.edit.get_edit_text())


	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if not super().keypress(size, key):
			return None

		cmd = self._command_map[key]
		if cmd == urwid.ACTIVATE:
			self.on_browse()
		else:
			return key

		return None


if __name__ == '__main__':
	import time
	from contextlib import contextmanager

	def on_select(path: str) -> None:
		loop.widget = urwid.Filler(urwid.Text(path))
		loop.draw_screen()
		time.sleep(2)
		raise urwid.ExitMainLoop()
	def on_cancel() -> None:
		raise urwid.ExitMainLoop()

	class OverlayOpener(App):

		def __init__(self) -> None:
			self.ui_notifier = UiNotifier()
			self.ui_notifier.set_ui_callback(print)

		def get_ui_notifier(self) -> UiNotifier:
			return self.ui_notifier

		def open_pressed_keys_overlay(self, keys: typing.Sequence[URWID_TYPE_KEY], command_map: urwid_multi_key_support.SubCommandMap) -> None:
			self._prev_widget = loop.widget
			loop.widget = urwid_multi_key_support.OverlayPressedKeys(self._prev_widget, keys, command_map)
		def close_pressed_keys_overlay(self) -> None:
			loop.widget = self._prev_widget

		@contextmanager
		def password_screen(self) -> typing.Iterator[None]:
			loop.screen.stop()
			try:
				yield
			finally:
				loop.screen.start()

		def save_view(self) -> View:
			raise NotImplementedError()
		def open_view(self, view: View) -> None:
			raise NotImplementedError()
		def show_help_bar(self, help_bar: urwid_multi_key_support.HelpBar) -> None:
			pass

	loop = urwid.MainLoop(DirectoryChooser(OverlayOpener(), on_select, on_cancel))
	ColorConfig.set_register_color(lambda c: typing.cast(None, loop.screen.register_palette_entry(*c.to_palette_tuple())))
	loop.run()
