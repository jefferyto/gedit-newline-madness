# -*- coding: utf-8 -*-
#
# Newline Madness, a plugin for gedit
# Change newline type for the current document
# v0.1.0
#
# Requires gedit 2.29.5 or above
#
# Based in part on Auto Tab by Kristoffer Lundén and Lars Uebernickel:
# http://code.google.com/p/gedit-autotab/
#
# Copyright (C) 2010 Jeffery To <jeffery.to@gmail.com>
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

import gedit
import gtk

from gettext import gettext as _

ui_str = """<ui>
	<menubar name="MenuBar">
		<menu name="EditMenu" action="Edit">
			<placeholder name="EditOps_4">
				<separator />
				<menu name="NewlineMadnessPluginMenu" action="NewlineMadnessPluginMenu">
					<menuitem name="NewlineMadnessPluginToLF" action="NewlineMadnessPluginToLF" />
					<menuitem name="NewlineMadnessPluginToCR" action="NewlineMadnessPluginToCR" />
					<menuitem name="NewlineMadnessPluginToCRLF" action="NewlineMadnessPluginToCRLF" />
				</menu>
			</placeholder>
		</menu>
	</menubar>
</ui>
"""

class NewlineMadnessWindowHelper:
	NEWLINE_TYPE_LF = 0
	NEWLINE_TYPE_CR = 1
	NEWLINE_TYPE_CRLF = 2

	def __init__(self, plugin, window):
		# Set up menu
		action_group = gtk.ActionGroup("NewlineMadnessPluginActions")
		action_group.add_actions([
			("NewlineMadnessPluginMenu",
				None,
				_("Change Line Endings"),
				None,
				None,
				None),
			("NewlineMadnessPluginToLF",
				None,
				_("Unix/Linux"),
				None,
				_("Change the document to use Unix/Linux line endings"),
				lambda a: self.change_newline(self.NEWLINE_TYPE_LF)),
			("NewlineMadnessPluginToCR",
				None,
				_("Mac OS Classic"),
				None,
				_("Change the document to use Mac OS Classic line endings"),
				lambda a: self.change_newline(self.NEWLINE_TYPE_CR)),
			("NewlineMadnessPluginToCRLF",
				None,
				_("Windows"),
				None,
				_("Change the document to use Windows line endings"),
				lambda a: self.change_newline(self.NEWLINE_TYPE_CRLF))
		])

		manager = window.get_ui_manager()
		manager.insert_action_group(action_group, -1)
		ui_id = manager.add_ui_from_string(ui_str)
		window.set_data("NewlineMadnessPluginUIId", ui_id)

		# Prime the statusbar
		statusbar = window.get_statusbar()
		sb_frame = gtk.Frame()
		sb_label = gtk.Label()
		sb_frame.add(sb_label)
		statusbar.pack_end(sb_frame, False, False)
		sb_frame.show_all()

		for view in window.get_views(): 
			self.connect_handlers(view)

		self._sb_frame = sb_frame
		self._sb_label = sb_label
		self._action_group = action_group
		self._window = window
		self._plugin = plugin

		tab_added_id = window.connect("tab_added", lambda w, t: self.connect_handlers(t.get_view()))
		window.set_data("NewlineMadnessPluginHandlerId", tab_added_id)

		self.update_ui()

	def deactivate(self):
		window = self._window

		ui_id = window.get_data("NewlineMadnessPluginUIId")
		manager = window.get_ui_manager()
		manager.remove_ui(ui_id)
		manager.remove_action_group(self._action_group)
		manager.ensure_update()

		tab_added_id = window.get_data("NewlineMadnessPluginHandlerId")
		window.disconnect(tab_added_id)
		window.set_data("NewlineMadnessPluginHandlerId", None)

		for view in window.get_views():
			self.disconnect_handlers(view)

		gtk.HBox.remove(window.get_statusbar(), self._sb_frame)

		self._sb_frame = None
		self._sb_label = None
		self._action_group = None
		self._window = None
		self._plugin = None

	def connect_handlers(self, view):
		doc = view.get_buffer()
		newline_id = doc.connect("notify::newline-type", self.update_status)
		doc.set_data("NewlineMadnessPluginHandlerId", newline_id)

	def disconnect_handlers(self, view):
		doc = view.get_buffer()
		newline_id = doc.get_data("NewlineMadnessPluginHandlerId")
		doc.disconnect(newline_id)
		doc.set_data("NewlineMadnessPluginHandlerId", None)

	def update_ui(self):
		doc = self._window.get_active_document()
		self._action_group.set_sensitive(doc != None and not doc.get_readonly())
		self.update_status(doc, None)

	def change_newline(self, nl):
		doc = self._window.get_active_document()

		if doc:
			doc.set_property("newline-type", nl)
			doc.set_modified(True)

	# Statusbar message
	def update_status(self, doc, pspec):
		sb_label = self._sb_label

		if doc:
			nl = doc.get_property('newline-type')

			if nl == self.NEWLINE_TYPE_LF:
				sb_label.set_text(_("Unix/Linux"))
			if nl == self.NEWLINE_TYPE_CR:
				sb_label.set_text(_("Mac OS Classic"))
			if nl == self.NEWLINE_TYPE_CRLF:
				sb_label.set_text(_("Windows"))

			sb_label.show()

		else:
			sb_label.hide()

class NewlineMadnessPlugin(gedit.Plugin):
	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}

	def activate(self, window):
		self._instances[window] = NewlineMadnessWindowHelper(self, window)

	def deactivate(self, window):
		self._instances[window].deactivate()
		del self._instances[window]

	def update_ui(self, window):
		self._instances[window].update_ui()

