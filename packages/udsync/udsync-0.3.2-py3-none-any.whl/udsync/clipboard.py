#!./runmodule.sh

import subprocess
import shlex
import enum
import typing

from confattr import Config, UiNotifier


@enum.unique
class Selection(enum.Enum):
	PRIMARY = 'primary'
	CLIPBOARD = 'clipboard'

class CopyError(Exception):
	pass


class Clipboard:

	default_selection = Config('clipboard.default-selection', Selection.CLIPBOARD)
	verbose = Config('clipboard.verbose', False, help='show the commands used to copy stuff to the clipboard/primary, this feature requires Python 3.8')

	def __init__(self, logger: UiNotifier) -> None:
		self.logger = logger

	def copy(self, text: str, selection: typing.Optional[Selection] = None) -> None:
		if selection is None:
			selection = self.default_selection
		if self.has_wlcopy():
			self.copy_wlcopy(text, selection)
		elif self.has_xsel():
			self.copy_xsel(text, selection)
		elif self.has_xclip():
			self.copy_xclip(text, selection)
		else:
			self.logger.show_error('cannot copy {text!r} to {selection}, please install wl-copy, xsel or xclip in order to use this feature'.format(text=text, selection=selection.value))
			return

		self.logger.show_info('copied %r' % text)


	def copy_wlcopy(self, text: str, selection: Selection) -> None:
		cmd = ['wl-copy']
		if selection == Selection.PRIMARY:
			cmd.append('--primary')
		cmd.append('--')
		cmd.append(text)

		if self.verbose:
			self.logger.show_info(shlex.join(cmd))
		self.run(cmd)

	def copy_xsel(self, text: str, selection: Selection) -> None:
		if selection == Selection.PRIMARY:
			sel = '--primary'
		else:
			sel = '--clipboard'

		cmd = ['xsel', '-i', sel]
		if self.verbose:
			self.logger.show_info(shlex.join(cmd))
		self.run(cmd, input=text)

	def copy_xclip(self, text: str, selection: Selection) -> None:
		if selection == Selection.PRIMARY:
			sel = 'primary'
		else:
			sel = 'clipboard'

		cmd = ['xclip', '-in', '-selection', sel]
		if self.verbose:
			self.logger.show_info(shlex.join(cmd))
		self.run(cmd, input=text)


	def has_wlcopy(self) -> bool:
		try:
			self.run(['wl-copy', '--version'])
			return True
		except FileNotFoundError:
			return False

	def has_xsel(self) -> bool:
		try:
			self.run(['xsel', '--version'])
			return True
		except FileNotFoundError:
			return False

	def has_xclip(self) -> bool:
		try:
			self.run(['xclip', '-version'])
			return True
		except FileNotFoundError:
			return False


	def run(self, cmd: typing.Sequence[str], *, input: typing.Optional[str] = None) -> None:
		try:
			subprocess.run(cmd, input=input, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
		except subprocess.SubprocessError as e:
			self.logger.show_error(e)
