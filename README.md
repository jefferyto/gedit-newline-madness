# Newline Madness, a plugin for gedit #

Change newline type for the current document  
<https://github.com/jefferyto/gedit-newline-madness>  
v0.3.3

All bug reports, feature requests and miscellaneous comments are welcome
at the [project issue tracker][].

## Requirements ##

v0.2.0 and higher requires gedit 3. The last version compatible with
gedit 2 (2.29.5 and higher) is [v0.1.0][].

## Installation ##

1.  Download the source code (as [zip][] or [tar.gz][]) and extract.
2.  Copy the `newline-madness` folder and the appropriate `.plugin` file
    into `~/.local/share/gedit/plugins` (create if it does not exist):
    *   For gedit 3.6 and earlier, copy `newline-madness.plugin.python2`
        and rename to `newline-madness.plugin`.
    *   For gedit 3.8 and later, copy `newline-madness.plugin`.
3.  Restart gedit, select **Edit > Preferences** (or
    **gedit > Preferences** on Mac), and enable the plugin in the
    **Plugins** tab.

## Usage ##

To select a newline type for the current document, either:

*   Select **Edit > Change Line Endings**; or
*   Click on the line ending selector in the statusbar, between the tab
    width selector and cursor position information.

Note that changing the newline type cannot be undone with `Undo` (yet).

## Development ##

The code in `newline-madness/utils` comes from [python-gtk-utils][];
changes should ideally be contributed to that project, then pulled back
into this one with `git subtree pull`.

## Credits ##

Based in part on:

*   [Auto Tab][] by Kristoffer Lundén and Lars Uebernickel
*   The gedit statusbar combo box widget

## License ##

Copyright &copy; 2010-2013 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[project issue tracker]: https://github.com/jefferyto/gedit-newline-madness/issues
[zip]: https://github.com/jefferyto/gedit-newline-madness/archive/master.zip
[tar.gz]: https://github.com/jefferyto/gedit-newline-madness/archive/master.tar.gz
[v0.1.0]: https://github.com/jefferyto/gedit-newline-madness/archive/v0.1.0.zip
[python-gtk-utils]: https://github.com/jefferyto/python-gtk-utils
[Auto Tab]: http://code.google.com/p/gedit-autotab/
