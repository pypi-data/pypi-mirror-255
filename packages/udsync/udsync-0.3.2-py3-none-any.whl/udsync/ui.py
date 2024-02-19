#!./runmodule.sh

#TODO: expanding nodes reads the HDD which is slow. Why does it not take the info from the model?
#TODO: don't crash on command.run if it is not installed


import os
import sys
import shutil
import subprocess
import re
import time
import datetime
import contextlib
import threading
import pkgutil
import logging
import contextlib
import enum
import typing
from collections.abc import Callable, Sequence

try:
	from ranger.ext import rifle
except ImportError:
	rifle = None

import urwid
import urwid_timed_progress

import confattr
from confattr import Config, DictConfig, MultiConfig, ConfigId, UiNotifier, NotificationLevel, Message
from confattr.types import SubprocessCommand as Command, SubprocessCommandWithAlternatives as CommandWithAlternatives, TYPE_CONTEXT

NotificationLevel_WARNING = NotificationLevel.new('warning', less_important_than=NotificationLevel.ERROR)
NotificationLevel_DEBUG = NotificationLevel.new('debug', less_important_than=NotificationLevel.INFO)

from .about import APP_NAME
from . import urwid_multi_key_support



QUIT = 'quit'
QUIT_ASK = 'quit --ask'
QUIT_ASK_IF_LONG = 'quit --ask-if-long-startup'
CONFIG = 'config'
HELP_LIST_OF_KEY_MAPPINGS = 'help key-mappings'
HELP_LIST_OF_COMMANDS = 'help commands'
HELP_CONFIG = 'help config'
FUNC_SHOW_LAST_SYNC_TIME = 'show last sync time'
FUNC_TOGGLE_STANDBY_AFTER = 'toggle standby after'

urwid.command_map['j'] = urwid.CURSOR_DOWN
urwid.command_map['k'] = urwid.CURSOR_UP
urwid.command_map['h'] = urwid.CURSOR_LEFT
urwid.command_map['l'] = urwid.CURSOR_RIGHT
urwid.command_map['ctrl p'] = CONFIG
urwid.command_map['f1'] = HELP_LIST_OF_KEY_MAPPINGS
urwid.command_map['f2'] = HELP_LIST_OF_KEY_MAPPINGS
urwid.command_map['f3'] = HELP_LIST_OF_COMMANDS
urwid.command_map['f4'] = HELP_CONFIG
urwid.command_map['f6'] = FUNC_SHOW_LAST_SYNC_TIME
urwid.command_map['q'] = QUIT_ASK_IF_LONG


from . import urwid_dialog
from . import urwid_directory_chooser
from . import urwid_colors

from . import model
from . import sync
Synchronizer = sync.Synchronizer
from . import lsblk
from . import clipboard
from . import human_bytes
from . import mime
from .symlink import read_symlink

Path = lsblk.Path

CANCEL = urwid_dialog.CANCEL
CURSOR_MAX_UP = urwid_directory_chooser.CURSOR_MAX_UP
CURSOR_MAX_DOWN = urwid_directory_chooser.CURSOR_MAX_DOWN

urwid.command_map.implemented_commands = {
	urwid.CURSOR_LEFT,
	urwid.CURSOR_RIGHT,
	urwid.CURSOR_MAX_LEFT,
	urwid.CURSOR_MAX_RIGHT,
	urwid.CURSOR_UP,
	urwid.CURSOR_DOWN,
	urwid.CURSOR_PAGE_UP,
	urwid.CURSOR_PAGE_DOWN,
	CURSOR_MAX_UP,
	CURSOR_MAX_DOWN,
	urwid_dialog.NEXT_SELECTABLE,
	urwid_dialog.PREV_SELECTABLE,
	urwid.ACTIVATE,
	CANCEL,
	QUIT,
	QUIT_ASK,
	QUIT_ASK_IF_LONG,
	CONFIG,
	HELP_LIST_OF_KEY_MAPPINGS,
	HELP_LIST_OF_COMMANDS,
	HELP_CONFIG,
	FUNC_SHOW_LAST_SYNC_TIME,
}

URWID_TYPE_SIZE = typing.Union[typing.Tuple[int], typing.Tuple[int, int]]
URWID_TYPE_KEY = str
URWID_TYPE_ATTR = str


FUNC_CURSOR_NEXT_SIBLING = 'cursor next sibling'
FUNC_CURSOR_PREV_SIBLING = 'cursor prev sibling'
FUNC_CURSOR_FIRST_SIBLING = 'cursor first sibling'
FUNC_CURSOR_LAST_SIBLING = 'cursor last sibling'
FUNC_CURSOR_NEXT_PARENT = 'cursor next parent'
FUNC_CURSOR_PARENT = 'cursor parent'
FUNC_NODE_TOGGLE_IGNORE = 'node toggle ignore'
FUNC_NODE_TOGGLE_DIRECTION = 'node toggle direction'
FUNC_NODE_SET_DIRECTION_SRC_TO_DST = 'node direction=src-to-dst'
FUNC_NODE_SET_DIRECTION_DST_TO_SRC = 'node direction=dst-to-src'
FUNC_NODE_UPDATE = 'node update'
FUNC_VIEW_EXPAND = 'node expand'
FUNC_VIEW_EXPAND_OR_DIFF = 'node expand or diff'
FUNC_VIEW_COLLAPSE = 'node collapse'
FUNC_VIEW_COLLAPSE_PARENT = 'node collapse parent'
FUNC_YANK_PATH_SRC = 'yank src'
FUNC_YANK_PATH_DST = 'yank dst'
FUNC_YANK_NAME_SRC = 'yank src name'
FUNC_YANK_NAME_DST = 'yank dst name'
FUNC_YANK_DIR_SRC = 'yank src directory'
FUNC_YANK_DIR_DST = 'yank dst directory'
FUNC_OPEN = 'open'
FUNC_OPEN_ASK = 'open --ask'
FUNC_OPEN_SRC = 'open src'
FUNC_OPEN_DST = 'open dst'
FUNC_OPEN_TEXT = 'open --editor'
FUNC_OPEN_ASK_TEXT = 'open --editor --ask'
FUNC_OPEN_SRC_TEXT = 'open --editor src'
FUNC_OPEN_DST_TEXT = 'open --editor dst'
FUNC_OPEN_XDG = 'open --external'
FUNC_OPEN_ASK_XDG = 'open --external --ask'
FUNC_OPEN_SRC_XDG = 'open --external src'
FUNC_OPEN_DST_XDG = 'open --external dst'
FUNC_DIFF = 'diff'
FUNC_SYNC = 'sync'
FUNC_SYNC_ASK = 'sync --ask'
FUNC_SYNC_TIME_STAMPS = 'sync time stamps'
FUNC_SYNC_TIME_STAMPS_ASK = 'sync time stamps --ask'
FUNC_TOGGLE_SHOW_SAME = 'toggle diff.show-same'
FUNC_SET_SHOW_SAME_TRUE = 'set diff.show-same=true'
FUNC_SET_SHOW_SAME_FALSE = 'set diff.show-same=false'
FUNC_RENAME = 'rename'
FUNC_RENAME_FROM = 'rename from'
FUNC_RENAME_TO = 'rename to'
FUNC_DEBUG_SHELL = 'debug shell'


ERROR_FAILED_TO_MOUNT_DEVICE = 1


@enum.unique
class LOG_LOCATION(enum.Enum):
	SOURCE = 'src'
	DESTINATION = 'dst'
	BOTH = 'both'
	NONE = 'none'


pattern_seconds = Config('time-formatter.pattern.seconds', '{s:.2f}s')
pattern_minutes = Config('time-formatter.pattern.minutes', '{m}:{s:02d}min')
pattern_hours = Config('time-formatter.pattern.hours', '{h}:{m:02d}h')
def time_difference_to_str(seconds: float) -> str:
	s = int(seconds)
	m = s // 60
	if m == 0:
		return pattern_seconds.value.format(s=seconds)
	s %= 60
	h = m // 60
	if h == 0:
		return pattern_minutes.value.format(s=s, m=m)
	m %= 60
	return pattern_hours.value.format(s=s, m=m, h=h)


class Return(Exception):
	def __init__(self, msg: str) -> None:
		self.msg = msg


View = urwid_dialog.View

class LastView(View):

	def __init__(self,
		widget: urwid.Widget,
		help_bar: urwid_multi_key_support.HelpBar,
	) -> None:
		self.widget = widget
		self.help_bar = help_bar

	def get_box_widget(self) -> urwid.Widget:
		return self.widget

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return self.help_bar


class App(urwid_directory_chooser.App):

	resource_help_config = 'doc/config.md'

	DIR_BACKUP_PLANS = 'backup-plans'

	handle_mouse = Config('urwid.handle-mouse', False, help={True: 'urwid intercepts mouse events so you cannot select and copy text as usual', False: 'this behaves like a normal terminal application'})

	default_backup_plan = Config('default-backup-plan', 'default', help='the name of the default backup plan to be loaded if no command line arguments are given')
	path_src = MultiConfig('path.src', Path(''), help='the source path to be used if no path is given on the command line')
	path_dst = MultiConfig('path.dst', Path(''), help='the destination path to be used if no path is given on the command line')

	should_ask_to_create_backup_plan = Config('backup-plan.ask-to-create', True, help='ask if the backup plan should be created if a not existing backup plan is passed as command line argument')
	open_not_existing_backup_plan = Config('backup-plan.edit-not-existing', False, help={True : '--edit-config opens a new file if the backup plan does not exist', False : '--edit-config with a not existing backup plan is an error'})

	log_level = Config('notification-level', NotificationLevel.INFO)
	config_level = Config('notification-level.config-file', NotificationLevel_WARNING)

	color_error = urwid_colors.ColorConfig('status.color.error', 'red')
	color_warning = urwid_colors.ColorConfig('status.color.warning', 'yellow')
	color_info = urwid_colors.ColorConfig('status.color.info', 'default')
	color_debug = urwid_colors.ColorConfig('status.color.debug', 'bright black')

	expected_number_of_files = Config('progress-bar.estimated-number-of-files', 500000, unit='', help='a rough guess how many files need to be processed, used for the progress bar before finish counting the real number')
	time_long_startup = Config('time-long-startup', 5.0, unit='seconds', help='if scanning the directories for changes has taken longer than this number of seconds it is considered long and `quit --ask-if-long-startup` will ask before quitting')

	WC_PATH = '{path}'
	cmd_file_browser = Config('cmd.filebrowser', CommandWithAlternatives([
		['ranger', WC_PATH],
		['xdg-open', WC_PATH],
		['vim', WC_PATH],
	]), help='the command used to open a directory')
	RIFLE = 'rifle'
	cmd_open = Config('cmd.open', CommandWithAlternatives([
		[RIFLE, WC_PATH],
		['xdg-open', WC_PATH],
	]), help = 'the commmand used to open non-text files, i.e. if the file mime type does not match %mime-type-text-re% or if --external is used. "rifle" is a special value, it is not executed as subprocess but the python binding is used which has the advantage that also programs with a text UI can be used.')
	cmd_default_editor = Config('cmd.editor', CommandWithAlternatives([
		['vim', WC_PATH],
		['vi', WC_PATH],
		['nano', WC_PATH]
	]), help='used if the environment variable EDITOR is not set')
	re_mime_text = Config('mime-type-text-re', r'text', help='when opening a file (without --external or --editor) it\'s mime type is matched against this regular expression. If it matches then the file is opened with EDITOR. Otherwise with %cmd.open%.')
	cmd_standby = Config('cmd.standby', CommandWithAlternatives([['systemctl', 'suspend']]))

	show_unhandled_keys = Config('show-unhandled-keys', True, help='show an error message if a key is pressed but nothing happens. This does not necessarily mean that the key is unmapped. For example `cursor down` does nothing if the cursor is already at the very bottom.')

	sync_log_name = 'sync'
	sync_log_file_name = Config('sync.log.name', '.udsync-logs' + os.path.sep + '%Y-%m-%d_%H-%M-%S_udsync.log', help='this file name is formatted with strftime, see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes')
	sync_log_location = Config('sync.log.location', LOG_LOCATION.BOTH)
	sync_log_level = logging.DEBUG
	sync_time_stamps_log_name = 'sync-time-stamps'
	sync_time_stamps_log_file_name = Config('sync.log-sync-time-stamps.name', '.udsync-logs' + os.path.sep + '%Y-%m-%d_%H-%M-%S_udsync_time_stamps.log', help='this file name is formatted with strftime, see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes')
	rename_log_name = 'rename'
	rename_log_file_name = Config('sync.log-rename.name', '.udsync-logs' + os.path.sep + '%Y-%m-%d_%H-%M-%S_udsync_rename.log', help='this file name is formatted with strftime, see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes')

	notify_log_files = Config('print-log-files-at-end', True, help='print the paths of the created log files when closing the program')

	# ------- app.init -------

	def __init__(self) -> None:
		self.lines_to_print_after_end: typing.List[str] = []
		self.ui_notifier = UiNotifier(notification_level=type(self).log_level)
		self._body_widget = None
		lsblk.udisksctl.set_logger(self.ui_notifier)
		self.frameview = urwid.Frame(None)
		self.synchronizer: typing.Optional[sync.Synchronizer] = None
		self.time_stamp_synchronizer: typing.Optional[sync.TimeStampSynchronizer] = None
		self._last_view: typing.Optional[LastView] = None
		self.standby_after = False
		if rifle:
			Command.register_python_callback(self.RIFLE, self.run_rifle)

		self.command_maps = {
			'diff' : DiffWidget._command_map,
			'progress-bar' : ProgressView._command_map,
			'edit' : urwid_directory_chooser.ExtendedEdit._command_map,
			'directory-browser.menu' : urwid_directory_chooser.MenuWidget._command_map,
			'general' : urwid.command_map,
		}
		self.config_file = urwid_multi_key_support.UrwidConfigFile(appname=APP_NAME, command_maps=self.command_maps, reference_command_map=urwid.command_map, notification_level=type(self).config_level)

	def print_help_config(self) -> None:
		print(self.config_file.get_help())

	def set_ui_callback(self, callback: 'Callable[[Message], None]') -> None:
		self.config_file.set_ui_callback(callback)
		self.ui_notifier.set_ui_callback(callback)

	def get_ui_notifier(self) -> UiNotifier:
		return self.ui_notifier


	def load(self, path_src: typing.Optional[str], path_dst: typing.Optional[str]) -> None:
		self.load_config()
		self.screen = self.create_screen()
		self.loop = urwid.MainLoop(self.frameview, screen=self.screen, input_filter=self.input_filter, unhandled_input=self.unhandled_input, handle_mouse=self.handle_mouse)
		urwid_colors.ColorStr.set_logger(self.ui_notifier)
		urwid_colors.ColorStr.set_register_color(self.register_color)
		urwid_colors.ColorConfig.set_register_color(self.register_color)
		self.set_ui_callback(self.show)

		if path_dst is None:
			if path_src is None:
				backup_plan = self.default_backup_plan
			else:
				backup_plan = path_src
				path_src = None
			if not self.load_backup_plan(backup_plan):
				return
		else:
			assert path_src
			self.config_id = MultiConfig.default_config_id
			self.path_src = Path(path_src)
			self.path_dst = Path(path_dst)
			del self.config_id
		self.init_model()

	def init_model(self) -> None:
		cls = type(self)
		paths = []
		for config_id in cls.path_src.config_ids:
			self.config_id = config_id
			try:
				path_src = self.path_src
				src_defined = bool(path_src.raw)
			except KeyError:
				src_defined = False
			try:
				path_dst = self.path_dst
				dst_defined = bool(path_dst.raw)
			except KeyError:
				dst_defined = False
			del self.config_id

			if not src_defined and not dst_defined:
				if config_id == MultiConfig.default_config_id:
					continue
				self.show_error('{key_src} and {key_dst} undefined for {config_id}'.format(key_src=cls.path_src.key, key_dst=cls.path_dst.key, config_id=config_id))
				continue
			elif not src_defined:
				self.show_error('{key_src} undefined for {config_id}'.format(key_src=cls.path_src.key, config_id=config_id))
				continue
			elif not dst_defined:
				self.show_error('{key_dst} undefined for {config_id}'.format(key_dst=cls.path_dst.key, config_id=config_id))
				continue

			try:
				expanded_path_src = lsblk.mounter.expand_path(path_src, self.password_screen())
			except lsblk.SubprocessException as e:
				self.unrecoverable_error(ERROR_FAILED_TO_MOUNT_DEVICE, 'failed to mount {key} {path!r}\n{err}'.format(key=cls.path_src.key, path=path_src.raw, err=str(e)))

			try:
				expanded_path_dst = lsblk.mounter.expand_path(path_dst, self.password_screen())
			except lsblk.SubprocessException as e:
				self.unrecoverable_error(ERROR_FAILED_TO_MOUNT_DEVICE, 'failed to mount {key} {path!r}\n{err}'.format(key=cls.path_dst.key, path=path_dst.raw, err=str(e)))

			paths.append((config_id, expanded_path_src, expanded_path_dst))

		self.meta_node = model.MetaNode()
		self.paths: typing.Sequence[typing.Tuple[ConfigId, str, str]] = paths
		LongTask(self, 'Scanning directories',
			lambda: self.meta_node.load(paths), self.after_load,
			lambda: model.ComparisonNode.number_nodes, self.get_load_goal,
			daemon = True,
			show_in_load_screen = '{compare_mode.key} = {compare_mode.value.value}'.format(compare_mode=model.ComparisonNode.compare_mode),
			more_tasks_pending = False,
		).start()
		self.show_last_sync_time(show_errors=False)

	def get_load_goal(self) -> int:
		if not hasattr(self, 'counter_thread'):
			self.number_files = self.expected_number_of_files
			self.counter_thread = threading.Thread(target=self._count_number_files_in_other_thread, args=[self.paths], daemon=True)
			self.counter_thread.start()

		return self.number_files

	def _count_number_files_in_other_thread(self, paths: typing.Sequence[typing.Tuple[ConfigId, str, str]]) -> None:
		self.number_files = sum(model.count_files(path_src) for config_id, path_src, path_dst in paths)

	def after_load(self, scan_time_in_s: float) -> None:
		root_directory_node = FileOrDirectoryNode(self.meta_node)
		self.treeview = DiffWidget(self, urwid.TreeWalker(root_directory_node))
		self.open_view(self.treeview)
		self.show_info('scanning the directories has taken %s' % time_difference_to_str(scan_time_in_s))

	def open_view(self, view: View) -> None:
		self.frameview.body = view.get_box_widget()
		if self._body_widget is not None:
			self._body_widget = self.frameview.body
		self.show_help_bar(view.get_help_bar())
		self.is_ask_to_quit_dialog_open = False

	def show_help_bar(self, help_bar: urwid_multi_key_support.HelpBar) -> None:
		self.frameview.header = help_bar

	def save_view(self) -> LastView:
		if self._body_widget is not None:
			main_widget = self._body_widget
		else:
			main_widget = self.frameview.body
		return LastView(main_widget, help_bar=self.frameview.header)


	def load_backup_plan(self, name: str) -> bool:
		if self.is_path(name):
			fn = name
		else:
			path = self.get_backup_plan_directory()
			fn = os.path.join(path, name)
		if not os.path.isfile(fn):
			if self.should_ask_to_create_backup_plan:
				self.ask_to_create_backup_plan(name, fn)
				return False
			else:
				self.error_in_init(f'backup plan {name!r} does not exist')
		self.load_config(fn)
		return True

	def get_backup_plan_directory(self) -> str:
		path = os.path.dirname(self.config_file.get_save_path())
		path = os.path.join(path, self.DIR_BACKUP_PLANS)
		return path

	def list_backup_plans(self) -> typing.Sequence[str]:
		out = os.listdir(self.get_backup_plan_directory())
		out = [fn for fn in out if not fn.startswith('.')]
		out.sort()
		return out

	def edit_backup_plan(self, name: str) -> bool:
		self.reset_has_error_occurred()
		fn = os.path.join(self.get_backup_plan_directory(), name)

		was_existing = True
		if not os.path.isfile(fn):
			if not self.open_not_existing_backup_plan:
				self.show_error('no such backup plan %r' % name)
				return False

			was_existing = False

		self.edit_file(fn)

		if not os.path.isfile(fn):
			self.show_error('backup plan %r not created' % name)
			return False

		if not was_existing:
			self.show_info('created backup plan %r' % name)

		self.load_backup_plan(fn)
		return not self.has_error_occurred()

	def delete_backup_plan(self, name: str) -> bool:
		fn = os.path.join(self.get_backup_plan_directory(), name)
		if not os.path.exists(fn):
			self.show_info('no such backup plan %r' % name)
			return False

		os.remove(fn)
		self.show_info('deleted %s' % fn)
		return True

	def is_path(self, name: str) -> bool:
		return os.path.isabs(name) or name.split(os.path.sep)[0] in (os.path.curdir, os.path.pardir)

	def ask_to_create_backup_plan(self, name: str, fn: str) -> None:
		self.open_view(urwid_dialog.YesNoDialog(self,
			f'Backup plan {name!r} does not exist. Do you want to create it?',
			yes = lambda: self.ask_for_backup_plan_data(name, fn),
			no = self.quit,
			key_handler = self.handle_key,
		))

	def ask_for_backup_plan_data(self, name: str, fn: str) -> None:
		self.open_view(BackupPlanWidget(self, name, fn, create=self.create_backup_plan, cancel=self.quit))

	def create_backup_plan(self, widget: 'BackupPlanWidget') -> None:
		name = widget.get_name()
		fn = widget.get_file_name()
		for paths_group in widget.get_path_groups():
			self.config_id = self.generate_config_id(paths_group)
			self.path_src = Path(paths_group.get_path_src())
			self.path_dst = Path(paths_group.get_path_dst())
			del self.config_id
		self.config_file.save_file(fn, config_instances=[App.path_src, App.path_dst, model.ComparisonNode.state_direction_map, App.sync_log_file_name, App.sync_time_stamps_log_file_name, App.rename_log_file_name, App.sync_log_location], ignore_commands=[urwid_multi_key_support.UrwidConfigFileArgparseCommand])
		self.ask_to_edit_backup_plan(fn)

	def ask_to_edit_backup_plan(self, fn: str) -> None:
		self.open_view(urwid_dialog.YesNoDialog(
			self,
			'I have created {fn}.\nDo you want to edit it (e.g. to change default directions)?'.format(fn=fn),
			yes = lambda: self.edit_backup_plan_and_start(fn),
			no = self.init_model,
			key_handler = self.handle_key,
		))

	def edit_backup_plan_and_start(self, fn: str) -> None:
		self.edit_file(fn)
		MultiConfig.reset()
		self.load_config(fn)
		self.init_model()

	def generate_config_id(self, paths_group: 'PathsGroup') -> ConfigId:
		path_src = paths_group.get_path_src()
		out = ConfigId(os.path.split(path_src)[1])
		if out not in MultiConfig.config_ids:
			return out

		return ConfigId('%s > %s' % (path_src, paths_group.get_path_dst()))


	def create_screen(self) -> urwid.BaseScreen:
		from urwid.raw_display import Screen
		screen = Screen()
		return screen


	def error_in_init(self, msg: str) -> typing.NoReturn:
		self.set_ui_callback(lambda msg: print(msg, file=sys.stderr))
		print(msg, file=sys.stderr)
		sys.exit(1)


	# ------- show -------

	loglevel_attributes = {
		NotificationLevel.ERROR : color_error.value,
		NotificationLevel_WARNING : color_warning.value,
		NotificationLevel.INFO : color_info.value,
		NotificationLevel_DEBUG : color_debug.value,
	}

	def on_error(self, exc: Exception) -> None:
		msg = str(exc)
		self.show_error(msg)

	def show_error(self, msg: typing.Union[BaseException, str]) -> None:
		self._has_error_occurred = True
		self.show(Message(NotificationLevel.ERROR, msg))

	def show_warning(self, msg: str) -> None:
		self.show(Message(NotificationLevel_WARNING, msg))

	def show_info(self, msg: str) -> None:
		self.show(Message(NotificationLevel.INFO, msg))

	def show_debug(self, msg: str) -> None:
		self.show(Message(NotificationLevel_DEBUG, msg))

	def show(self, msg: Message) -> None:
		if not isinstance(self.frameview.footer, urwid.Pile):
			self.frameview.footer = urwid.Pile([])
		attr = self.loglevel_attributes[msg.notification_level]
		widget = urwid.Text((attr, str(msg)))
		self.frameview.footer.contents.append((widget, (urwid.PACK, None)))


	def input_filter(self, keys: typing.List[URWID_TYPE_KEY], raw: typing.List[int]) -> typing.List[URWID_TYPE_KEY]:
		self.frameview.footer = None
		return keys


	def unrecoverable_error(self, exit_code: int, err_message: str) -> typing.NoReturn:
		self.screen.stop()
		print(err_message, file=sys.stderr)
		sys.exit(exit_code)


	def handle_key(self, command_map: urwid_multi_key_support.SubCommandMap, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = command_map[key]
		if cmd == HELP_LIST_OF_KEY_MAPPINGS:
			self.open_help_list_of_key_mappings()
		elif cmd == HELP_LIST_OF_COMMANDS:
			self.open_help_list_of_commands()
		elif cmd == HELP_CONFIG:
			self.open_help_config()
		elif cmd == FUNC_SHOW_LAST_SYNC_TIME:
			self.show_last_sync_time(show_errors=True)

		elif cmd == FUNC_TOGGLE_STANDBY_AFTER:
			self.toggle_standy_after(in_progress=False)

		elif cmd == CONFIG:
			self.open_config()
		elif cmd == QUIT:
			self.quit()
		elif cmd == QUIT_ASK:
			self.ask_to_quit()
		elif cmd == QUIT_ASK_IF_LONG:
			self.ask_to_quit_if_long_startup()
		else:
			return key

		return None

	# show_error is intended for when implicit things fail, e.g. an error in the config file
	# show_big_error is intended for when explicit things fail, e.g. the user wants to sync the time stamps but that is not possible because wrong compare_mode is selected
	show_big_error = show_error


	def has_error_occurred(self) -> bool:
		return self._has_error_occurred

	def reset_has_error_occurred(self) -> None:
		self._has_error_occurred = False


	# ------- print after end -------

	def print_after_end(self, msg: str) -> None:
		self.lines_to_print_after_end.append(msg)


	# ------- pressed keys overlay -------

	def open_pressed_keys_overlay(self, pressed_keys: typing.Sequence[URWID_TYPE_KEY], command_map: urwid_multi_key_support.SubCommandMap) -> None:
		self._body_widget = self.frameview.body
		self.frameview.body = urwid_multi_key_support.OverlayPressedKeys(self.frameview.body, pressed_keys, command_map)

	def close_pressed_keys_overlay(self) -> None:
		self.frameview.body = self._body_widget
		self._body_widget = None


	# ------- actions -------

	def unhandled_input(self, key: URWID_TYPE_KEY) -> bool:
		if self.show_unhandled_keys:
			self.show_error('unhandled key: %s' % urwid_multi_key_support.MultiKeySupport.format_key(key))
			return True
		return False

	def ask_to_quit_if_long_startup(self) -> None:
		now = time.time()
		t0 = getattr(self, 't0', now)
		t1 = getattr(self, 't1', now)
		dt = t1 - t0
		if dt > self.time_long_startup:
			self.ask_to_quit()
		else:
			self.quit()

	def ask_to_quit(self) -> None:
		if self.is_ask_to_quit_dialog_open:
			return

		last_view = self.save_view()
		self.open_view(urwid_dialog.YesNoDialog(
			self,
			'Do you want to close this program?'.format(),
			yes = self.quit,
			no = lambda: self.open_view(last_view),
			key_handler = self.handle_key,
		))
		self.is_ask_to_quit_dialog_open = True

	def quit(self) -> typing.NoReturn:
		if self.synchronizer:
			self.synchronizer.stop()
		if self.time_stamp_synchronizer:
			self.time_stamp_synchronizer.stop()
		raise urwid.ExitMainLoop()


	@contextlib.contextmanager
	def outside_of_urwid(self, cmd: Command) -> typing.Iterator[Command]:
		if hasattr(self, 'screen'):
			self.screen.stop()
		self.show_debug('%s  # outside of urwid screen' % cmd)
		try:
			yield cmd
		finally:
			if hasattr(self, 'screen'):
				self.screen.start()

	def create_config_if_not_existing(self) -> str:
		return self.config_file.save(ignore={App.path_src, App.path_dst}, no_multi=True, if_not_existing=True)

	def open_config(self) -> bool:
		self.reset_has_error_occurred()
		fn = self.create_config_if_not_existing()
		self.open_file(fn, edit=True)
		self.load_config(fn)
		return not self.has_error_occurred()

	def delete_config(self) -> bool:
		fn = self.config_file.get_save_path()
		if os.path.isfile(fn):
			os.remove(fn)
			self.show_info('deleted %s' % fn)
			return True
		else:
			self.show_error('no config file found')
			return False

	def load_config(self, fn: typing.Optional[str] = None) -> None:
		if fn:
			self.config_file.load_file(fn)
		else:
			self.config_file.load()
		FileWidget.update_symbols()

	def open_node(self, node: model.ComparisonNode, *, ask_always: bool = False, edit: typing.Optional[bool] = None) -> None:
		if not ask_always:
			if node.type_src is model.TYPE.NOT_EXISTING and node.type_dst is model.TYPE.NOT_EXISTING:
				self.show_error('no such file or directory on either side')
				return
			elif  node.type_src is model.TYPE.NOT_EXISTING:
				self.open_file_or_directory(node.path_dst)
				return
			elif  node.type_dst is model.TYPE.NOT_EXISTING:
				self.open_file_or_directory(node.path_src)
				return

		last_view = self.save_view()
		def open_src() -> None:
			self.open_file_or_directory(node.path_src, edit=edit)
			self.open_view(last_view)
		def open_dst() -> None:
			self.open_file_or_directory(node.path_dst, edit=edit)
			self.open_view(last_view)

		self.open_view(urwid_dialog.Dialog(self,
			'Which version do you want to open?\n'
			'Source: {node.path_src}\n'
			'Destination: {node.path_dst}'.format(node=node),
			{
				'Source': open_src,
				'Destination': open_dst,
			},
			cancel = lambda: self.open_view(last_view),
			key_handler = self.handle_key,
		))

	def open_file_or_directory(self, path: str, edit: typing.Optional[bool] = None) -> None:
		try:
			if os.path.isdir(path):
				self.open_directory(path)
			else:
				self.open_file(path, edit=edit)
		except KeyboardInterrupt:
			pass
		except Exception as e:
			self.show_error(e)

	def open_directory(self, path: str) -> None:
		self.cmd_file_browser.replace(self.WC_PATH, path).run(context=self.outside_of_urwid)

	def open_file(self, fn: str, *, edit: typing.Optional[bool] = None) -> None:
		if not os.path.isfile(fn):
			self.show_error('%r is not a file' % fn)
			return

		if edit is None:
			mime_type = mime.get_mime_type(fn)
			self.show_debug(f'mime type: {mime_type}')
			edit = bool(re.match(self.re_mime_text, mime_type, re.I))

		if edit:
			self.edit_file(fn)
		else:
			self.open_file_with_cmd_open(fn)

	def run_rifle(self, cmd: Command, context: TYPE_CONTEXT) -> None:
		if not hasattr(self, 'rifle'):
			rifleconfig = rifle.find_conf_path()
			if not rifleconfig:
				self.show_error('failed to find rifle config')
				Command.unregister_python_callback(self.RIFLE)
				self.open_file_with_cmd_open(cmd.cmd[-1])
				return

			#https://github.com/ranger/ranger/blob/master/ranger/ext/rifle.py
			self.rifle = rifle.Rifle(rifleconfig)
			self.rifle.reload_config()
			#https://github.com/ranger/ranger/blob/master/ranger/core/fm.py
			self.rifle.hook_before_executing = lambda a, b, flags: self.screen.stop() if 'f' not in flags else None
			self.rifle.hook_after_executing = lambda a, b, flags: self.screen.start() if 'f' not in flags else None

		args = cmd.cmd[1:]
		self.show_debug('rifle.execute(%r)' % (args,))
		self.rifle.execute(args)

	def open_file_with_cmd_open(self, fn: str) -> None:
		self.show_debug('%s &>/dev/null </dev/null' % self.cmd_open.replace(self.WC_PATH, fn))
		command = self.cmd_open.replace(self.WC_PATH, fn)
		command.run(context=None)

	def edit_file(self, fn: str) -> None:
		editor = os.environ.get('EDITOR', None)
		if editor:
			command = Command([editor, self.WC_PATH])
		else:
			command = self.cmd_default_editor.get_preferred_command()

		command.replace(self.WC_PATH, fn).run(context=self.outside_of_urwid)

	def toggle_standy_after(self, *, in_progress: bool) -> None:
		if self.standby_after:
			self.disable_standby_after(in_progress=in_progress)
		else:
			self.enable_standby_after(in_progress=in_progress)

	def enable_standby_after(self, *, in_progress: bool) -> None:
		if in_progress:
			self.show_info('standby after finishing this task')
			self.standby_after = True
		else:
			self.show_error('setting standby after is only possible while a long task is running')

	def disable_standby_after(self, *, in_progress: bool) -> None:
		self.standby_after = False
		self.show_info('not going to standby')


	# ------- update -------

	def update_node(self, cw: 'ComparisonWidget', *, after: typing.Optional[typing.Callable[[], None]] = None) -> None:
		self._focused_widget = cw
		cn = cw.get_model()
		model.ComparisonNode.number_nodes = 0
		if isinstance(cn, model.DirectoryComparisonNode):
			goal = cn.statistics.get_number_nodes_to_be_updated()
		else:
			goal = 1

		def after_update_node(scan_time_in_s: float) -> None:
			self.open_view(self.treeview)
			self._focused_widget.update_widget()
			self.show_info('rescanning this node has taken %s' % time_difference_to_str(scan_time_in_s))
			del self._focused_widget
			if after:
				after()

		LongTask(self, 'Scanning directories',
			cn.update, after_update_node,
			lambda: model.ComparisonNode.number_nodes, lambda: goal,
			daemon = True,
			more_tasks_pending = False,
		).start()


	# ------- sync time stamps -------

	def sync_time_stamps_possible(self) -> bool:
		if model.ComparisonNode.compare_mode.value is not model.CMP.SHALLOW:
			self.show_big_error('Synchronizing the time stamps requires {config.key} = {val}. The program must be restarted after changing {config.key}.'.format(config=model.ComparisonNode.compare_mode, val=model.CMP.SHALLOW.value))
			return False
		return True

	def ask_to_sync_time_stamps(self) -> None:
		if not self.sync_time_stamps_possible():
			return

		last_view = self.save_view()

		def sync() -> None:
			self.open_view(last_view)
			self.sync_time_stamps()

		self.open_view(urwid_dialog.YesNoDialog(self,
			'Do you want to synchronize the modification time of files which have the same content but are not recognized as unchanged because they have a different modification time?',
			yes = self.sync_time_stamps,
			no = lambda: self.open_view(last_view),
			key_handler = self.handle_key,
		))

	def sync_time_stamps(self) -> None:
		if not self.sync_time_stamps_possible():
			return

		log = self.create_sync_logger(self.sync_time_stamps_log_name, self.sync_time_stamps_log_file_name, 'has-sync-time-stamp-log')
		synchronizer = sync.TimeStampSynchronizer(log)
		self.time_stamp_synchronizer = synchronizer

		cn = self.meta_node
		goal = synchronizer.get_number_files_to_be_checked(cn)

		LongTask(self, 'Synchronizing time stamp',
			lambda: synchronizer.sync(cn), self.after_sync_time_stamps,
			lambda: synchronizer.files_checked, lambda: goal,
			daemon = False,
			more_tasks_pending = True,  # an update happens afterwards
		).start()

	def after_sync_time_stamps(self, sync_time_in_s: float) -> None:
		model.ComparisonNode.number_nodes = 0
		goal = self.meta_node.statistics.get_number_nodes_to_be_updated()
		LongTask(self, 'Scanning directories',
			lambda: self.meta_node.update(), lambda rescan_time_in_s: self.after_sync_time_stamps_and_update_view(sync_time_in_s, rescan_time_in_s),
			lambda: model.ComparisonNode.number_nodes, lambda: goal,
			daemon = True,
			more_tasks_pending = False,
		).start()

	def after_sync_time_stamps_and_update_view(self, sync_time_in_s: float, rescan_time_in_s: float) -> None:
		assert self.time_stamp_synchronizer is not None
		root_directory_node = FileOrDirectoryNode(self.meta_node)
		self.treeview = DiffWidget(self, urwid.TreeWalker(root_directory_node))
		self.open_view(urwid_dialog.Dialog(self,
			'Finished time stamp synchronization.\n'
			'Time: {sync_time} + {rescan_time}\n'
			'Checked files: {checked}\n'
			'Changed files: {changes}\n'
			'Ignored nodes: {ignored}\n'
			'Errors: {errors}\n'.format(
				sync_time = time_difference_to_str(sync_time_in_s),
				rescan_time = time_difference_to_str(rescan_time_in_s),
				checked = self.time_stamp_synchronizer.files_checked,
				changes = self.time_stamp_synchronizer.files_changed,
				ignored = self.meta_node.statistics[model.ACTION.IGNORE],
				errors = self.time_stamp_synchronizer.errors,
			),
			{'back': lambda: self.open_view(self.treeview)},
			key_handler = self.handle_key,
		))
		self.time_stamp_synchronizer = None


	# ------- sync -------

	def ask_to_sync(self) -> None:
		last_view = self.save_view()
		statistics = ConfirmChangesStatisticsWidget()
		statistics.set(self.meta_node)
		widget = urwid.Pile([
			urwid.Text('Would you like me to do these changes?'),
			statistics,
		])
		self.open_view(urwid_dialog.YesNoDialog(self,
			widget,
			yes = self.sync,
			no = lambda: self.open_view(last_view),
			key_handler = self.handle_key,
		))

	def sync(self) -> None:
		del self.treeview

		log = self.create_sync_logger(self.sync_log_name, self.sync_log_file_name, 'has-sync-log')
		synchronizer = sync.Synchronizer(log)
		self.synchronizer = synchronizer

		goal = self.meta_node.statistics.get_number_nodes_to_be_changed()

		LongTask(self, 'Synchronizing directories',
			self.sync_in_other_thread, self.after_sync,
			lambda: synchronizer.nodes_synchronized, lambda: goal,
			daemon = False,
			more_tasks_pending = False,
		).start()

	def create_sync_logger(self, log_name: str, fn: str, attr_has_created_log: str) -> logging.Logger:
		log = logging.getLogger(log_name)
		log.setLevel(self.sync_log_level)
		if fn and not getattr(self, attr_has_created_log, False):
			fn = datetime.datetime.now().strftime(fn)
			if self.sync_log_location is LOG_LOCATION.SOURCE:
				ffn = os.path.join(self.meta_node.children[0].path_src, fn)
				self.ensure_that_directory_exists(ffn)
				log.addHandler(logging.FileHandler(ffn, mode='wt'))
			elif self.sync_log_location is LOG_LOCATION.DESTINATION:
				ffn = os.path.join(self.meta_node.children[0].path_dst, fn)
				self.ensure_that_directory_exists(ffn)
				log.addHandler(logging.FileHandler(ffn, mode='wt'))
			elif self.sync_log_location is LOG_LOCATION.BOTH:
				ffn = os.path.join(self.meta_node.children[0].path_src, fn)
				self.ensure_that_directory_exists(ffn)
				log.addHandler(logging.FileHandler(ffn, mode='wt'))
				last_ffn = ffn
				ffn = os.path.join(self.meta_node.children[0].path_dst, fn)
				if os.path.realpath(ffn) != os.path.realpath(last_ffn):
					self.ensure_that_directory_exists(ffn)
					log.addHandler(logging.FileHandler(ffn, mode='wt'))
			log.addHandler(AppHandler(self))
			setattr(self, attr_has_created_log, True)
		return log

	def ensure_that_directory_exists(self, ffn: str) -> None:
		path, fn = os.path.split(ffn)
		if not os.path.exists(path):
			os.makedirs(path)
		if self.notify_log_files:
			self.print_after_end('created log file %s' % ffn)

	def sync_in_other_thread(self) -> None:
		assert self.synchronizer is not None
		self.synchronizer.sync(self.meta_node)
		self.show_info('sync')
		subprocess.run(['sync'])

	def after_sync(self, sync_time_in_s: float) -> None:
		assert self.synchronizer is not None
		self.open_view(urwid_dialog.Dialog(self,
			'Finished synchronization.\n'
			'Time:    {time}\n'
			'Changes: {changes}\n'
			'Ignored: {ignored}\n'
			'Errors:  {errors}\n'.format(
				time = time_difference_to_str(sync_time_in_s),
				changes = self.synchronizer.nodes_synchronized,
				ignored = self.meta_node.statistics[model.ACTION.IGNORE],
				errors = self.synchronizer.errors,
			),
			{'quit': self.quit},
			key_handler = self.handle_key,
		))


	# ------- last update -------

	time_stamp_format = Synchronizer.time_stamp_format.lstrip('# ')

	def show_last_sync_time(self, *, show_errors: bool) -> None:
		t = self.get_last_sync_time(show_errors)
		if t is None:
			return

		self.show_info('last synchronization: %s' % t)

	def get_last_sync_time(self, show_errors: bool) -> typing.Optional[str]:
		if not hasattr(self, 'paths'):
			if show_errors:
				self.show_info('There is no time of a last synchronization because no paths have been set yet')
			return None
		fn = self.sync_log_file_name
		if self.sync_log_location is LOG_LOCATION.NONE:
			if show_errors:
				self.show_info('I don\'t know when the last synchronization happened because logging is disabled')
			return None
		elif self.sync_log_location is LOG_LOCATION.DESTINATION:
			path_dst = self.paths[0][2]
			fn = os.path.join(path_dst, fn)
		else:
			path_src = self.paths[0][1]
			fn = os.path.join(path_src, fn)
		path, fn = os.path.split(fn)
		if not os.path.isdir(path):
			if show_errors:
				self.show_info('%s does not exist, these directories have probably never been synchronized with this program' % path)
			return None
		fn = self.log_file_name_pattern_to_regex(fn)
		fn = '^' + fn + '$'
		reo = re.compile(fn)

		logs: typing.List[typing.Tuple[datetime.datetime, str]] = []
		for fn in os.listdir(path):
			if reo.match(fn):
				dt = self.read_sync_time_from_log_file(os.path.join(path, fn))
				if dt is not None:
					logs.append((dt, fn))

		if not logs:
			if show_errors:
				self.show_info('no log file found, these directories have probably never been synchronized with this program')
			return None

		return max(logs)[0].strftime(self.time_stamp_format)

	def read_sync_time_from_log_file(self, fn: str) -> typing.Optional[datetime.datetime]:
		with open(fn, 'rt') as f:
			ln = f.readline().rstrip()
		try:
			return datetime.datetime.strptime(ln, sync.Synchronizer.time_stamp_format)
		except ValueError as e:
			self.show_error('failed to parse time stamp %r from log file %r' % (ln, fn))
			return None

	def log_file_name_pattern_to_regex(self, fn_pattern: str) -> str:
		wildcards = {
			'%Y' : '[0-9]{4}',
			'%m' : '[0-9]{2}',
			'%d' : '[0-9]{2}',
			'%H' : '[0-9]{2}',
			'%M' : '[0-9]{2}',
			'%S' : '[0-9]{2}',
			'%z' : '[+-][0-9]+',
			'%a' : '[A-Za-z]+',
			'%A' : '[A-Za-z]+',
			'%b' : '[A-Za-z]+',
			'%B' : '[A-Za-z]+',
			'%c' : '.+',
			'%I' : '[0-9]{2}',
			'%p' : '[aApP][mM]',
		}

		fn_pattern = re.escape(fn_pattern)
		for wc in wildcards:
			fn_pattern = fn_pattern.replace(re.escape(wc), wildcards[wc])

		return fn_pattern


	# ------- help -------

	def open_help_list_of_key_mappings(self) -> None:
		self.open_help(HelpWidgetListOfKeyMappings(self, self.command_maps))

	def open_help_list_of_commands(self) -> None:
		self.open_help(HelpWidgetListOfImplementedCommands(self))

	def open_help_config(self) -> None:
		self.open_help(HelpWidgetFromResource(self, self.resource_help_config))

	def open_help(self, widget: urwid.Widget) -> None:
		if self._last_view is None:
			self._last_view = self.save_view()
		self.open_view(widget)

	def close_help(self) -> None:
		assert self._last_view is not None
		self.open_view(self._last_view)
		self._last_view = None


	# ------- main -------

	def mainloop(self) -> None:
		self.loop.run()
		for ln in self.lines_to_print_after_end:
			print(ln)
		if self.notify_log_files and self.lines_to_print_after_end:
			print('''\
if you want to disable logging open the config file with `udsync --edit-config`
and set `set sync.log.location = none`
if you want to disable this info set `set print-log-files-at-end = false`.
'''.rstrip())

		lsblk.udisksctl.remove_logger()
		for dev in tuple(lsblk.mounted_devices):
			try:
				dev.unmount()
				print('unmounted %s' % dev.path)
			except lsblk.SubprocessException as e:
				print(f'failed to unmount {dev.path}: {e}')
				continue

			backing_device = dev.get_crypto_backing_device()
			if backing_device:
				try:
					backing_device.lock()
					print('locked %s' % backing_device.path)
				except lsblk.SubprocessException as e:
					print(f'failed to lock {backing_device.path}: {e}')
					continue

		self.do_after()

	def do_after(self) -> None:
		if self.standby_after:
			self.cmd_standby.run()
			self.standby_after = False

	def register_color(self, color: urwid_colors.Color) -> None:
		self.screen.register_palette_entry(*color.to_palette_tuple())

	@contextlib.contextmanager
	def password_screen(self) -> typing.Iterator[None]:
		self.screen.stop()
		try:
			yield None
		finally:
			self.screen.start()


#https://docs.python.org/3/howto/logging-cookbook.html#a-qt-gui-for-logging
class AppHandler(logging.Handler):

	def __init__(self, app: App) -> None:
		super().__init__()
		self.app = app

	def emit(self, record: logging.LogRecord) -> None:
		if record.levelno >= logging.ERROR:
			self.app.show_error(record.getMessage())
		elif record.levelno >= logging.WARNING:
			self.app.show_warning(record.getMessage())


# ========== main widget ==========

class DiffWidget(urwid.TreeListBox, urwid_multi_key_support.MultiKeySupport, View):

	help_bar_content = Config('diff.help-bar', [
		urwid_multi_key_support.HelpItem(HELP_LIST_OF_KEY_MAPPINGS, 'help'),
		urwid_multi_key_support.HelpItem(FUNC_NODE_TOGGLE_DIRECTION, 'toggle direction'),
		urwid_multi_key_support.HelpItem(FUNC_NODE_TOGGLE_IGNORE, 'toggle ignore'),
		urwid_multi_key_support.HelpItem([FUNC_SYNC, FUNC_SYNC_ASK], 'sync'),
		urwid_multi_key_support.HelpItem([FUNC_SYNC_TIME_STAMPS, FUNC_SYNC_TIME_STAMPS_ASK], 'sync time stamps'),
		urwid_multi_key_support.HelpItem(FUNC_DIFF, 'show changes'),
		urwid_multi_key_support.HelpItem('<O>', 'open ...'),
		urwid_multi_key_support.HelpItem('<y>', 'copy ...'),
		urwid_multi_key_support.HelpItem(CONFIG, 'edit config'),
	])

	PATH_SRC = '{path.src}'
	PATH_DST = '{path.dst}'
	PATH_FROM = '{path.change-from}'
	PATH_TO = '{path.change-to}'
	cmd_diff = Config('cmd.diff', CommandWithAlternatives([
		['vimdiff', PATH_SRC, PATH_DST],  # exit with :qa
		['gitd', '--open-always', '--no-index', '--', PATH_TO, PATH_FROM],  # requires git-viewer version 1.9.0 or newer
		Command(['git', '--paginate', 'diff', '--no-index', '--', PATH_TO, PATH_FROM], env=dict(GIT_PAGER='less -+F')),
		['diff', '--color=always', '--side-by-side', PATH_SRC, PATH_DST, '|', 'less', '-R'],  # this is unintuitive because lines to be added are red and lines to be deleted green. swapping src and dst would make it even more unintuitive with --side-by-side.
	]), help='the command used to display the differences between two files')

	_command_map = urwid.command_map.copy()
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_MAX_LEFT, CURSOR_MAX_UP)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_MAX_RIGHT, CURSOR_MAX_DOWN)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_LEFT, FUNC_VIEW_COLLAPSE_PARENT)
	urwid_multi_key_support.replace_command(_command_map, urwid.CURSOR_RIGHT, FUNC_VIEW_EXPAND_OR_DIFF)
	_command_map['u'] = FUNC_NODE_TOGGLE_DIRECTION
	_command_map[' '] = FUNC_NODE_TOGGLE_IGNORE
	_command_map['>'] = FUNC_NODE_SET_DIRECTION_SRC_TO_DST
	_command_map['<'] = FUNC_NODE_SET_DIRECTION_DST_TO_SRC
	_command_map['f5'] = FUNC_NODE_UPDATE
	_command_map['i'] = FUNC_DIFF
	_command_map['f6'] = FUNC_SHOW_LAST_SYNC_TIME

	_command_map['}'] = FUNC_CURSOR_NEXT_SIBLING
	_command_map['{'] = FUNC_CURSOR_PREV_SIBLING
	_command_map[']'] = urwid_multi_key_support.SubCommandMap()
	_command_map[']'][']'] = FUNC_CURSOR_NEXT_PARENT
	_command_map['['] = urwid_multi_key_support.SubCommandMap()
	_command_map['[']['['] = FUNC_CURSOR_PARENT

	_command_map['y'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['p'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['p']['s'] = FUNC_YANK_PATH_SRC
	_command_map['y']['p']['d'] = FUNC_YANK_PATH_DST
	_command_map['y']['n'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['n']['s'] = FUNC_YANK_NAME_SRC
	_command_map['y']['n']['d'] = FUNC_YANK_NAME_DST
	_command_map['y']['d'] = urwid_multi_key_support.SubCommandMap()
	_command_map['y']['d']['s'] = FUNC_YANK_DIR_SRC
	_command_map['y']['d']['d'] = FUNC_YANK_DIR_DST

	_command_map['a'] = FUNC_RENAME
	_command_map['d'] = urwid_multi_key_support.SubCommandMap()
	_command_map['d']['d'] = FUNC_RENAME_FROM
	_command_map['p'] = urwid_multi_key_support.SubCommandMap()
	_command_map['p']['p'] = FUNC_RENAME_TO

	_command_map['o'] = FUNC_OPEN
	_command_map['O'] = urwid_multi_key_support.SubCommandMap()
	_command_map['O']['<'] = FUNC_OPEN_SRC
	_command_map['O']['>'] = FUNC_OPEN_DST
	_command_map['O']['e'] = urwid_multi_key_support.SubCommandMap()
	_command_map['O']['e']['<'] = FUNC_OPEN_SRC_TEXT
	_command_map['O']['e']['>'] = FUNC_OPEN_DST_TEXT
	_command_map['O']['x'] = urwid_multi_key_support.SubCommandMap()
	_command_map['O']['x']['<'] = FUNC_OPEN_SRC_XDG
	_command_map['O']['x']['>'] = FUNC_OPEN_DST_XDG
	_command_map['H'] = FUNC_OPEN_SRC
	_command_map['L'] = FUNC_OPEN_DST
	_command_map['f11'] = FUNC_DEBUG_SHELL
	_command_map['f12'] = FUNC_SYNC_TIME_STAMPS_ASK
	_command_map['enter'] = FUNC_SYNC_ASK
	_command_map['backspace'] = FUNC_TOGGLE_SHOW_SAME  # <ctrl h>
	_command_map.implemented_commands = {
		urwid.CURSOR_UP,
		urwid.CURSOR_DOWN,
		urwid.CURSOR_PAGE_UP,
		urwid.CURSOR_PAGE_DOWN,
		CURSOR_MAX_UP,
		CURSOR_MAX_DOWN,
		FUNC_CURSOR_FIRST_SIBLING,
		FUNC_CURSOR_LAST_SIBLING,
		FUNC_CURSOR_NEXT_SIBLING,
		FUNC_CURSOR_PREV_SIBLING,
		FUNC_CURSOR_PARENT,
		FUNC_CURSOR_NEXT_PARENT,
		FUNC_VIEW_COLLAPSE,
		FUNC_VIEW_COLLAPSE_PARENT,
		FUNC_VIEW_EXPAND,
		FUNC_VIEW_EXPAND_OR_DIFF,
		FUNC_NODE_TOGGLE_DIRECTION,
		FUNC_NODE_TOGGLE_IGNORE,
		FUNC_NODE_SET_DIRECTION_SRC_TO_DST,
		FUNC_NODE_SET_DIRECTION_DST_TO_SRC,
		FUNC_NODE_UPDATE,
		FUNC_YANK_PATH_SRC,
		FUNC_YANK_PATH_DST,
		FUNC_YANK_NAME_SRC,
		FUNC_YANK_NAME_DST,
		FUNC_YANK_DIR_SRC,
		FUNC_YANK_DIR_DST,
		FUNC_OPEN,
		FUNC_OPEN_ASK,
		FUNC_OPEN_SRC,
		FUNC_OPEN_DST,
		FUNC_OPEN_TEXT,
		FUNC_OPEN_ASK_TEXT,
		FUNC_OPEN_SRC_TEXT,
		FUNC_OPEN_DST_TEXT,
		FUNC_OPEN_XDG,
		FUNC_OPEN_ASK_XDG,
		FUNC_OPEN_SRC_XDG,
		FUNC_OPEN_DST_XDG,
		FUNC_DIFF,
		FUNC_SYNC,
		FUNC_SYNC_ASK,
		FUNC_SYNC_TIME_STAMPS,
		FUNC_SYNC_TIME_STAMPS_ASK,
		FUNC_TOGGLE_SHOW_SAME,
		FUNC_SET_SHOW_SAME_TRUE,
		FUNC_SET_SHOW_SAME_FALSE,
		FUNC_RENAME,
		FUNC_RENAME_FROM,
		FUNC_RENAME_TO,
		FUNC_SHOW_LAST_SYNC_TIME,
		HELP_LIST_OF_KEY_MAPPINGS,
		HELP_LIST_OF_COMMANDS,
		HELP_CONFIG,
		CONFIG,
		QUIT,
		QUIT_ASK,
		QUIT_ASK_IF_LONG,
		FUNC_DEBUG_SHELL,
	}

	to_be_displayed_anyway: typing.Optional[model.ComparisonNode] = None

	def __init__(self, app: App, tree_walker: urwid.TreeWalker) -> None:
		super().__init__(tree_walker)
		self.init_multi_key_support(app)
		self.app = app
		self.clipboard = clipboard.Clipboard(self.app.ui_notifier)
		self.statistics_widget = StatisticsWidget()
		self.update_statistics()
		self._rename_from: typing.Optional[ComparisonWidget] = None

	def update_statistics(self) -> None:
		self.statistics_widget.set(self.focus.get_model())


	# ------- implementing View methods -------

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self._command_map, self.app.ui_notifier, edit_context=False)

	def get_box_widget(self) -> urwid.Widget:
		return urwid.Frame(self, footer=self.statistics_widget)


	# ------- overriding widget methods -------

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None
		DiffWidget.to_be_displayed_anyway = None

		try:
			func = self._command_map[key]
			if func == FUNC_VIEW_COLLAPSE:
				self.set_expanded(False)
			elif func == FUNC_VIEW_COLLAPSE_PARENT:
				self.collapse_parent()
			elif func == FUNC_VIEW_EXPAND:
				self.set_expanded(True)
			elif func == FUNC_VIEW_EXPAND_OR_DIFF:
				if self.focus.get_model().has_children():
					self.set_expanded(True)
				else:
					self.open_diff(self.focus.get_model())
			elif func == CURSOR_MAX_UP:
				self.focus_home(size)
			elif func == CURSOR_MAX_DOWN:
				self.focus_end(size)
			elif func == FUNC_CURSOR_NEXT_SIBLING:
				self.focus_next_sibling()
			elif func == FUNC_CURSOR_PREV_SIBLING:
				self.focus_prev_sibling()
			elif func == FUNC_CURSOR_LAST_SIBLING:
				self.focus_last_sibling()
			elif func == FUNC_CURSOR_FIRST_SIBLING:
				self.focus_first_sibling()
			elif func == FUNC_CURSOR_PARENT:
				self.focus_parent()
			elif func == FUNC_CURSOR_NEXT_PARENT:
				self.focus_next_parent()

			elif func == FUNC_NODE_TOGGLE_DIRECTION:
				try:
					self.focus.get_model().toggle_direction()
				except model.CommandNotAllowed as e:
					self.app.show_error(e)
			elif func == FUNC_NODE_TOGGLE_IGNORE:
				try:
					self.focus.get_model().toggle_ignore()
				except model.CommandNotAllowed as e:
					self.show_error(e)
			elif func == FUNC_NODE_SET_DIRECTION_SRC_TO_DST:
				try:
					self.focus.get_model().set_direction_recursively(model.DIRECTION.SRC_TO_DST)
				except model.CommandNotAllowed as e:
					self.show_error(e)
			elif func == FUNC_NODE_SET_DIRECTION_DST_TO_SRC:
				try:
					self.focus.get_model().set_direction_recursively(model.DIRECTION.DST_TO_SRC)
				except model.CommandNotAllowed as e:
					self.show_error(e)
			elif func == FUNC_NODE_UPDATE:
				self.app.update_node(self.focus)

			elif func == FUNC_YANK_PATH_SRC:
				self.clipboard.copy(self.focus.get_model().path_src)
			elif func == FUNC_YANK_PATH_DST:
				self.clipboard.copy(self.focus.get_model().path_dst)
			elif func == FUNC_YANK_NAME_SRC:
				tmp = self.focus.get_model().path_src
				tmp = os.path.split(tmp)[1]
				self.clipboard.copy(tmp)
			elif func == FUNC_YANK_NAME_DST:
				tmp = self.focus.get_model().path_dst
				tmp = os.path.split(tmp)[1]
				self.clipboard.copy(tmp)
			elif func == FUNC_YANK_DIR_SRC:
				tmp = self.focus.get_model().path_src
				tmp = os.path.split(tmp)[0]
				self.clipboard.copy(tmp)
			elif func == FUNC_YANK_DIR_DST:
				tmp = self.focus.get_model().path_dst
				tmp = os.path.split(tmp)[0]
				self.clipboard.copy(tmp)

			elif func == FUNC_OPEN:
				self.app.open_node(self.focus.get_model())
			elif func == FUNC_OPEN_ASK:
				self.app.open_node(self.focus.get_model(), ask_always=True)
			elif func == FUNC_OPEN_SRC:
				self.app.open_file_or_directory(self.focus.get_model().path_src)
			elif func == FUNC_OPEN_DST:
				self.app.open_file_or_directory(self.focus.get_model().path_dst)

			elif func == FUNC_OPEN_TEXT:
				self.app.open_node(self.focus.get_model(), edit=True)
			elif func == FUNC_OPEN_ASK_TEXT:
				self.app.open_node(self.focus.get_model(), ask_always=True, edit=True)
			elif func == FUNC_OPEN_SRC_TEXT:
				self.app.open_file_or_directory(self.focus.get_model().path_src, edit=True)
			elif func == FUNC_OPEN_DST_TEXT:
				self.app.open_file_or_directory(self.focus.get_model().path_dst, edit=True)

			elif func == FUNC_OPEN_XDG:
				self.app.open_node(self.focus.get_model(), edit=False)
			elif func == FUNC_OPEN_ASK_XDG:
				self.app.open_node(self.focus.get_model(), ask_always=True, edit=False)
			elif func == FUNC_OPEN_SRC_XDG:
				self.app.open_file_or_directory(self.focus.get_model().path_src, edit=False)
			elif func == FUNC_OPEN_DST_XDG:
				self.app.open_file_or_directory(self.focus.get_model().path_dst, edit=False)

			elif func == FUNC_DIFF:
				self.open_diff(self.focus.get_model())

			elif func == FUNC_SET_SHOW_SAME_TRUE:
				self.set_show_same(True)
			elif func == FUNC_SET_SHOW_SAME_FALSE:
				self.set_show_same(False)
			elif func == FUNC_TOGGLE_SHOW_SAME:
				self.set_show_same(toggle=True)

			elif func == FUNC_RENAME:
				self.rename_current_node()
			elif func == FUNC_RENAME_FROM:
				self.rename_from()
			elif func == FUNC_RENAME_TO:
				self.rename_to()

			elif func == FUNC_SYNC_ASK:
				self.app.ask_to_sync()
			elif func == FUNC_SYNC:
				self.app.sync()

			elif func == FUNC_SYNC_TIME_STAMPS_ASK:
				self.app.ask_to_sync_time_stamps()
			elif func == FUNC_SYNC_TIME_STAMPS:
				self.app.sync_time_stamps()

			elif func == FUNC_SHOW_LAST_SYNC_TIME:
				self.app.show_last_sync_time(show_errors=True)

			elif func == FUNC_DEBUG_SHELL:
				self.open_debug_shell()

			elif self.app.handle_key(self._command_map, size, key) is None:
				pass

			else:
				out = typing.cast(typing.Optional[URWID_TYPE_KEY], self.__super.keypress(size, key))
				if not out:
					self.update_statistics()
				return out

			self.update_statistics()
			assert func in self._default_command_map.implemented_commands
			return None

		finally:
			self.reset_command_map()


	# ------- focus -------

	def focus_first_sibling(self) -> None:
		parent = self.focus.get_node().get_parent()
		if parent is None:
			# if this node does not have a parent, then it does not have any siblings either
			return

		self.set_focus(parent.get_first_child())

	def focus_last_sibling(self) -> None:
		parent = self.focus.get_node().get_parent()
		if parent is None:
			# if this node does not have a parent, then it does not have any siblings either
			return

		self.set_focus(parent.get_last_child())

	def focus_next_sibling(self) -> None:
		f = self.focus.get_node().next_sibling()
		if f is None:
			return

		self.set_focus(f)

	def focus_prev_sibling(self) -> None:
		f = self.focus.get_node().prev_sibling()
		if f is None:
			return

		self.set_focus(f)

	def focus_parent(self) -> None:
		parent = self.focus.get_node().get_parent()
		if parent is None:
			return

		self.set_focus(parent)

	def focus_next_parent(self) -> None:
		parent = self.focus.get_node().get_parent()
		if parent is None:
			return

		f = parent.next_sibling()
		if f is None:
			return

		self.set_focus(f)


	def focus_child(self, parent_node: urwid.ParentNode, name: str) -> None:
		for key in parent_node.get_child_keys():
			#assert isinstance(tree_node, FileOrDirectoryNode)
			if key.name == name:
				tree_node = parent_node.get_child_node(key)
				self.body.set_focus(tree_node)
				return

		self.app.show_error('failed to find node to be focused %s' % name)


	# ------- custom methods -------

	def set_show_same(self, value: bool = False, *, toggle: bool = False) -> None:
		widget = self.focus.get_parent_or_self()
		tree_node = widget.get_node()
		if toggle:
			value = not tree_node.show_same

		if not value:
			self.move_focus_to_visible_widget()

		tree_node.show_same = value

		widget.update_widget()
		self.focus.update_widget()

	def move_focus_to_visible_widget(self) -> None:
		# focus a widget which stays visible to avoid crash with urwid.treetools.TreeWidgetError: Can't find key in ParentNode
		# must be called *before* setting show_same to False because this method uses prev_inorder which would trigger the TreeWidgetError
		widget = self.focus
		while widget.get_model().state is model.STATE.SAME:
			prev = widget.prev_inorder()
			if prev is None:
				break
			widget = prev

		# there is also a self.set_focus but that does not help because it has a delay
		self.body.set_focus(widget.get_node())

	def set_expanded(self, value: bool) -> None:
		comparison_widget: ComparisonWidget = self.focus
		comparison_widget.set_expanded(value)

		tree_node: FileOrDirectoryNode = comparison_widget.get_node()
		if hasattr(tree_node, 'last_focus') and tree_node.last_focus.is_existing():
			self.body.set_focus(tree_node.last_focus)

	def collapse_parent(self) -> None:
		comparison_widget: ComparisonWidget = self.focus
		tree_node: FileOrDirectoryNode = comparison_widget.get_node()
		if comparison_widget.expanded:
			comparison_widget.set_expanded(False)
			tree_node.last_focus = tree_node
			return

		parent_tree_node = tree_node.get_parent()
		if parent_tree_node is None:
			comparison_widget.set_expanded(False)
			tree_node.last_focus = tree_node
			return

		self.body.set_focus(parent_tree_node)
		parent_widget = parent_tree_node.get_widget()
		parent_widget.set_expanded(False)
		parent_tree_node.last_focus = tree_node


	def open_diff(self, cn: model.ComparisonNode) -> None:
		if cn.type_src is not model.TYPE.NOT_EXISTING and cn.type_dst is model.TYPE.NOT_EXISTING:
			self.app.open_file_or_directory(cn.path_src)
		elif cn.type_dst is not model.TYPE.NOT_EXISTING and cn.type_src is model.TYPE.NOT_EXISTING:
			self.app.open_file_or_directory(cn.path_dst)
		else:
			src_to_dst = self.is_src_to_dst(cn)
			cmd = self.cmd_diff \
				.replace(self.PATH_SRC, cn.path_src) \
				.replace(self.PATH_DST, cn.path_dst) \
				.replace(self.PATH_FROM, cn.path_src if src_to_dst else cn.path_dst) \
				.replace(self.PATH_TO, cn.path_dst if src_to_dst else cn.path_src)
			cmd.run(context=self.app.outside_of_urwid)

	def is_src_to_dst(self, cn: model.ComparisonNode) -> bool:
		if cn.direction is model.DIRECTION.SRC_TO_DST:
			return True
		elif cn.direction is model.DIRECTION.DST_TO_SRC:
			return False
		elif cn.default_direction is model.DIRECTION.SRC_TO_DST:
			return True
		elif cn.default_direction is model.DIRECTION.DST_TO_SRC:
			return False
		elif isinstance(cn, model.DirectoryComparisonNode):
			if cn.direction_of_children is model.DIRECTION.SRC_TO_DST:
				return True
			elif cn.direction_of_children is model.DIRECTION.DST_TO_SRC:
				return False
		return True


	def open_debug_shell(self) -> None:
		w = self.focus
		cn = w.get_model()

		self.app.screen.stop()
		print(f'w = self.focus = {w}')
		print(f'cn = w.get_model() = {cn}')
		try:
			import IPython
			IPython.embed(locals_=locals())
		except ImportError:
			try:
				import bpython
				bpython.embed(locals_=locals())
			except ImportError:
				import code
				code.interact(local=locals())
		self.app.screen.start()


	# ------- rename -------

	@property
	def rename_logger(self) -> logging.Logger:
		return self.app.create_sync_logger(self.app.rename_log_name, self.app.rename_log_file_name, 'has-rename-log')

	def rename_current_node(self) -> None:
		cn: model.ComparisonNode = self.focus.get_model()
		parent = self.focus.get_parent_or_self()
		if cn.type_src is model.TYPE.NOT_EXISTING and cn.type_dst is model.TYPE.NOT_EXISTING:
			self.app.show_error('I cannot rename %s because both sides are not existing' % cn.name)
			return

		def check(oldpath: str, newname: str) -> typing.Tuple[str, str]:
			if not os.path.exists(oldpath):
				raise Return('file system has changed since scanning it, %s does not exist anymore' % oldpath)

			newpath = os.path.join(os.path.dirname(oldpath), newname)
			if os.path.exists(newpath):
				raise Return(f'{newname} exists already')

			return oldpath, newpath

		last_view = self.app.save_view()
		edit = urwid.Edit(edit_text=cn.name)

		def rename() -> None:
			newname = edit.get_edit_text()
			try:
				if cn.type_src is not model.TYPE.NOT_EXISTING:
					path_src_from, path_src_to = check(cn.path_src, newname)
				if cn.type_dst is not model.TYPE.NOT_EXISTING:
					path_dst_from, path_dst_to = check(cn.path_dst, newname)
			except Return as e:
				self.app.show_error(e.msg)
				return

			self.app.show_info('renaming {oldname} to {newname}'.format(oldname=cn.name, newname=newname))
			if cn.type_src is not model.TYPE.NOT_EXISTING:
				self.rename_file_or_directory(path_src_from, path_src_to)
			if cn.type_dst is not model.TYPE.NOT_EXISTING:
				self.rename_file_or_directory(path_dst_from, path_dst_to)

			self.app.open_view(last_view)
			self.body.set_focus(parent.get_node())
			self.app.update_node(parent, after = lambda: self.focus_child(parent.get_node(), newname))

		def cancel() -> None:
			self.app.open_view(last_view)

		self.app.open_view(urwid_dialog.Dialog(self,
			urwid.Pile([
				urwid.Text('Please enter a new name for %s:' % cn.name),
				edit,
			]),
			{
				'Rename': rename,
				'Cancel': cancel,
			},
			cancel = cancel,
			key_handler = self.app.handle_key,
			add_commands = {urwid.ACTIVATE : rename},
		))

	def rename_from(self) -> None:
		if isinstance(self.focus, TitleWidget):
			self.app.show_error('no node selected to be renamed/moved')
			return

		self._rename_from = self.focus
		assert isinstance(self._rename_from, ComparisonWidget)
		if self.is_renaming_one_side():
			self.app.show_info('choose a target what to rename %s to' % self._rename_from.get_model().name)
		elif self.is_moving_both_sides():
			self.app.show_info('choose a target where to move %s' % self._rename_from.get_model().name)
		else:
			assert False

	def rename_to(self) -> None:
		if self._rename_from is None:
			self.app.show_error('no node to be renamed/moved has been chosen')
			return
		if isinstance(self.focus, TitleWidget):
			self.app.show_error('no target node selected')
			return

		if self.is_renaming_one_side():
			self.rename_one_side(self._rename_from, self.focus)
		elif self.is_moving_both_sides():
			self.move_both_sides(self._rename_from, self.focus)
		else:
			assert False

	def is_renaming_one_side(self) -> bool:
		if self._rename_from is None:
			return False

		cn_from: model.ComparisonNode = self._rename_from.get_model()
		if cn_from.type_src is model.TYPE.NOT_EXISTING and cn_from.type_dst is not model.TYPE.NOT_EXISTING:
			return True
		if cn_from.type_src is not model.TYPE.NOT_EXISTING and cn_from.type_dst is model.TYPE.NOT_EXISTING:
			return True

		return False

	def is_moving_both_sides(self) -> bool:
		if self._rename_from is None:
			return False

		cn_from: model.ComparisonNode = self._rename_from.get_model()
		if cn_from.type_src is not model.TYPE.NOT_EXISTING and cn_from.type_dst is not model.TYPE.NOT_EXISTING:
			return True

		return False

	def rename_one_side(self, cw_from: 'ComparisonWidget', cw_to: 'ComparisonWidget') -> None:
		cn_from = cw_from.get_model()
		cn_to = cw_to.get_model()

		if cn_to.type_src is not model.TYPE.NOT_EXISTING and cn_to.type_dst is not model.TYPE.NOT_EXISTING:
			self.app.show_error('cannot rename {name_from} to {name_to} because both sides are existing at the target'.format(name_from=cn_from.name, name_to=cn_to.name))
			return
		elif cn_from.type_src is not model.TYPE.NOT_EXISTING and cn_to.type_src is model.TYPE.NOT_EXISTING:
			path_from = cn_from.path_src
			path_to = cn_to.path_src
		elif cn_from.type_dst is not model.TYPE.NOT_EXISTING and cn_to.type_dst is model.TYPE.NOT_EXISTING:
			path_from = cn_from.path_dst
			path_to = cn_to.path_dst
		else:
			self.app.show_error('cannot rename {name_from} to {name_to} because the same sides are existing/missing'.format(name_from=cn_from.name, name_to=cn_to.name))
			return

		if os.path.exists(path_to):
			self.app.show_error('file system has changed since scanning it, %s exists by now' % path_to)
			return
		if not os.path.exists(path_from):
			self.app.show_error('file system has changed since scanning it, %s does not exist anymore' % path_from)
			return

		self.app.show_info('renaming {path_from} to {path_to}'.format(path_from=path_from, path_to=path_to))
		self.rename_file_or_directory(path_from, path_to)

		# make sure the focused widget does not disappear to avoid crash in render
		DiffWidget.to_be_displayed_anyway = cn_to

		assert cn_from.parent is not None, 'parent cannot be None because rename_from checks that the widget is not a TitleWidget'
		cn_from.parent.children.remove(cn_from)
		self.app.update_node(cw_to)
		cw_from.get_parent_or_self().update_widget()
		cw_to.get_parent_or_self().update_widget()

	def move_both_sides(self, cw_from: 'ComparisonWidget', cw_to: 'ComparisonWidget') -> None:
		cn_from = cw_from.get_model()
		cn_to = cw_to.get_model()

		if cn_to.type_src is not model.TYPE.DIRECTORY and cn_to.type_dst is not model.TYPE.DIRECTORY:
			self.app.show_error('move target must be a directory')
			return

		def check(path_from: str, path_to: str) -> typing.Tuple[str, str]:
			if not os.path.isdir(path_to):
				raise Return('file system has changed since scanning it, %s is not a directory anymore' % path_to)
			if not os.path.exists(path_from):
				raise Return('file system has changed since scanning it, %s does not exist anymore' % path_from)
			path_to = os.path.join(path_to, os.path.split(path_from)[1])
			if os.path.exists(path_to):
				raise Return(f'cannot move {path_from} because {path_to} exists already')
			return path_from, path_to

		try:
			path_src_from, path_src_to = check(cn_from.path_src, cn_to.path_src)
			path_dst_from, path_dst_to = check(cn_from.path_dst, cn_to.path_dst)
		except Return as e:
			self.app.show_error(e.msg)
			return

		self.app.show_info(f'moving {path_src_from} to {path_src_to}')
		self.rename_file_or_directory(path_src_from, path_src_to)
		self.app.show_info(f'moving {path_dst_from} to {path_dst_to}')
		self.rename_file_or_directory(path_dst_from, path_dst_to)

		assert cn_from.parent is not None, 'parent cannot be None because rename_from checks that the widget is not a TitleWidget'
		cn_from.parent.children.remove(cn_from)
		# a simple `cn_to.children.append(cn_from)` is not enough because the all the paths in cn_from need to be updated
		# `self.app.update_node(cw_to)` is not the most efficient way but the easiest way
		self.app.update_node(cw_to)
		cw_from.get_parent_or_self().update_widget()
		cw_to.update_widget()


	def rename_file_or_directory(self, path_from: str, path_to: str) -> None:
		target_dir = os.path.dirname(path_to)
		if not os.path.exists(target_dir):
			self.rename_logger.info('mkdir %r' % target_dir)
			os.makedirs(target_dir)
		self.rename_logger.info('mv %r %r' % (path_from, path_to))
		os.rename(path_from, path_to)


class ComparisonWidget(urwid.TreeWidget):

	indent_cols: int  # inherited from TreeWidget

	highlight_action_of_expanded_parent_as_changed = Config('diff.highligt-action-of-expanded-parent-as-changed', False)

	action_width = 5

	COLOR_SEP = urwid_colors.Color.SEP_COLOR
	BG_ACTION_DEFAULT = 'black'
	BG_ACTION_CHANGED = 'blue'

	FG_ACTION_CREATE  = 'green,bold'
	FG_ACTION_DELETE  = 'red,bold'
	FG_ACTION_CHANGE  = 'default'
	FG_ACTION_IGNORE  = 'default'
	FG_ACTION_NONE    = 'white'
	FG_ACTION_ERROR   = 'red,bold'

	color_action_create = urwid_colors.ColorConfig('diff.color.action-create', FG_ACTION_CREATE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_delete = urwid_colors.ColorConfig('diff.color.action-delete', FG_ACTION_DELETE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_change = urwid_colors.ColorConfig('diff.color.action-change', FG_ACTION_CHANGE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_ignore = urwid_colors.ColorConfig('diff.color.action-ignore', FG_ACTION_IGNORE + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_none   = urwid_colors.ColorConfig('diff.color.action-none',   FG_ACTION_NONE   + COLOR_SEP + BG_ACTION_DEFAULT)
	color_action_error  = urwid_colors.ColorConfig('diff.color.action-error',  FG_ACTION_ERROR  + COLOR_SEP + BG_ACTION_DEFAULT)

	color_changed_action_create = urwid_colors.ColorConfig('diff.color.changed-action-create', FG_ACTION_CREATE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_delete = urwid_colors.ColorConfig('diff.color.changed-action-delete', FG_ACTION_DELETE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_change = urwid_colors.ColorConfig('diff.color.changed-action-change', FG_ACTION_CHANGE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_ignore = urwid_colors.ColorConfig('diff.color.changed-action-ignore', FG_ACTION_IGNORE + COLOR_SEP + BG_ACTION_CHANGED)
	color_changed_action_none =   urwid_colors.ColorConfig('diff.color.changed-action-none',   FG_ACTION_NONE   + COLOR_SEP + BG_ACTION_CHANGED)

	action_symbol = DictConfig('diff.action-symbols', {
		model.ACTION.NONE               : ' = ',
		model.ACTION.IGNORE             : ' | ',
		model.ACTION.ERROR              : ' ! ',
		model.ACTION.CREATE             : ' >+',
		model.ACTION.DELETE             : ' >-',
		model.ACTION.UPDATE             : ' > ',
		model.ACTION.DOWNGRADE          : ' >!',
		model.ACTION.UNDO_CREATE        : '-< ',
		model.ACTION.UNDO_DELETE        : '+< ',
		model.ACTION.UNDO_UPDATE        : '!< ',
		model.ACTION.UNDO_DOWNGRADE     : ' < ',
		model.ACTION.DIR_CHANGE_DESTINATION  : ' > ',
		model.ACTION.DIR_CHANGE_SOURCE  : ' < ',
		model.ACTION.DIR_CHANGE_BOTH    : '> <',
		model.ACTION.CHANGE_DESTINATION_TYPE : ' >t',
		model.ACTION.CHANGE_SOURCE_TYPE : 't< ',
		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        : '->+',
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   : '+<-',
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN : '->t',
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      : 't<-',
	})

	action_format = {
		model.ACTION.NONE               : (color_action_none.value,   color_changed_action_none.value),
		model.ACTION.IGNORE             : (color_action_ignore.value, color_changed_action_ignore.value),
		model.ACTION.CREATE             : (color_action_create.value, color_changed_action_create.value),
		model.ACTION.DELETE             : (color_action_delete.value, color_changed_action_delete.value),
		model.ACTION.UPDATE             : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DOWNGRADE          : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_CREATE        : (color_action_delete.value, color_changed_action_delete.value),
		model.ACTION.UNDO_DELETE        : (color_action_create.value, color_changed_action_create.value),
		model.ACTION.UNDO_UPDATE        : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_DOWNGRADE     : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_DESTINATION  : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_SOURCE  : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.DIR_CHANGE_BOTH    : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_DESTINATION_TYPE : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_SOURCE_TYPE : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN        : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN   : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN : (color_action_change.value, color_changed_action_change.value),
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN      : (color_action_change.value, color_changed_action_change.value),

		model.ACTION.ERROR              : (color_action_error.value,  color_action_error.value),
	}

	# These symbols should all have the same width, otherwise the action symbols will not be aligned.
	# I have tried to auto align this but failed with redrawing the TreeListBox, see commit 47198a46f630165c9157c3dc21acf2e97656160a
	pref_symbol_dir_show_same = Config('diff.symbol.show-same.directory', urwid_colors.ColorStr('<color=blue>*</color>'))
	pref_symbol_dir_hide_same = Config('diff.symbol.hide-same.directory', urwid_colors.ColorStr(' '))
	pref_symbol_file_show_same = Config('diff.symbol.show-same.file', pref_symbol_dir_show_same.value)
	pref_symbol_file_hide_same = Config('diff.symbol.hide-same.file', pref_symbol_dir_hide_same.value)


	def __init__(self, tree_node: urwid.TreeNode) -> None:
		super().__init__(tree_node)

		cn = self.get_model()
		cn.set_direction_changed_listener(self.update_action)

		# I need to set self.expanded because it's used by urwid internally
		if isinstance(cn, model.DirectoryComparisonNode):
			self.expanded = cn.is_expanded
		else:
			self.expanded = False

	# methods of urwid.TreeWidget:
	get_node: typing.Callable[[], 'FileOrDirectoryNode']  # FileOrDirectoryNode is an urwid.TreeNode

	def get_model(self) -> model.ComparisonNode:
		return self.get_node().get_value()

	def get_action(self) -> typing.Tuple[str, str]:
		comparison_node = self.get_model()
		has_action_been_changed = comparison_node.has_direction_been_changed()
		if isinstance(comparison_node, model.DirectoryComparisonNode) and (not comparison_node.is_expanded or self.highlight_action_of_expanded_parent_as_changed):
			has_action_been_changed = has_action_been_changed or comparison_node.has_child_direction_been_changed()
		action_symbol = self.action_symbol[comparison_node.action]
		action_format = self.action_format[comparison_node.action][has_action_been_changed]
		action_symbol = ' ' + action_symbol + ' '
		return (action_format, action_symbol)

	def get_parent_or_self(self) -> 'ComparisonWidget':
		parent_node = self.get_node().get_parent()
		if parent_node is None:
			return self
		return parent_node.get_widget()


	# ------- overriding methods -------

	def get_indented_widget(self) -> urwid.Widget:
		tn = self.get_node()
		cn = self.get_model()

		indent_cols = self.get_indent_cols()
		is_expanded = isinstance(cn, model.DirectoryComparisonNode) and cn.is_expanded
		self.widget_src = FileWidget(cn.name_src, cn.type_src, cn.type_dst, cn.error_src, is_expanded, indent_cols)
		self.widget_dst = FileWidget(cn.name_dst, cn.type_dst, cn.type_src, cn.error_dst, is_expanded, indent_cols)
		self.widget_action = urwid.Text(self.get_action())

		if isinstance(cn, model.DirectoryComparisonNode):
			if tn.show_same:
				pref_symbol = self.pref_symbol_dir_show_same
			else:
				pref_symbol = self.pref_symbol_dir_hide_same
		else:
			if tn.show_same:
				pref_symbol = self.pref_symbol_file_show_same
			else:
				pref_symbol = self.pref_symbol_file_hide_same
		pref_symbol = urwid_colors.ColorStr.to_markup(pref_symbol)
		widget_pref = urwid.Text(pref_symbol)

		widget = urwid.Columns(
			[
				('weight', 1, self.widget_src),
				('fixed', self.action_width, self.widget_action),
				('weight', 1, self.widget_dst),
				('pack', widget_pref),
			], dividechars=0)

		widget = urwid.AttrMap(widget, None, urwid_colors.focus_map)

		return widget

	def get_indent_cols(self) -> int:
		return self.indent_cols * (self.get_node().get_depth() - 1)

	def update_expanded_icon(self) -> None:
		self.widget_src.update_expanded_icon(self.expanded)
		self.widget_dst.update_expanded_icon(self.expanded)


	def selectable(self) -> bool:
		return True


	# ------- custom methods -------

	def update_action(self) -> None:
		self.widget_action.set_text(self.get_action())

	def update_widget(self) -> None:
		self.get_node().reload_children()
		self._w = self.get_indented_widget()


	def set_expanded(self, value: bool) -> None:
		cn = self.get_model()
		if not isinstance(cn, model.DirectoryComparisonNode):
			return

		cn.set_expanded(value)
		# expanded is used by urwid so I need to set it
		self.expanded = value
		self.update_expanded_icon()
		if not self.highlight_action_of_expanded_parent_as_changed:
			self.update_action()

	def is_expanded(self) -> bool:
		return self.get_model().is_expanded


class TitleWidget(ComparisonWidget):

	color_title = urwid_colors.ColorConfig('diff.color.title', 'cyan')

	sym_src = Config('diff.symbol.source', '🖳 ')
	sym_dst = Config('diff.symbol.destination', '🖴 ')

	def get_indented_widget(self) -> urwid.Widget:
		cn = self.get_model()

		self.widget_src = urwid.Text(self.sym_src + cn.name_src)
		self.widget_dst = urwid.Text(self.sym_dst + cn.name_dst)
		self.widget_action = urwid.Text(self.get_action())

		pref_symbol = self.pref_symbol_dir_hide_same
		pref_symbol = urwid_colors.ColorStr.to_markup(pref_symbol)
		widget_pref = urwid.Text(pref_symbol)

		widget = urwid.Columns(
			[
				('weight', 1, self.widget_src),
				('fixed', self.action_width, self.widget_action),
				('weight', 1, self.widget_dst),
				('pack', widget_pref),
			], dividechars=0)

		widget = urwid.AttrMap(widget, None, urwid_colors.focus_map)
		widget = urwid.AttrMap(widget, self.color_title, type(self).color_title.focus.value)

		return widget

	def update_expanded_icon(self) -> None:
		pass

	def set_expanded(self, value: bool) -> None:
		pass


class FileWidget(urwid.AttrMap):

	color_type_file = urwid_colors.ColorConfig('diff.color.type-file', 'default', focus='black/white')
	color_type_link = urwid_colors.ColorConfig('diff.color.type-link', 'blue', focus='black/blue')
	color_type_dir = urwid_colors.ColorConfig('diff.color.type-dir', 'yellow', focus='black/yellow')
	color_type_missing_file = urwid_colors.ColorConfig('diff.color.type-missing-file', 'magenta', focus='magenta/white')
	color_type_missing_link = urwid_colors.ColorConfig('diff.color.type-missing-link', 'magenta', focus='magenta/blue')
	color_type_missing_dir = urwid_colors.ColorConfig('diff.color.type-missing-dir', 'magenta', focus='magenta/yellow')
	color_error = urwid_colors.ColorConfig('diff.color.error', 'default/red')

	sym_directory_closed   = Config('diff.symbol.directory.closed',   '🗀 ')  # 📁
	sym_directory_expanded = Config('diff.symbol.directory.expanded', '🗁 ')  # 📂
	sym_file               = Config('diff.symbol.file',               '🗎 ')  # 📄
	sym_link               = Config('diff.symbol.link',               '🠦 ')  # 🢥🡪🠒
	sym_deleted            = Config('diff.symbol.deleted',            '🗙 ')

	@classmethod
	def update_symbols(cls) -> None:
		cls.icon_directory_closed   = urwid.Text(cls.sym_directory_closed.value)
		cls.icon_directory_expanded = urwid.Text(cls.sym_directory_expanded.value)

		cls.icon_file = urwid.Text(cls.sym_file.value)
		cls.icon_link = urwid.Text(cls.sym_link.value)
		cls.icon_not_existing = urwid.Text(cls.sym_deleted.value)

		cls.icon_width = max(urwid.calc_width(symcfg.value, 0, len(symcfg.value)) for symcfg in (cls.sym_directory_closed, cls.sym_directory_expanded, cls.sym_file, cls.sym_deleted))

	def __init__(self, name: str, filetype: model.TYPE, other_filetype: model.TYPE, error: typing.Optional[str], expanded: bool, indent_cols: int) -> None:
		self.filetype = filetype

		icon = self.get_icon_widget(expanded)
		name = urwid.Text(name)
		attr = self.get_attr(filetype, other_filetype, error)

		widget = urwid.Columns([('fixed', self.icon_width, icon), name], dividechars=1)
		widget = urwid.Padding(widget, width=('relative', 100), left=indent_cols)
		super().__init__(widget, attr)


	# ------- internal methods -------

	def get_attr(self, filetype: model.TYPE, other_filetype: model.TYPE, error: typing.Optional[str]) -> str:
		if error:
			return self.color_error
		elif filetype is model.TYPE.FILE:
			return self.color_type_file
		elif filetype is model.TYPE.DIRECTORY:
			return self.color_type_dir
		elif filetype is model.TYPE.LINK:
			return self.color_type_link
		elif filetype is model.TYPE.NOT_EXISTING:
			if other_filetype is model.TYPE.DIRECTORY:
				return self.color_type_missing_dir
			if other_filetype is model.TYPE.LINK:
				return self.color_type_missing_link
			else:
				return self.color_type_missing_file
		else:
			assert False

	def get_icon_widget(self, expanded: bool) -> urwid.Widget:
		filetype = self.filetype
		if filetype == model.TYPE.DIRECTORY:
			if expanded:
				icon = self.icon_directory_expanded
			else:
				icon = self.icon_directory_closed
		elif filetype == model.TYPE.FILE:
			icon = self.icon_file
		elif filetype == model.TYPE.NOT_EXISTING:
			icon = self.icon_not_existing
		elif filetype is model.TYPE.LINK:
			icon = self.icon_link
		else:
			assert False

		return icon


	# ------- public methods -------

	def update_expanded_icon(self, expanded: bool) -> None:
		# see original implementation of
		# urwid.TreeWidget.update_expanded_icon
		self.base_widget.widget_list[0] = self.get_icon_widget(expanded)


class FileOrDirectoryNode(urwid.ParentNode):

	default_show_same = Config('diff.show-same', False, help = {
		True: 'show files and directories which are the same on both sides',
		False: 'hide files and directories which are the same on both sides'
	})

	@property
	def show_same(self) -> bool:
		if self._show_same is None:
			parent = self.get_parent()
			if parent is None:
				return self.default_show_same
			return parent.show_same
		return self._show_same
	@show_same.setter
	def show_same(self, val: bool) -> None:
		parent = self.get_parent()
		if parent is None:
			self.default_show_same = val
			self._show_same = None
		elif parent.show_same == val:
			self._show_same = None
		else:
			self._show_same = val

	_child_keys: typing.Optional[typing.Sequence[model.ComparisonNode]]
	_children: typing.Dict[model.ComparisonNode, urwid.TreeNode]
	get_widget: typing.Callable[[], typing.Union[ComparisonWidget, TitleWidget]]
	get_parent: typing.Callable[[], typing.Optional['FileOrDirectoryNode']]
	get_value: typing.Callable[[], model.ComparisonNode]
	get_key: typing.Callable[[], model.ComparisonNode]
	get_depth: typing.Callable[[], int]

	def __init__(self, comparison_node: model.ComparisonNode, parent: typing.Optional['FileOrDirectoryNode'] = None) -> None:
		super().__init__(value=comparison_node, key=comparison_node, parent=parent)
		self._show_same = None


	# ------- overriding methods -------

	def load_widget(self) -> urwid.Widget:
		if isinstance(self.get_key(), model.MetaNode):
			return TitleWidget(self)
		return ComparisonWidget(self)

	def load_child_keys(self) -> typing.Sequence[model.ComparisonNode]:
		'''Provide ParentNode with an ordered list of child keys (implementation of virtual function)'''
		cn = self.get_value()
		if isinstance(cn, model.DirectoryComparisonNode):
			if self.show_same:
				return cn.children
			else:
				return [child for child in cn.children if child.state is not model.STATE.SAME or child.has_error() or child is DiffWidget.to_be_displayed_anyway]
		else:
			return []

	def load_child_node(self, key: model.ComparisonNode) -> urwid.TreeNode:
		'''Load the child node for a given key (implementation of virtual function)'''
		return FileOrDirectoryNode(key, parent=self)

	def reload_children(self) -> None:
		self._child_keys = None
		self._children = {}


	# ------- custom methods -------

	def is_existing(self) -> bool:
		parent = self.get_parent()
		if parent is None:
			return True
		return self.get_key() in parent.get_child_keys()


# ========== statistics widget ==========

class StatisticsWidget(urwid.WidgetWrap):

	sep = Config('diff.statistics.sep', urwid_colors.ColorStr(', '))
	pattern_errors = Config('diff.statistics.pattern.errors', urwid_colors.ColorStr('<color={' + FileWidget.color_error.key + '}>{n} error(s)</color>'))
	pattern_action = Config('diff.statistics.pattern.action', urwid_colors.ColorStr('{n}x<color={{action_color_name}}/bright black>{action_symbol}</color>'))

	actions = Config('diff.statistics.actions-to-show', [
		model.ACTION.ERROR,
		model.ACTION.NONE,
		model.ACTION.IGNORE,
		model.ACTION.CREATE,
		model.ACTION.DELETE,
		model.ACTION.UNDO_CREATE,
		model.ACTION.UNDO_DELETE,

		model.ACTION.UPDATE,
		model.ACTION.DOWNGRADE,
		model.ACTION.UNDO_UPDATE,
		model.ACTION.UNDO_DOWNGRADE,

		model.ACTION.CHANGE_DESTINATION_TYPE,
		model.ACTION.CHANGE_SOURCE_TYPE,

		model.ACTION.CREATE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.UNDO_DELETE_DIRECTORY_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.CHANGE_DESTINATION_TYPE_BUT_DELETE_SOME_CHILDREN,
		model.ACTION.CHANGE_SOURCE_TYPE_BUT_DELETE_SOME_CHILDREN,
	])

	def __init__(self) -> None:
		super().__init__(None)
		self._widget_statistics: typing.Optional[urwid.Widget] = None
		self._widget_file_info: typing.Optional[urwid.Widget] = None

	def set(self, cn: model.ComparisonNode) -> None:
		if isinstance(cn, model.DirectoryComparisonNode):
			self.set_directory(cn)
		else:
			self.set_file(cn)

	def set_directory(self, cn: model.DirectoryComparisonNode) -> None:
		'''show statistics which actions cn's children have'''
		if cn.has_error():
			self.set_file(cn)
			return

		if self._widget_statistics is None:
			self._widget_statistics = urwid.Text('')

		statistics = cn.statistics
		markup: typing.List[urwid_colors.URWID_TYPE_MARKUP] = []
		for a in self.actions:
			n = statistics.statistics.get(a, 0)
			if n == 0:
				continue

			if markup:
				markup.append(urwid_colors.ColorStr.to_markup(self.sep))

			symbol = ComparisonWidget.action_symbol[a]
			name = a.name.lower()
			color_name = ComparisonWidget.action_format[a][0]
			markup.append(urwid_colors.ColorStr.to_markup(self.pattern_action.replace('{action_color_name}', color_name), format=dict(n=n, action_symbol=symbol, action_name=name)))

		markup = urwid_colors.ColorStr.simplify_markup(markup)
		self._widget_statistics.set_text(markup)
		self._w = self._widget_statistics

	# ------- file info -------

	pattern_file_info = Config('diff.file-info.format', urwid_colors.ColorStr('{size}, last modified: {mtime}{error}'), help='supports the wildcards {size} for the size of the file, {mtime} for the last modification time of the file and {error}, see %diff.file-info.error%')
	pattern_file_error = Config('diff.file-info.error', urwid_colors.ColorStr(', <color=red>{error}</color>'), help='this is inserted in %diff.file-info.format% for {error} in case there is an error, supported wild cards: {error}')
	pattern_link_info = Config('diff.link-info.format', urwid_colors.ColorStr('-> {target}{error}'), help='supports the wildcards {target} for the target of the link, {size} for the size of the link, {mtime} for the last modification time of the link and {error}, see %diff.link-info.error%')
	pattern_link_error = Config('diff.link-info.error', urwid_colors.ColorStr(', <color=red>{error}</color>'), help='this is inserted in %diff.link-info.format% for {error} in case there is an error, supported wild cards: {error}')
	fmt_time = Config('diff.file-info.date', '%x %X', help='https://docs.python.org/3/library/time.html#time.strftime')
	pattern_error_only = Config('diff.error-info.format', urwid_colors.ColorStr('<color=red>{error}</color>'), help='this is displayed in case of an error where no file is existing or a directory cannot be read')
	size_is_metric = Config('diff.file-info.size.metric', False, help={
		True: 'based on powers of 10³',
		False: 'based on powers of 2¹⁰',
	})
	size_sep = Config('diff.file-info.size.sep', ' ', help='separator between number and unit')

	def set_file(self, cn: model.ComparisonNode) -> None:
		'''show one text widget for each side with file information or error messages'''
		if self._widget_file_info is None:
			self._widget_file_info_src = urwid.Text('')
			self._widget_file_info_dst = urwid.Text('')
			self._widget_file_info = urwid.Columns(
				[
					('weight', 1, self._widget_file_info_src),
					('fixed', ComparisonWidget.action_width, urwid.Text('')),
					('weight', 1, self._widget_file_info_dst),
				], dividechars=0)

		is_dir = isinstance(cn, model.DirectoryComparisonNode)
		self._widget_file_info_src.set_text(self.get_file_info(cn.path_src, error=cn.error_src, is_link=cn.type_src is model.TYPE.LINK, is_dir=is_dir))
		self._widget_file_info_dst.set_text(self.get_file_info(cn.path_dst, error=cn.error_dst, is_link=cn.type_dst is model.TYPE.LINK, is_dir=is_dir))
		self._w = self._widget_file_info
	
	def get_file_info(self, path: str, error: typing.Optional[str], is_link: bool, is_dir: bool) -> urwid_colors.URWID_TYPE_MARKUP:
		if is_dir:
			info = self.pattern_error_only.format(error=error) if error else ''

		elif is_link:
			st = os.stat(path, follow_symlinks=False)
			info = self.pattern_link_info.format(
				mtime = self.format_time(st.st_mtime),
				size = self.format_size(st.st_size),
				target = read_symlink(path)[1],
				error = self.pattern_link_error.format(error=error) if error else '',
			)

		elif not os.path.exists(path):
			info = self.pattern_error_only.format(error=error) if error else ''

		else:
			info = self.pattern_file_info.format(
				mtime = self.format_time(os.path.getmtime(path)),
				size = self.format_size(os.path.getsize(path)),
				error = self.pattern_file_error.format(error=error) if error else '',
			)

		return urwid_colors.ColorStr.to_markup(info)

	def format_time(self, time: float) -> str:
		return datetime.datetime.fromtimestamp(time).strftime(self.fmt_time)

	def format_size(self, size: int) -> str:
		return human_bytes.format(size, metric=self.size_is_metric, sep=self.size_sep)


class ConfirmChangesStatisticsWidget(StatisticsWidget):

	sep = Config('dialog.statistics.sep', urwid_colors.ColorStr('\n'))
	pattern_errors = Config('dialog.statistics.pattern.errors', StatisticsWidget.pattern_errors.value)
	pattern_action = Config('dialog.statistics.pattern.action', urwid_colors.ColorStr('- {n} x <color={{action_color_name}}/bright black>{action_symbol}</color>'))

	@property
	def actions(self) -> typing.Sequence[model.ACTION]:  # type: ignore [override]  # yes, I am aware that I am overriding a technically read/writable attribute with a read only attribute
		return [a for a in StatisticsWidget.actions.value if a not in model.Statistics.ACTIONS_NO_CHANGE]


# ========== create new backup plan ==========

class PathsGroup(urwid.WidgetWrap):

	after_edit = Config('backup-plan-widget.after-edit', urwid_colors.ColorStr(' <color=bright black>|</color> '), help='a symbol indicating the end of an edit widget')

	@property
	def base_widget(self) -> urwid.Widget:
		return self._w.base_widget

	def __init__(self, app: App, master: 'BackupPlanWidget') -> None:
		self.path_src = urwid_directory_chooser.PathEdit(app, 'src: ', '', key_handler=app.handle_key)
		self.path_dst = urwid_directory_chooser.PathEdit(app, 'dst: ', '', key_handler=app.handle_key)
		self.btn_add = urwid_dialog.ColorButton('+', master.add_path_group)
		self.btn_del = urwid_dialog.ColorButton('-', master.del_path_group)

		w_add = self.btn_add.calc_required_width()
		w_del = self.btn_del.calc_required_width()
		w_after_edit = urwid.Text(urwid_colors.ColorStr.to_markup(self.after_edit))
		widget = urwid_dialog.TabAwarePile((
			urwid_dialog.TabAwareColumns((
				self.path_src,
				(urwid.PACK, w_after_edit),
				(urwid.FIXED, w_add + w_del, urwid.Text('')),
			), cycle_focus=False),
			urwid_dialog.TabAwareColumns((
				self.path_dst,
				(urwid.PACK, w_after_edit),
				(urwid.FIXED, w_add, self.btn_add),
				(urwid.FIXED, w_del, self.btn_del)
			), cycle_focus=False),
			urwid.Text(''),
		), cycle_focus=False)
		super().__init__(widget)

	def focus_first(self) -> None:
		self._w.focus_position = 0
		self._w.contents[0][0].focus_position = 0

	def focus_last(self) -> None:
		self._w.focus_position = 1


	def has_opened_directory_chooser(self) -> bool:
		return self.path_src.has_opened_directory_chooser or self.path_dst.has_opened_directory_chooser

	def is_empty(self) -> bool:
		return not self.get_path_src() and not self.get_path_dst()

	def get_invalid_paths(self) -> 'list[tuple[str, bool]]':
		'''
		:return: list (expanded path, can be created) tuples, empty list means both src and dst are valid
		'''
		return self.path_src.get_invalid_path() + self.path_dst.get_invalid_path()

	def get_path_src(self) -> str:
		return self.path_src.get_path()

	def get_path_dst(self) -> str:
		return self.path_dst.get_path()


class BackupPlanWidget(urwid.WidgetWrap, View):

	help_bar_content = Config('backup-plan-widget.help-bar.button', [
		urwid_multi_key_support.HelpItem(urwid.ACTIVATE, 'click button'),
		urwid_multi_key_support.HelpItem(urwid_dialog.NEXT_SELECTABLE, 'focus next'),
		urwid_multi_key_support.HelpItem(urwid_dialog.PREV_SELECTABLE, 'focus previous'),
	])
	urwid_directory_chooser.PathEdit.help_bar_content.key = 'backup-plan-widget.help-bar.path-edit'

	def __init__(self, app: App, name: str, fn: str, create: typing.Callable[['BackupPlanWidget'], None], cancel: typing.Callable[[], None]):
		self.app = app
		self.name = name
		self.fn = fn
		text = urwid.Text(f'creating backup plan {name!r}')
		sep = urwid.Text('')
		self.create_callback = create
		self.btn_create = urwid_dialog.ColorButton('create', self.validate_and_create)
		self.btn_cancel = urwid_dialog.ColorButton('cancel', lambda btn: cancel())
		self.was_edit_path_focused = False

		self.buttons_frame = urwid_dialog.ButtonsFrame(self.btn_create, self.btn_cancel)
		self.pile = urwid_dialog.TabAwarePile([text, sep, PathsGroup(app, self), self.buttons_frame])
		widget = urwid.Filler(self.pile)
		super().__init__(widget)
		self.help_bar_edit = urwid_multi_key_support.HelpBar(urwid_directory_chooser.PathEdit.help_bar_content.value, self._command_map, self.app.ui_notifier, edit_context=True)
		self.help_bar_button = urwid_multi_key_support.HelpBar(self.help_bar_content, self._command_map, self.app.ui_notifier, edit_context=False)
		self.on_path_edit_focus_change(self.is_edit_path_focused())

	# ------- View methods -------

	def get_box_widget(self) -> urwid.Widget:
		return self

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return self.help_bar_edit

	# ------- update help bar -------

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		out = super().keypress(size, key)
		if not out and self.is_edit_path_focused() != self.was_edit_path_focused:
			self.was_edit_path_focused = not self.was_edit_path_focused
			if not any(w.has_opened_directory_chooser() for w, options in self.pile.contents if isinstance(w, PathsGroup)):
				self.on_path_edit_focus_change(self.was_edit_path_focused)
		if out:
			return self.app.handle_key(self._command_map, size, key)
		return typing.cast(typing.Optional[URWID_TYPE_KEY], out)

	def is_edit_path_focused(self) -> bool:
		widget = self._w
		while hasattr(widget, 'focus'):
			widget = widget.base_widget.focus
			if isinstance(widget, urwid_directory_chooser.PathEdit):
				return True
		return False

	def on_path_edit_focus_change(self, focus: bool) -> None:
		self.was_edit_path_focused = focus
		if focus:
			help_bar = self.help_bar_edit
		else:
			help_bar = self.help_bar_button
		self.app.show_help_bar(help_bar)

	# ------- buttons -------

	def add_path_group(self, btn_add: urwid.Button) -> None:
		contents = self.pile.contents
		i = next(i for i in range(len(contents)) if isinstance(w := contents[i][0], PathsGroup) and w.btn_add.base_widget is btn_add)
		contents.insert(i+1, (PathsGroup(self.app, self), (urwid.PACK, None)))
		self.pile.focus_position = i + 1

	def del_path_group(self, btn_del: urwid.Button) -> None:
		contents = self.pile.contents
		i = next(i for i in range(len(contents)) if isinstance(w := contents[i][0], PathsGroup) and w.btn_del.base_widget is btn_del)
		del contents[i]

		if not any(isinstance(w, PathsGroup) for w, options in contents):
			contents.insert(i, (PathsGroup(self.app, self), (urwid.PACK, None)))
			self.pile.focus_position = i

	def validate_and_create(self, btn_create: urwid.Button) -> None:
		paths = self.get_path_groups()
		if not paths:
			self.app.show_error('please enter a pair of paths')
			return

		invalid_paths: 'list[tuple[str, bool]]' = sum((w.get_invalid_paths() for w in paths), start=[])
		failed_to_mount = set(path.split(os.path.sep)[0] for path, can_be_created in invalid_paths if not can_be_created)
		if failed_to_mount:
			for path in failed_to_mount:
				self.app.show_error("failed to mount or unlock %r" % path)
			if any(can_be_created for path, can_be_created in invalid_paths):
				self.app.show_error("and one or more other paths are not existing")
			return

		if any(path == '' for path, can_be_created in invalid_paths):
			self.app.show_error("a src or dst path is missing")
			if any(path for path, can_be_created in invalid_paths):
				self.app.show_error("and one or more entered paths are not existing")
			return

		self._ask_to_create_not_existing_directories([path for path, can_be_created in invalid_paths])

	def _ask_to_create_not_existing_directories(self, invalid_paths: 'Sequence[str]') -> None:
		if not invalid_paths:
			self.create_callback(self)
			return

		self.app.open_view(urwid_dialog.YesNoDialog(self.app,
			f'Directory {invalid_paths[0]!r} does not exist. Do you want to create it?',
			yes = lambda: self._yes_create_directory(invalid_paths),
			no = self._no_dont_create_directory,
			key_handler = self.app.handle_key,
		))

	def _yes_create_directory(self, invalid_paths: 'Sequence[str]') -> None:
		os.makedirs(invalid_paths[0])
		self._ask_to_create_not_existing_directories(invalid_paths[1:])

	def _no_dont_create_directory(self) -> None:
		# update entry colors because a previous directory might have been created
		for path in self.get_path_groups():
			path.get_invalid_paths()

		self.app.open_view(self)


	# ------- getters -------

	def get_name(self) -> str:
		return self.name

	def get_file_name(self) -> str:
		return self.fn

	def get_path_groups(self) -> typing.Sequence[PathsGroup]:
		return [w for w, options in self.pile.contents if isinstance(w, PathsGroup) and not w.is_empty()]


# ========== progress bar ==========

class LongTask:

	progress_bar_update_time = Config('progress-bar.update-time', 0.5, unit='seconds', help='time between two updates of the progress bar')
	time_before_opening_loading_screen = Config('time-before-opening-progress-bar', 1, unit='seconds', help='wait time before opening the progress bar to avoid an unnecessary progress bar when scanning small directories')

	def __init__(self, app: App, label: str,
		run: typing.Callable[[], None], after: typing.Callable[[float], None],
		get_progress: typing.Callable[[], int], get_goal: typing.Callable[[], int],
		*,
		daemon: bool,
		show_in_load_screen: typing.Optional[str] = None,
		more_tasks_pending: bool,
	) -> None:
		self.app = app
		self.label = label
		self.do_in_other_thread = run
		self.do_after_finished = after
		self.get_progress = get_progress
		self.get_goal = get_goal
		self.daemon = daemon
		self.show_in_load_screen = show_in_load_screen
		self.more_tasks_pending = more_tasks_pending

	def start(self) -> None:
		self.exception_in_other_thread: typing.Optional[BaseException] = None
		self.thread = threading.Thread(target=self._in_other_thread, daemon=self.daemon)
		self.thread.start()
		self.t0 = time.time()
		self.thread.join(self.time_before_opening_loading_screen)
		if self.thread.is_alive():
			self.progressview = ProgressView(self.app, label=self.label, done=self.get_goal())
			self.progressbar = self.progressview.progressbar
			self.app.open_view(self.progressview)
			self.app.loop.set_alarm_in(self.progress_bar_update_time, self.update_progressbar)
			if self.show_in_load_screen:
				self.app.show_info(self.show_in_load_screen)
		else:
			self.after()

	def _in_other_thread(self) -> None:
		try:
			self.do_in_other_thread()
		except BaseException as e:
			self.exception_in_other_thread = e

	def update_progressbar(self, loop: urwid.MainLoop, user_data: typing.Any) -> None:
		if self.thread.is_alive():
			self.progressbar.add_progress(self.get_progress() - self.progressbar.current, self.get_goal())
			self.app.loop.set_alarm_in(self.progress_bar_update_time, self.update_progressbar)
		else:
			self.after()

	def after(self) -> None:
		if self.exception_in_other_thread:
			raise self.exception_in_other_thread

		self.t1 = time.time()
		# tell urwid to call do_after_finished at the correct time
		# after keypress has returned and _command_map has been reset (in case of a multi key combo)
		# and where urwid redraws the screen if necessary
		self.app.loop.set_alarm_in(0, lambda loop, time_in_s: self.do_after_finished(time_in_s), self.t1 - self.t0)

		if not self.more_tasks_pending:
			self.app.loop.set_alarm_in(0, lambda loop, arg: self.app.do_after(), None)


class ProgressView(urwid.WidgetWrap, urwid_multi_key_support.MultiKeySupport, View):

	_command_map = urwid.command_map.copy()
	_command_map['esc'] = FUNC_TOGGLE_STANDBY_AFTER
	_command_map.implemented_commands = {
		FUNC_TOGGLE_STANDBY_AFTER,
	}

	color_label = urwid_colors.ColorConfig('progress-bar.color.title', 'cyan')
	color_todo = urwid_colors.ColorConfig('progress-bar.color.todo', 'default')
	color_done = urwid_colors.ColorConfig('progress-bar.color.done', 'green/white')
	unit = 'files'

	help_bar_content = Config('progress-bar.help-bar', [
		urwid_multi_key_support.HelpItem([QUIT, QUIT_ASK, QUIT_ASK_IF_LONG], 'quit'),
		urwid_multi_key_support.HelpItem(FUNC_TOGGLE_STANDBY_AFTER, 'standby after'),
	])

	def __init__(self, app: App, label: str, *, done: int) -> None:
		self.label = urwid.Text((self.color_label, label))
		self.progressbar = urwid_timed_progress.TimedProgressBar(self.color_todo, self.color_done, done=done, units=self.unit)
		super().__init__(urwid.Pile((self.label, self.progressbar)))
		self.init_multi_key_support(app)
		self.app = app

	def selectable(self) -> bool:
		return True

	def keypress(self, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		if self.waiting_for_next_key(key):
			return None

		if super().keypress(size, key) is None:
			self.reset_command_map()
			return None

		cmd = self._command_map[key]
		if cmd == FUNC_TOGGLE_STANDBY_AFTER:
			self.app.toggle_standy_after(in_progress=True)
			out = None
		else:
			out = self.app.handle_key(self._command_map, size, key)

		self.reset_command_map()
		return out

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self._default_command_map, self.app.ui_notifier, edit_context=False)

	def get_box_widget(self) -> urwid.Widget:
		return urwid.Filler(self)



# ========== help ==========

class HelpWidget(urwid.WidgetWrap, View):

	help_bar_content = Config('help-page.help-bar', [
		urwid_multi_key_support.HelpItem(CANCEL, 'back'),
		urwid_multi_key_support.HelpItem(urwid.CURSOR_UP, 'up'),
		urwid_multi_key_support.HelpItem(urwid.CURSOR_DOWN, 'down'),
	])

	color_section = urwid_colors.ColorConfig('help-page.color.section', 'default,bold')
	color_subsection = urwid_colors.ColorConfig('help-page.color.subsection', 'default')
	indentation = Config('help-page.indentation', '  ')
	indent_subsection_title = Config('help-page.indent-subsection-title', False)

	def __init__(self, widget: urwid_multi_key_support.ExtendedListBox, app: App) -> None:
		super().__init__(widget)
		self.app = app
		widget.set_key_handler(self.handle_key)

	def handle_key(self, command_map: urwid_multi_key_support.SubCommandMap, size: URWID_TYPE_SIZE, key: URWID_TYPE_KEY) -> typing.Optional[URWID_TYPE_KEY]:
		cmd = command_map[key]
		if cmd == CANCEL:
			self.app.close_help()
		elif self.app.handle_key(command_map, size, key) is None:
			pass
		else:
			return key

		return None

	def get_box_widget(self) -> urwid.Widget:
		return self


class HelpWidgetListOfKeyMappings(HelpWidget):

	def __init__(self, app: App, command_maps: typing.Dict[str, urwid_multi_key_support.SubCommandMap]) -> None:
		widgets = []
		for widget_name, command_map in app.command_maps.items():
			title = 'key mappings in %s' % widget_name
			widget = urwid_multi_key_support.PressedKeysWidget(app, pressed_keys=[], command_map=command_map, title=title)
			widgets.extend(widget.body)
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		self.listbox = widget
		super().__init__(widget, app)

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self.listbox._default_command_map, self.app.ui_notifier, edit_context=False)


class HelpWidgetListOfImplementedCommands(HelpWidget):

	def __init__(self, app: App) -> None:
		widgets = []
		for name, cmdmap in app.command_maps.items():
			title = 'commands which can be mapped to keys in {map_name}'.format(map_name = name)
			widgets.append(HelpTitleWidget(self.color_section, title))
			for cmd in sorted(cmdmap.implemented_commands):
				widgets.append(HelpCommandWidget(cmd))
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		self.listbox = widget
		super().__init__(widget, app)

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self.listbox._default_command_map, self.app.ui_notifier, edit_context=False)

class HelpWidgetFromResource(HelpWidget):

	PREFIX_SECTION = '# '
	PREFIX_SUBSECTION = '## '
	TAB = '    '

	reo_command = re.compile(r'`(?P<command>.*?)`')

	pattern_cmd = Config('help-page.format.command', urwid_colors.ColorStr('<color={%s}>{cmd}</color>' % urwid_multi_key_support.PressedKeysLineWidget.color_cmd.key),
		help='how to format a command which no keys are mapped to. Supports the wildcard {cmd}.')
	pattern_key = Config('help-page.format.key', urwid_colors.ColorStr('<color={%s}>{key}</color> (<color={%s}>{cmd}</color>)' % (urwid_multi_key_support.PressedKeysLineWidget.color_key.key, urwid_multi_key_support.PressedKeysLineWidget.color_cmd.key)),
		help='how to format a command which one or more keys are mapped to. Supports the wildcards {key} and {cmd}.')

	def __init__(self, app: App, resource_name: str) -> None:
		self.app = app
		#https://stackoverflow.com/a/58941536
		raw = pkgutil.get_data(__name__, resource_name)
		assert raw is not None
		widgets = self.parse(raw.decode('utf-8'))
		widget = urwid_multi_key_support.ExtendedListBox(app, widgets)
		self.listbox = widget
		super().__init__(widget, app)

	def parse(self, raw: str) -> typing.Sequence[urwid.Widget]:
		widgets = []
		widgets.append(HelpLineWidget(self.indentation + '[The keyboard shortcuts mentioned in the following help page refer to the diff widget.]'))
		widgets.append(HelpLineWidget(''))
		for ln in raw.splitlines():
			ln = ln.rstrip()
			ln = ln.replace('\t', self.TAB)
			if ln.startswith(self.PREFIX_SUBSECTION):
				ln = ln[len(self.PREFIX_SUBSECTION):].strip()
				if self.indent_subsection_title:
					ln = self.indentation + ln
				widgets.append(HelpTitleWidget(self.color_subsection, ln))
			elif ln.startswith(self.PREFIX_SECTION):
				ln = ln[len(self.PREFIX_SECTION):].strip()
				widgets.append(HelpTitleWidget(self.color_section, ln))
			elif '{map_names}' in ln:
				ln = self.indentation + ln
				for map_name in self.app.command_maps.keys():
					widgets.append(HelpLineWidget(ln.format(map_names=map_name)))
			else:
				ln = self.indentation + ln
				widget = self.parse_text_line(ln)
				widgets.append(widget)

		return widgets

	def parse_text_line(self, ln: str) -> 'HelpLineWidget':
		splitted_line = self.reo_command.split(ln)
		markup = [splitted_line[0]]
		for i in range(1, len(splitted_line), 2):
			cmd = splitted_line[i]
			keys = [_key for _key, _cmd in urwid_multi_key_support.KeyMapper.iter_commands(DiffWidget._command_map) if _cmd == cmd]
			text = splitted_line[i+1]
			if keys:
				pattern = self.pattern_key
				format_args = {'cmd': cmd, 'key': keys[0]}
			else:
				pattern = self.pattern_cmd
				format_args = {'cmd': cmd}
			markup.append(urwid_colors.ColorStr.to_markup(pattern, format=format_args))
			markup.append(text)
		return HelpLineWidget(markup)

	def get_help_bar(self) -> urwid_multi_key_support.HelpBar:
		return urwid_multi_key_support.HelpBar(self.help_bar_content, self.listbox._default_command_map, self.app.ui_notifier, edit_context=False)


class HelpLineWidget(urwid.Text):
	pass

class HelpTitleWidget(urwid.Text):

	def __init__(self, color: str, text: str) -> None:
		super().__init__((color, text))

class HelpCommandWidget(urwid.Text):

	color_cmd = urwid_multi_key_support.PressedKeysLineWidget.color_cmd

	def __init__(self, text: str) -> None:
		super().__init__((self.color_cmd, text))


if __name__ == '__main__':
	app = App()
	app.load(os.path.join('test', 'src'), os.path.join('test', 'dst'))
	app.mainloop()
