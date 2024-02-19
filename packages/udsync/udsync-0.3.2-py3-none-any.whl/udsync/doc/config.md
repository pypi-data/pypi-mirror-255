The config file can be used to set settings and map keys to commands.

# Settings
The set command supports two different syntaxes:

	set key1=val1 [key2=val2 ...]
	set key [=] val

The first (vim-like) syntax allows to set several settings at once.
Keys and values are separated by an equals sign and no spaces are allowed between the key and it's value.

The second syntax allows to add spaces and align the values but you can set only one setting at a time.
The equals sign is optional. If the equal sign is given spaces must be on both sides of it.

When you open the config file for the first time using `config` the current settings and key mappings are written to the new file.
Refer to this file to see which keys are supported and what kind of values they accept.
By default all lines are commented out, if you want to change a setting you need to comment in that line.

Some keys support several values.
For example %path.src% and %path.dst% can be set to different values in different setting groups.
This allows to compare/sync several directories at the same time.

To start a new settings group give it's name in square brackets on a separate line:

	[my new settings group]

The name of the group is pretty much irrelevant. It is not displayed in the UI.
The only thing that's important is that it must be different from the name of other setting groups.
If two setting groups have the same name they are the same group and setting a setting a second time will overwrite it's previous value.

The name of a settings group must not contain square brackets.

Trying to set a setting which does not support multiple values in a settings group other than the default group "general" is an error.


# Mappings
You can change key mappings with the following commands:

	map [context] key command
	unmap [context] key
	mapclear [context]

`map` assigns a command to a key. If the key was already defined the previous definition is overwritten.

`unmap` or `unm` for short clears the definition of a key without assigning a new command to the key.

`mapclear` or `mapc` for short deletes all definitions of all keys.

Each of these three commands takes an optional context argument to limit the effect of the command.
The context is a comma separated list of the widget types listed below.
If you want to apply the effect to all widgets you can leave out the context or explicitly set it to `all`.
- {map_names}

The possible commands depend on the context.
For a list of all possible commands for each context see `help commands`.

## Key
key is a sequence of one or more keys to be pressed in order to run cmd.
Each of these keys is generally specified in the same way as urwid passes them to keypress.
Exceptions are the three keys SPACE, LESS and GREATER (see the examples below).
Key representations longer than one character are wrapped in angular brackets.
Keys to be pressed at the same time are treated like one key, i.e. the keys are placed in the same pair of angular brackets.
Keys to be pressed after one another are concatenated without a separator.

Some key combinations are intercepted by the terminal to insert control characters.
https://github.com/urwid/urwid/issues/140

Example key combinations (pressed at the same time):
  -------------------------------------
  | input          | key              |
  -------------------------------------
  | H              | h                |
  | SHIFT+H        | H                |
  | ENTER          | <enter>          |
  | TAB            | <tab>            |
  | UP             | <up>             |
  | PAGE DOWN      | <page down>      |
  | F5             | <f5>             |
  | SHIFT+F5       | <shift f5>       |
  | CTRL+SHIFT+F5  | <shift ctrl f5>  |
  | ALT+J          | <meta j>         |
  -------------------------------------
  | SPACE          | <space>          |
  | <              | <less>           |
  | >              | <greater>        |
  -------------------------------------

  see also http://urwid.org/manual/userinput.html#keyboard-input

Example key combinations intercepted by the terminal:
  ---------------------------------------------
  | input          | key/effect               |
  ---------------------------------------------
  | CTRL+I         | <tab>                    |
  | CTRL+SPACE     | <<0>>                    |
  ---------------------------------------------
  | CTRL+C         | close                    |
  | CTRL+S         | stop updating screen     |
  | CTRL+Q         | resume updating screen   |
  ---------------------------------------------

  https://github.com/urwid/urwid/issues/140


# Comments
Empty lines and lines starting with either a `"` (like in vim) or a `#` (like in a POSIX shell) are ignored.

Comments at the end of a line can only start with a `#`.

# Quotes
Lines are split using `shlex.split(ln, comments=True)`.
Therefore quoting works similar to a POSIX shell.

If an argument contains spaces it must be wrapped in quotes.
In this config file there is no difference between single and double quotes.

# Indentation
All white space at the beginning and end of a line is stripped so you can indent the lines however you want.
