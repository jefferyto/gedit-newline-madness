# -*- coding: utf-8 -*-
#
# Newline Madness, a plugin for gedit
# Change newline type for the current document
# v0.2.0
#
# Copyright (C) 2010-2011 Jeffery To <jeffery.to@gmail.com>
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

from gi.repository import GObject, Gtk, Gedit
from gettext import gettext as _

ui_str = '''
<ui>
	<menubar name="MenuBar">
		<menu name="EditMenu" action="Edit">
			<placeholder name="EditOps_6">
				<menu name="NewlineMadnessPluginMenu" action="NewlineMadnessPluginMenu">
					<menuitem name="NewlineMadnessPluginToLF" action="NewlineMadnessPluginToLF" />
					<menuitem name="NewlineMadnessPluginToCR" action="NewlineMadnessPluginToCR" />
					<menuitem name="NewlineMadnessPluginToCRLF" action="NewlineMadnessPluginToCRLF" />
				</menu>
			</placeholder>
		</menu>
	</menubar>
</ui>
'''

class NewlineMadnessPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = 'NewlineMadnessPlugin'

	window = GObject.property(type=Gedit.Window)

	HANDLER_IDS = 'NewlineMadnessPluginHandlerIds'

	LINE_ENDINGS = {
		Gedit.DocumentNewlineType.LF: {
			'name': 'NewlineMadnessPluginToLF',
			'label': _('Unix/Linux'),
			'tooltip': _('Change the document to use Unix/Linux line endings')
		},
		Gedit.DocumentNewlineType.CR: {
			'name': 'NewlineMadnessPluginToCR',
			'label': _('Mac OS Classic'),
			'tooltip': _('Change the document to use Mac OS Classic line endings')
		},
		Gedit.DocumentNewlineType.CR_LF: {
			'name': 'NewlineMadnessPluginToCRLF',
			'label': _('Windows'),
			'tooltip': _('Change the document to use Windows line endings')
		}
	}



	# Plugin interface

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		window = self.window

		# Set up menu
		menu_action_group = Gtk.ActionGroup('NewlineMadnessPluginMenuActions')
		action = Gtk.Action('NewlineMadnessPluginMenu', _('Change Line Endings'), None, None)
		menu_action_group.add_action(action)

		newline_action_group = Gtk.ActionGroup('NewlineMadnessPluginNewlineActions')
		first_action = None
		for key, props in self.LINE_ENDINGS.iteritems():
			action = Gtk.RadioAction(props['name'], props['label'], props['tooltip'], None, key)
			newline_action_group.add_action_with_accel(action, None)

			if first_action is None:
				first_action = action
			else:
				action.join_group(first_action)

			self.connect_handlers(action, ('activate',), 'menu_action')

		manager = window.get_ui_manager()
		manager.insert_action_group(menu_action_group, -1)
		manager.insert_action_group(newline_action_group, -1)
		ui_id = manager.add_ui_from_string(ui_str)

		# Prime the statusbar
		statusbar = window.get_statusbar()
		sb_frame = Gtk.Frame()
		sb_label = Gtk.Label()
		sb_frame.add(sb_label)
		statusbar.pack_end(sb_frame, False, False, 0)
		sb_frame.show_all()

		self._ui_id = ui_id
		self._sb_frame = sb_frame
		self._sb_label = sb_label
		self._menu_action_group = menu_action_group
		self._newline_action_group = newline_action_group

		for doc in window.get_documents(): 
			self.window_tab_added(window, Gedit.Tab.get_from_document(doc))

		self.connect_handlers(window, ('active-tab-changed', 'active-tab-state-changed', 'tab-added', 'tab-removed'), 'window')
		self.connect_handlers(window, ('notify::state',), self.sync_window_state)

		self.do_update_state()

	def do_deactivate(self):
		window = self.window

		self.disconnect_handlers(window)

		for doc in window.get_documents(): 
			self.window_tab_removed(window, Gedit.Tab.get_from_document(doc))

		for action in self._newline_action_group.list_actions():
			self.disconnect_handlers(action)

		manager = window.get_ui_manager()
		manager.remove_ui(self._ui_id)
		manager.remove_action_group(self._newline_action_group)
		manager.remove_action_group(self._menu_action_group)
		manager.ensure_update()

		super(Gtk.Container, window.get_statusbar()).remove(self._sb_frame)

		self._ui_id = None
		self._sb_frame = None
		self._sb_label = None
		self._menu_action_group = None
		self._newline_action_group = None

	def do_update_state(self):
		self.set_sensitivity_according_to_window_state()
		self.set_sensitivity_according_to_tab()
		self.update_newline_menu()
		self.update_status(self.window.get_active_document(), None)



	# Callbacks

	def window_active_tab_changed(self, window, tab):
		self.set_sensitivity_according_to_tab()
		self.update_newline_menu()

	def window_active_tab_state_changed(self, window):
		self.set_sensitivity_according_to_tab()

	def window_tab_added(self, window, tab):
		doc = tab.get_document()
		self.connect_handlers(doc, ('notify::newline-type',), self.sync_newline_menu)
		self.connect_handlers(doc, ('notify::newline-type',), self.update_status) # XXX

	def window_tab_removed(self, window, tab):
		self.disconnect_handlers(tab.get_document())

	def sync_window_state(self, window, pspec):
		self.set_sensitivity_according_to_window_state()

	def sync_newline_menu(self, doc, pspec):
		self.update_newline_menu()

	def menu_action_activate(self, action):
		doc = self.window.get_active_document()
		if doc and action.get_active():
			self.set_document_newline(doc, action.get_current_value())



	# Doers

	def set_sensitivity_according_to_window_state(self):
		window = self.window
		action_group = self._menu_action_group
		sensitive = action_group.get_sensitive()

		if (window.get_state() & Gedit.WindowState.SAVING_SESSION) != 0:
			if sensitive:
				action_group.set_sensitive(False)
		else:
			if not sensitive:
				action_group.set_sensitive(window.get_active_tab() is not None)

	def set_sensitivity_according_to_tab(self):
		tab = self.window.get_active_tab()
		state_normal = tab is not None and tab.get_state() is Gedit.TabState.STATE_NORMAL
		editable = tab is not None and tab.get_view().get_editable()
		action = self._menu_action_group.get_action('NewlineMadnessPluginMenu')
		action.set_sensitive(state_normal and editable)

	def update_newline_menu(self):
		doc = self.window.get_active_document()

		if doc:
			action_group = self._newline_action_group
			actions = action_group.list_actions()
			newline = doc.get_property('newline-type')

			for key, props in self.LINE_ENDINGS.iteritems():
				if key is newline:
					name = props['name']

			# prevent recursion
			for action in actions:
				self.block_handlers(action)

			action = action_group.get_action(name)
			action.set_active(True)

			for action in actions:
				self.unblock_handlers(action)

	def update_status(self, doc, pspec):
		sb_label = self._sb_label

		if doc:
			nl = doc.get_property('newline-type')

			if nl == Gedit.DocumentNewlineType.LF:
				sb_label.set_text(_('Unix/Linux'))
			if nl == Gedit.DocumentNewlineType.CR:
				sb_label.set_text(_('Mac OS Classic'))
			if nl == Gedit.DocumentNewlineType.CR_LF:
				sb_label.set_text(_('Windows'))

			sb_label.show()

		else:
			sb_label.hide()

	def set_document_newline(self, doc, newline):
		if doc:
			doc.set_property('newline-type', newline)
			doc.set_modified(True)



	# Utilities

	def connect_handlers(self, obj, signals, m, *args):
		HANDLER_IDS = self.HANDLER_IDS
		l_ids = getattr(obj, HANDLER_IDS) if hasattr(obj, HANDLER_IDS) else []

		for signal in signals:
			if type(m).__name__ == 'str':
				method = getattr(self, m + '_' + signal.replace('-', '_'))
			else:
				method = m
			l_ids.append(obj.connect(signal, method, *args))

		setattr(obj, HANDLER_IDS, l_ids)

	def disconnect_handlers(self, obj):
		HANDLER_IDS = self.HANDLER_IDS
		if hasattr(obj, HANDLER_IDS):
			for l_id in getattr(obj, HANDLER_IDS):
				obj.disconnect(l_id)

			delattr(obj, HANDLER_IDS)

	def block_handlers(self, obj):
		HANDLER_IDS = self.HANDLER_IDS
		if hasattr(obj, HANDLER_IDS):
			for l_id in getattr(obj, HANDLER_IDS):
				obj.handler_block(l_id)

	def unblock_handlers(self, obj):
		HANDLER_IDS = self.HANDLER_IDS
		if hasattr(obj, HANDLER_IDS):
			for l_id in getattr(obj, HANDLER_IDS):
				obj.handler_unblock(l_id)

