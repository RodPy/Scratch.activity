# Copyright (C) 2012-2018 One Laptop per Child

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import subprocess
import os
import errno
import logging

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import Gtk

from sugar3.activity.activity import Activity


class ScratchLauncher(Activity):

    def __init__(self, handle):
        # Initialize the parent
        Activity.__init__(self, handle)

        self.max_participants = 1

        hbox = Gtk.HBox()
        self.set_canvas(hbox)
        self.show_all()
        options = [
            'scratch-desktop', '--nolockfile', '--fullscreen=native', '--noprint']
        doc_path = self.get_documents_path()
        if doc_path is not None:
            options.extend(('--savedir', doc_path))
        proc = subprocess.Popen(options)

        # Stay alive with a blank window mapped for at least 60 seconds
        # so that the shell knows that we launched
        GLib.timeout_add_seconds(60, Gtk.main_quit)
        # but get rid of that window if the child exits beforehand
        GLib.child_watch_add(proc.pid, Gtk.main_quit)

    def get_documents_path(self):
        """Gets the path of the DOCUMENTS folder

        If xdg-user-dir can not find the DOCUMENTS folder it returns
        $HOME, which we omit. xdg-user-dir handles localization
        (i.e. translation) of the filenames.

        Returns: Path to $HOME/DOCUMENTS or None if an error occurs

        Code from src/jarabe/journal/model.py
        """
        try:
            pipe = subprocess.Popen(['xdg-user-dir', 'DOCUMENTS'],
                                    stdout=subprocess.PIPE)
            documents_path = os.path.normpath(pipe.communicate()[0].strip())
            if os.path.exists(documents_path) and \
                    os.environ.get('HOME') != documents_path:
                return documents_path
        except OSError as exception:
            if exception.errno != errno.ENOENT:
                logging.exception('Could not run xdg-user-dir')
        return None
