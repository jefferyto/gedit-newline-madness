# Newline Madness, a plugin for gedit #

Change newline type for the current document  
<https://github.com/jefferyto/gedit-newline-madness>  
v0.3.0

All bug reports, feature requests and miscellaneous comments are
welcome at <https://github.com/jefferyto/gedit-newline-madness/issues>.

## Requirements ##

v0.2.0 and higher requires at least gedit 3.2. (Untested with gedit
3.0; it *may* work :-) )

gedit 2 users should use [v0.1.0][] (requires at least gedit 2.29.5).

## Installation ##

1.  Download the source code (as [zip][] or [tar.gz][]) and extract.
2.  Copy `newline-madness.plugin` and the `newline-madness` folder into
    `~/.local/share/gedit/plugins` (create if it does not exist).
3.  Restart gedit, select `Edit > Preferences`, and enable the plugin
    in the `Plugins` tab.

## Usage ##

To select a newline type for the current document, either:

*   Select `Edit > Change Line Endings`; or
*   Click on the line ending selector in the statusbar, between the tab
    width selector and cursor position information.

Note that changing the newline type cannot be undone with `Undo` (yet).

## Credits ##

Based in part on:

*   [Auto Tab][] by Kristoffer Lundén and Lars Uebernickel
*   The gedit statusbar combo box widget

## License ##

Copyright &copy; 2010-2012 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[v0.1.0]: https://github.com/jefferyto/gedit-newline-madness/zipball/v0.1.0
[zip]: https://github.com/jefferyto/gedit-newline-madness/zipball/master
[tar.gz]: https://github.com/jefferyto/gedit-newline-madness/tarball/master
[Auto Tab]: http://code.google.com/p/gedit-autotab/
