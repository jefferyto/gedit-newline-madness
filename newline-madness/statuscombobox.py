# -*- coding: utf-8 -*-
#
# statuscombobox.py
# This file is part of Newline Madness, a plugin for gedit
#
# Copyright (C) 2010-2013 Jeffery To <jeffery.to@gmail.com>
# https://github.com/jefferyto/gedit-newline-madness
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is a shameless copy of GeditStatusComboBox from gedit
# All credit should go the to gedit team :-)

from gi.repository import GObject, Gtk, Gdk

class StatusComboBox(Gtk.EventBox):
	__gtype_name__ = 'StatusComboBox'

	__gproperties__ = {
		'label': (str, 'LABEL', 'The Label', None, GObject.PARAM_READWRITE)
	}

	__gsignals__ = {
		'destroy': 'override',
		'changed': (GObject.SIGNAL_RUN_LAST, None, (object,))
	}

	COMBO_BOX_TEXT_DATA = 'StatusComboBoxTextData'

	_css = None

	def __init__(self, label=None):
		super(StatusComboBox, self).__init__()

		if not StatusComboBox._css:
			style = '''
* {
-GtkButton-default-border : 0;
-GtkButton-default-outside-border : 0;
-GtkButton-inner-border: 0;
-GtkWidget-focus-line-width : 0;
-GtkWidget-focus-padding : 0;
padding: 1px 8px 2px 4px;
}
'''
			StatusComboBox._css = Gtk.CssProvider()
			StatusComboBox._css.load_from_data(style)

		self.set_visible_window(True)

		self._frame = Gtk.Frame()
		self._frame.show()

		self._button = Gtk.ToggleButton()
		self._button.set_relief(Gtk.ReliefStyle.NONE)
		self._button.show()

		self.__set_shadow_type()

		self._hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, 3)
		self._hbox.show()

		self.add(self._frame)
		self._frame.add(self._button)
		self._button.add(self._hbox)

		self._label = Gtk.Label('')
		self._label.show()

		self._label.set_single_line_mode(True)
		self._label.set_halign(Gtk.Align.START)

		self._hbox.pack_start(self._label, False, True, 0)

		self._item = Gtk.Label('')
		self._item.show()

		self._item.set_single_line_mode(True)
		self._item.set_halign(Gtk.Align.START)

		self._hbox.pack_start(self._item, True, True, 0)

		try:
			self._arrow = Gtk.Arrow(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
		except TypeError:
			self._arrow = Gtk.Arrow()
			self._arrow.set(Gtk.ArrowType.DOWN, Gtk.ShadowType.NONE)
		self._arrow.show()

		self._hbox.pack_start(self._arrow, False, True, 0)

		self._padding = None

		self._menu = Gtk.Menu()
		self._menu.attach_to_widget(self, self.__menu_detached)

		self._button.connect('button-press-event', self.__button_press_event)
		self._button.connect('key-press-event', self.__key_press_event)
		self._menu.connect('deactivate', self.__menu_deactivate)

		# make it as small as possible
		self._button.get_style_context().add_provider(self._css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self._frame.get_style_context().add_provider(self._css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self._current_item = None

		self.set_label(label)

	def do_get_property(self, prop):
		if prop.name == 'label':
			return self.get_label()
		else:
			raise AttributeError, 'unknown property %s' % prop.name

	def do_set_property(self, prop, value):
		if prop.name == 'label':
			self.set_label(value)
		else:
			raise AttributeError, 'unknown property %s' % prop.name

	def do_destroy(self):
		if self._menu:
			self._menu.disconnect_by_func(self.__menu_deactivate)
			self._menu.detach()

		self._frame = None
		self._button = None
		self._hbox = None
		self._label = None
		self._item = None
		self._arrow = None
		self._padding = None
		self._menu = None
		self._current_item = None

		super(StatusComboBox, self).do_destroy()

	def do_changed(self, item):
		text = getattr(item, self.COMBO_BOX_TEXT_DATA)
		if text:
			self._item.set_markup(text)
			self._current_item = item

	def __menu_deactivate(self, menu):
		self._button.set_active(False)

	def __menu_position_func(self, menu, data):
		request = menu.get_preferred_size()[0]

		# get the origin...
		x, y = self.get_window().get_origin()[1:]

		# make the menu as wide as the widget
		allocation = self.get_allocation()
		if request.width < allocation.width:
			menu.set_size_request(allocation.width, -1)

		# position it above the widget
		y -= request.height

		return x, y, False

	def __show_menu(self, button, time):
		request = self._menu.get_preferred_size()[0]

		# do something relative to our own height here, maybe we can do better
		allocation = self.get_allocation()
		max_height = allocation.height * 20

		if request.height > max_height:
			self._menu.set_size_request(-1, max_height)
			self._menu.get_toplevel().set_size_request(-1, max_height)

		self._menu.popup(None, None, self.__menu_position_func, None, button, time)

		self._button.set_active(True)

		if self._current_item:
			self._menu.select_item(self._current_item)

	@staticmethod
	def __menu_detached(widget, menu):
		if widget._menu != menu:
			return

		widget._menu = None

	def __button_press_event(self, button, event):
		if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
			self.__show_menu(event.button, event.time)
			return True

		return False

	def __key_press_event(self, button, event):
		if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_ISO_Enter or event.keyval == Gdk.KEY_KP_Enter or event.keyval == Gdk.KEY_space or event.keyval == Gdk.KEY_KP_Space:
			self.__show_menu(0, event.time)
			return True

		return False

	def __set_shadow_type(self):
		# This is a hack needed to use the shadow type of a statusbar
		statusbar = Gtk.Statusbar()
		context = statusbar.get_style_context()

		# I guess this counts as "documentation"?
		# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=636620
		shadow_type = GObject.Value()
		shadow_type.init(Gtk.ShadowType)
		context.get_style_property('shadow-type', shadow_type)
		self._frame.set_shadow_type(shadow_type.get_enum())

	# public functions

	def set_label(self, label):
		self._label.set_markup('  ' + label + ': ' if label is not None else '  ')

	def get_label(self):
		return self._label.get_label()

	def __item_activated(self, item):
		self.set_item(item)

	def add_item(self, item, text):
		if not isinstance(item, Gtk.MenuItem):
			return

		self._menu.append(item)

		self.set_item_text(item, text)
		item.connect('activate', self.__item_activated)

	def remove_item(self, item):
		if not isinstance(item, Gtk.MenuItem):
			return

		self._menu.remove(item)

	def get_items(self):
		return self._menu.get_children()

	def get_item_text(self, item):
		if not isinstance(item, Gtk.MenuItem):
			return None

		return getattr(item, self.COMBO_BOX_TEXT_DATA)

	def set_item_text(self, item, text):
		if not isinstance(item, Gtk.MenuItem):
			return

		setattr(item, self.COMBO_BOX_TEXT_DATA, text)

	def set_item(self, item):
		if not isinstance(item, Gtk.MenuItem):
			return

		self.emit('changed', item)

	def get_item_label(self):
		return self._item

	# hack /hack/ HACK
	def clone_padding_from_gedit_status_combo_box(self, parent):
		frame = None
		for combo in parent.get_children():
			if combo.__gtype__.name == 'GeditStatusComboBox':
				for child in combo.get_children():
					if isinstance(child, Gtk.Frame):
						frame = child
						break
				if frame:
					break

		if frame:
			self.remove_padding_from_gedit_status_combo_box()

			padding = frame.get_style_context().get_padding(Gtk.StateType.NORMAL)
			css_str = '* { padding: %dpx %dpx %dpx %dpx; }' % (padding.top, padding.right, padding.bottom, padding.left)
			css = Gtk.CssProvider()
			css.load_from_data(css_str)

			self._button.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
			self._frame.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

			self._padding = css

	def remove_padding_from_gedit_status_combo_box(self):
		css = self._padding
		if css:
			self._button.get_style_context().remove_provider(css)
			self._frame.get_style_context().remove_provider(css)
			self._padding = None

