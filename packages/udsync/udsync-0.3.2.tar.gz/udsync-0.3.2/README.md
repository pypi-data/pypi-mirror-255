An interactive urwid based directory synchronizer.
Similar to [Free File Sync](https://freefilesync.org/) but in a terminal and with the possibility to expand and collapse directories to keep the list of changes to a manageable size.

WARNING:
This software is *not* mature yet.
Use at your own risk.

usage:
```bash
udsync <sourcedir> <destinationdir>
udsync [<backupplan>]
```

# Installation

```
pipx install udsync
```

If you want to use [ranger](https://github.com/ranger/ranger)'s file opener *rifle* to open files:
```
udsync --install-rifle
```


# Comparing and Copying of Files

In order to safe time this program does not compare the content of a file but only it's size and modification time.
Depending on how you have copied your files before this may lead to many false positives.
`cp` for example sets the modification time to the time where the copy has been created.
So the modification time may differ even if the files are the same.
On the other hand some file managers (e.g. Gnome's Files 3.38.2 and ranger 1.9.3) copy the modification time when copying a file.

This program uses `shutil.copy2` which copies the modification time but not all file meta data can be copied.
Please see the official [Python documentation](https://docs.python.org/3/library/shutil.html) for more information.

Different file systems can have different resolutions for time stamps.
ext4 has a resolution of nanoseconds [[Wikipedia](https://en.wikipedia.org/wiki/Ext4)] while FAT has a resolution of 2 seconds for the modification time [[Wikipedia](https://en.wikipedia.org/wiki/Fat32)].
Therefore this program allows a difference of up to 2 seconds for two files to be considered the same.
You can change this in the config file with `set diff.model.time-precision = <number-of-seconds>`.

Instead of copying all files again this program offers the feature to update the modification times by pressing F12 (or whatever key you bind to `sync time stamps`).

You can also choose to change the setting `diff.model.compare-mode`.
The following values are allowed for it:

- `shallow`: The default setting described above
- `mixed`: Two files are taken to be identical if file type, size and modification time are identical. Compare the content if the modification time differs. This uses [`filecmp.cmp(shallow=True)`](https://docs.python.org/3/library/filecmp.html#filecmp.cmp).
- `deep`: Compare the content except if the file size differs. This uses [`filecmp.cmp(shallow=False)`](https://docs.python.org/3/library/filecmp.html#filecmp.cmp).


# Config

You can open the config file with `udsync --edit-config` or inside of udsync by pressing F4 (or whatever key you bind to `config`).
You can choose the editor to be used with the environment variable `EDITOR`.
If the config file does not exist yet a template will be created with all possible settings and comments explaining the allowed values.
The syntax of the config file is explained in the in-app help which can be opened with F4 (or whatever key you bind to `help config`).
A list of all commands which can be bound to keys can be opened with F3 (`help commands`).
A list off all defined keyboard shortcuts can be opened with F2 (`help key-mappings`).

Each backup plan has it's own config file which is loaded after the normal config file.
Most importantly it contains the `path.src` and `path.dst` settings which are not contained in the normal config file.
But it can contain all other commands which can be used in the normal config file, too.
The config file of a backup plan can be opened with `udsync -e <backup-plan-name>`.


# Actions

This program compares two directories (in the following called source and destination) and displays a list of changes that it will perform in order to make the two directories the same.
By default the destination will be changed to match the source but the user can choose to toggle the direction of an action (by pressing `u`, `<` or `>`) or ignore it (by pressing space).

Special actions which do not perform any changes:

- ` = ` none:
	Both sides are the same.
	This is a special case.
	The direction cannot be toggled and it cannot be ignored.
	These nodes are not displayed by default but your can toggle that with Ctrl+H.
- ` | ` ignore:
	The two sides are different but the differences are ignored.
	Neither side will be changed during the synchronization.
	The direction of this action cannot be toggled.
	You can change any of the following actions to ignore by pressing space.
- ` ! ` error:
	The two sides cannot be compared or synchronized.
	Focus this node in order to see the reason in the status at the bottom of the window.
	Neither side will be changed during the synchronization.
	If this was caused by missing read permissions toggling the direction of this action has no effect.
	If this was caused by the file system to write to not supporting symlinks toggling the direction of this action will change this to a different action which will delete or overwrite the symlink, e.g. *undo-create* if src is the link and dst does not exist.
	If this was caused by a broken symlink toggling the direction may or may not change this action depending on whether the other side is a broken symlink, too, or not.

Actions where either the source or the destination are missing:

- ` >+` create:
	The source exists, the destination does not.
	The source can be any type (directory, file, link).
	The source will be copied to the destination during synchronization.
	Toggling the direction will change this to *undo-create*.
- ` >-` delete:
	The destination exists, the source does not.
	The destination can be any type (directory, file, link).
	The destination will be deleted during synchronization.
	Toggling the direction will change this to *undo-delete*.
- `-< ` undo-create:
	The source exists, the destination does not.
	The source can be any type (directory, file, link).
	The source will be deleted during synchronization.
	Toggling the direction will change this to *create*.
- `+< ` undo-delete:
	The destination exists, the source does not.
	The destination can be any type (directory, file, link).
	The destination will be copied to the source during synchronization.
	Toggling the direction will change this to *delete*.

Actions where both source and destination are existing:

- ` > ` update:
	Both sides are existing but are different.
	Both sides are either files or links or one is a file and the other a link.
	The source is newer than the destination (according to the last modification timestamp).
	The destination file (the older file) will be overwritten during synchronization.
	Toggling the direction will change this to *undo-update*.
- ` >!` downgrade:
	Both sides are existing but are different.
	Both sides are either files or links or one is a file and the other a link.
	The destination is newer than the source (according to the last modification timestamp).
	The destination file (the newer file) will be overwritten during synchronization.
	Toggling the direction will change this to *undo-downgrade*.
- ` > ` dir-change-destination:
	Both sides are existing directories but at least one of their children differs.
	None of the children has an action which changes the source.
	This may overwrite newer files in the destionation.
	Toggling the direction will change this to *dir-change-source*.

- `!< ` undo-update:
	Both sides are existing but are different.
	Both sides are either files or links or one is a file and the other a link.
	The source is newer than the destination (according to the last modification timestamp).
	The source file (the newer file) will be overwritten during synchronization.
	Toggling the direction will change this to *update*.
- ` < ` undo-downgrade:
	Both sides are existing but are different.
	Both sides are either files or links or one is a file and the other a link.
	The destination is newer than the source (according to the last modification timestamp).
	The source file (the older file) will be overwritten during synchronization.
	Toggling the direction will change this to *downgrade*.
- ` < ` dir-change-source:
	Both sides are existing directories but at least one of their children differs.
	None of the children has an action which changes the destination.
	This may overwrite newer files in the source.
	Toggling the direction will change this to *dir-change-destination*.

- `> <` dir-change-both:
	Both sides are existing directories but at least one of their children differs.
	Changes will be performed in both destination and source, or one of the children has action *error*.
	This may overwrite newer files.
	Toggling the direction will change this to either *dir-change-destination* or *dir-change-source* if no child has action *error*.

- ` >t` change-destination-type:
	One side is a directory and the other side is a file or link.
	The destination will be overwritten during synchronization.
	This may overwrite newer files in the destination.
	Toggling the direction will change this to *change-source-type*.
- `t< ` change-source-type:
	One side is a directory and the other side is a file or link.
	The source will be overwritten during synchronization.
	This may overwrite newer files in the source.
	Toggling the direction will change this to *change-destination-type*.

- `->+` create-directory-but-delete-some-children:
	The source is a directory and the destination does not exist.
	In contrast to the *create* action at least one child will be deleted on the source side.
	The deleted child(ren) are *not* copied to the destination.
	Toggling the direction will change this to *undo-create*.
- `+<-` undo-delete-directory-but-delete-some-children:
	The destination is a directory and the source does not exist.
	In contrast to the *undo-delete* action at least one child will be removed on the destination side during synchronization.
	The deleted child(ren) are *not* copied to the source.
	Toggling the direction will change this to *delete*.
- `->t` change-destination-type-but-delete-some-children:
	The source is a directory and the destination is a file or link.
	In contrast to the *change-destination-type* action at least one child will be removed on the source side during synchronization.
	The deleted child(ren) are *not* copied to the destination.
	Toggling the direction will change this to *change-source-type*.
- `t<-` change-source-type-but-delete-some-children:
	The source is a file or link and the destination is a directory.
	In contrast to the *change-source-type* action at least one child will be removed on the destination side during synchronization.
	The deleted child(ren) are *not* copied to the source.
	Toggling the direction will change this to *change-destination-type*.

If you don't like any of the action symbols you can change them in the config file with `set diff.action-symbols.<action name> = '<new symbol>'`.
There you can also change the default direction for certain conditions with `set diff.model.default-direction.<state> = <direction>`.
When you open the config file for the first time (by pressing `p`) a new template will be created and you will see which values can be given.


# Opening files

udsync offers the feature to open the focused file by pressing o.
The program used to open the file can be changed with the settings `cmd.open` and `mime-type-text-re` (see [Config](#Config)).

By default, if [ranger](https://github.com/ranger/ranger) is installed as a python package in the same python environment like udsync, rifle (ranger's file opener) is used.
Otherwise [xdg-open](https://www.freedesktop.org/wiki/Software/xdg-utils/) is used.

If you have installed udsync in a virtual environment (e.g. via pipx) and want to use rifle you need to install ranger in the virtual environment.
You can do this with `udsync --install-rifle`.

If you want to see which command is executed to open a file you can `set status.level = debug`.


# Fonts

This program is using special symbols to distinguish between files, directories and links.
If these symbols don't show up correctly on your system you have two options:

1. Use a font containing these symbols, e.g. [Noto fonts](https://en.wikipedia.org/wiki/Noto_fonts).

   ```bash
   pacman -S noto-fonts
   apt install fonts-noto-core
   ```

   If you are using [kitty](https://sw.kovidgoyal.net/kitty/) you don't even need to change your default font.
   Just restart kitty and it will start using the font for characters not contained in your default font automatically.

   According to the [Arch Wiki](https://wiki.archlinux.org/title/Font#List_installed_fonts_for_a_particular_Unicode_character) you can list all installed fonts containing (one of) the symbols with `fc-match -s monospace:charset=1f5c0`.
   However, I am under the impression that this lists more than just the fonts containing the symbol.
   All fonts which are compatible with kitty can be printed with `kitty +list-fonts`.
   These two commands can be combined to `grep -Ff <(fc-match -s monospace:charset=1f5c0 | sed -E 's/([^:]*): "([^"]*)" "([^"]*)"/\2/') <(kitty +list-fonts)`.

   If you are curious which fonts kitty is using start it with `kitty --debug-font-fallback`.

2. Change the symbols. Open the config file with `udsync --edit-config` and change the following settings:

   ```
   set diff.symbol.deleted = '🗙 '
   set diff.symbol.directory.closed = '🗀 '
   set diff.symbol.directory.expanded = '🗁 '
   set diff.symbol.file = '🗎 '
   set diff.symbol.link = '🠦 '
   
   set diff.symbol.destination = '🖴 '
   set diff.symbol.source = '🖳 '
   ```


# Known Bugs

- When comparing a case sensitive and a case insensitive file system and there are two identical items but one is in upper case and one is in lower case then it is displayed as missing on one side because the version on the case sensitive fs is found on the case insensitive fs and therefore not displayed but the version on the case insensitive fs is not found on the case sensitive fs. The expected behavior would be that both versions are displayed as missing on the other side (`file a   >+   x` and `x   >-   File A`).


---

# Running the automated tests

I am using [mypy](https://www.mypy-lang.org/) for static type checking and [pytest](https://docs.pytest.org/en/latest/) for dynamic testing.
[tox](https://tox.wiki/en/latest/) creates a virtual environment and installs all dependencies for you.
You can install tox with [pipx](https://pypa.github.io/pipx/) (`pipx install tox`).

```bash
$ tox
```

In order to make tox work without an internet connection install [devpi](https://devpi.net/docs/devpi/devpi/stable/%2Bd/index.html):

```bash
$ pipx install devpi-server
$ devpi-init
$ devpi-gen-config
$ su
# cp gen-config/devpi.service /etc/systemd/system/
# systemctl start devpi.service
# systemctl enable devpi.service
```

and add the following line to your bashrc:

```bash
export PIP_INDEX_URL=http://localhost:3141/root/pypi/+simple/
```
