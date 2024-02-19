#!./runmodule.sh

HELP = '''
If src and dst are given the two directories are compared and
a list of changes to be performed in order to make dst the same like src will be displayed.
You can choose to ignore differences or to change the direction so that src will be changed to match dst.

If only one argument is given it is considered to be the name of a backup plan.
A backup plan is one or several pairs of directories to be compared/synchronized
and may include further settings special to these directories.
If no backup plan with the given name is existing you will be prompted to select the directories
and the backup plan will be created.

If one of the directories is located on a removable drive
the file system can be identified via it's UUID and mounted automatically.

Passing no argument will use the backup plan called 'default'.

This program has an in-app help:
Press F2 for a list of all defined keyboard shortcuts.
Press F3 for a list of all commands which can be bound to keys.
Press F4 for a description of the config file syntax.

If you use any of the optional arguments only the first of them will be considered
and the program will exit immediately afterwards.
'''

import sys
import subprocess
import argparse
import contextlib
import typing

from . import ui
from .about import __doc__, __version__, APP_NAME


def print_version() -> None:
	import urwid
	print(APP_NAME, __version__)
	print("python %s" % sys.version)
	print("urwid %s" % urwid.__version__)


@contextlib.contextmanager
def tmpapp() -> typing.Iterator[ui.App]:
	a = ui.App()
	a.set_ui_callback(print)
	yield a

def boolexit(result: bool, error_code: int = 1) -> typing.NoReturn:
	if result:
		exit()
	else:
		exit(error_code)


def main(args_list: typing.Optional[typing.Sequence[str]] = None) -> None:
	BACKUP_PLAN = 'BACKUP_PLAN'
	p = argparse.ArgumentParser(prog=APP_NAME, description=__doc__ + HELP, formatter_class=argparse.RawTextHelpFormatter)
	p.add_argument('-H', '--help-config', action='store_true', help='show the help for the config file and exit')
	p.add_argument('-v', '--version', action='store_true', help='show the version number and exit')
	p.add_argument('-l', '--list-backup-plans', action='store_true')
	p.add_argument('-e', '--edit-backup-plan', metavar=BACKUP_PLAN)
	p.add_argument('-d', '--delete-backup-plan', metavar=BACKUP_PLAN)
	p.add_argument('-E', '--edit-config', action='store_true')
	p.add_argument('-D', '--delete-config', action='store_true')
	p.add_argument('--install-rifle', action='store_true', help='use ranger\'s file opener rifle to choose which application to use for opening a file')
	p.add_argument('src', nargs='?', help='the source directory')
	p.add_argument('dst', nargs='?', help='the destination directory')

	def assert_no_args(flag: str, suggestion: str) -> None:
		if args.src:
			print(f"{flag} does not take any arguments. Did you mean {suggestion}?", file=sys.stderr)
			exit(1)

	args = p.parse_args(args_list)
	if args.version:
		print_version()
		return
	if args.help_config:
		app = ui.App()
		app.print_help_config()
		return
	elif args.list_backup_plans:
		with tmpapp() as a:
			for fn in a.list_backup_plans():
				print(fn)
		return
	elif args.edit_backup_plan is not None:
		with tmpapp() as a:
			boolexit(a.edit_backup_plan(args.edit_backup_plan))
	elif args.delete_backup_plan is not None:
		with tmpapp() as a:
			boolexit(a.delete_backup_plan(args.delete_backup_plan))
	elif args.edit_config:
		assert_no_args('--edit-config', '--edit-backup-plan')
		with tmpapp() as a:
			boolexit(a.open_config())
	elif args.delete_config:
		assert_no_args('--delete-config', '--delete-backup-plan')
		with tmpapp() as a:
			boolexit(a.delete_config())
	elif args.install_rifle:
		# 'python' would use the system python, not the one from the venv
		# https://stackoverflow.com/a/749769
		# there are comments claiming sys.executable would not work "e.g. in an environment or if you have multiple python versions installed" and that `os.__file__` would be better.
		# But sys.executable works in a virtual environment as created by pipx and os.__file__ does not.
		subprocess.run([sys.executable, '-m', 'pip', 'install', 'ranger-fm'])
		return

	app = ui.App()
	app.load(args.src, args.dst)
	app.mainloop()


if __name__ == '__main__':
	main()
