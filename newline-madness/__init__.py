# -*- coding: utf-8 -*-
#
# __init__.py
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

from gi.repository import GObject, Gtk, Gedit
from .statuscombobox import StatusComboBox
from .utils import connect_handlers, disconnect_handlers, block_handlers, unblock_handlers

class NewlineMadnessPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = 'NewlineMadnessPlugin'

	window = GObject.property(type=Gedit.Window)

	LINE_ENDING_DATA = 'NewlineMadnessPluginLineEndingData'

	LINE_ENDINGS = {
		Gedit.DocumentNewlineType.LF: {
			'name': 'NewlineMadnessPluginToLF',
			'label': _("Unix/Linux")
		},
		Gedit.DocumentNewlineType.CR: {
			'name': 'NewlineMadnessPluginToCR',
			'label': _("Mac OS Classic")
		},
		Gedit.DocumentNewlineType.CR_LF: {
			'name': 'NewlineMadnessPluginToCRLF',
			'label': _("Windows")
		}
	}

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		window = self.window

		# Menu
		action_group = Gtk.ActionGroup('NewlineMadnessPluginActions')
		action_group.set_translation_domain('gedit')
		action = Gtk.Action('NewlineMadnessPluginMenu', _("Change Line Endings"), None, None)
		action_group.add_action(action)
		menu_action = action

		first_action = None
		for key, props in self.LINE_ENDINGS.items():
			label = props['label']
			action = Gtk.RadioAction(props['name'], label, _("Change the document to use %s line endings") % label, None, key)
			action_group.add_action_with_accel(action, None)

			if first_action is None:
				first_action = action
			else:
				action.join_group(first_action)

			connect_handlers(self, action, ('activate',), 'action')

		ui_str = """
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
			</ui>"""

		manager = window.get_ui_manager()
		manager.insert_action_group(action_group, -1)
		ui_id = manager.add_ui_from_string(ui_str)

		# Combo
		combo = StatusComboBox()
		combo.show()
		statusbar = window.get_statusbar()
		combo.clone_padding_from_gedit_status_combo_box(statusbar)
		statusbar.pack_end(combo, False, True, 0)
		statusbar.reorder_child(combo, 5)

		for key, props in self.LINE_ENDINGS.items():
			label = props['label']
			item = Gtk.MenuItem(label)
			setattr(item, self.LINE_ENDING_DATA, key)

			combo.add_item(item, label)

			item.show()

		connect_handlers(self, combo, ('changed',), 'combo')

		self._ui_id = ui_id
		self._menu_action = menu_action
		self._action_group = action_group
		self._combo = combo

		for doc in window.get_documents(): 
			self.on_window_tab_added(window, Gedit.Tab.get_from_document(doc))

		connect_handlers(self, window, ('active-tab-changed', 'active-tab-state-changed', 'tab-added', 'tab-removed'), 'window')

		if hasattr(Gedit.WindowState, 'SAVING_SESSION'):
			connect_handlers(self, window, ('notify::state',), 'window')

		self.do_update_state()

	def do_deactivate(self):
		window = self.window

		disconnect_handlers(self, window)

		for doc in window.get_documents(): 
			self.on_window_tab_removed(window, Gedit.Tab.get_from_document(doc))

		disconnect_handlers(self, self._combo)
		super(Gtk.Container, window.get_statusbar()).remove(self._combo)

		for action in self._action_group.list_actions():
			disconnect_handlers(self, action)

		manager = window.get_ui_manager()
		manager.remove_ui(self._ui_id)
		manager.remove_action_group(self._action_group)
		manager.ensure_update()

		self._ui_id = None
		self._menu_action = None
		self._action_group = None
		self._combo = None

	def do_update_state(self):
		self._set_sensitivity()
		self._update_ui()

	def on_window_active_tab_changed(self, window, tab):
		self._set_sensitivity()
		self._update_ui()

	def on_window_active_tab_state_changed(self, window):
		self._set_sensitivity()

	def on_window_tab_added(self, window, tab):
		connect_handlers(self, tab.get_document(), ('notify::newline-type',), 'doc')

	def on_window_tab_removed(self, window, tab):
		disconnect_handlers(self, tab.get_document())

	def on_window_notify_state(self, window, prop):
		self._set_sensitivity()

	def on_doc_notify_newline_type(self, doc, prop):
		self._update_ui()

	def on_action_activate(self, action):
		doc = self.window.get_active_document()
		if doc and action.get_active():
			self._set_document_newline(doc, action.get_current_value())

	def on_combo_changed(self, combo, item):
		doc = self.window.get_active_document()
		if doc:
			self._set_document_newline(doc, getattr(item, self.LINE_ENDING_DATA))

	def _set_sensitivity(self):
		window = self.window
		tab = window.get_active_tab()
		combo = self._combo
		sensitive = False

		if tab:
			# Gedit.WindowState.SAVING_SESSION was removed in gedit 3.8
			not_window_saving_session = (window.get_state() & Gedit.WindowState.SAVING_SESSION) == 0 if hasattr(Gedit.WindowState, 'SAVING_SESSION') else True
			tab_state_normal = tab.get_state() is Gedit.TabState.STATE_NORMAL
			tab_editable = tab.get_view().get_editable()

			sensitive = not_window_saving_session and tab_state_normal and tab_editable

		self._menu_action.set_sensitive(sensitive)
		combo.set_sensitive(sensitive)
		if tab:
			combo.show()
		else:
			combo.hide()

	def _update_ui(self):
		doc = self.window.get_active_document()

		if doc:
			newline = doc.get_property('newline-type')

			for key, props in self.LINE_ENDINGS.items():
				if key is newline:
					name = props['name']

			# Menu
			action_group = self._action_group
			actions = action_group.list_actions()

			# prevent recursion
			for action in actions:
				block_handlers(self, action)

			action = action_group.get_action(name)
			action.set_active(True)

			for action in actions:
				unblock_handlers(self, action)

			# Combo
			combo = self._combo

			for item in combo.get_items():
				if getattr(item, self.LINE_ENDING_DATA) == newline:
					block_handlers(self, combo)
					combo.set_item(item)
					unblock_handlers(self, combo)
					break

	def _set_document_newline(self, doc, newline):
		if doc:
			doc.set_property('newline-type', newline)
			doc.set_modified(True)
