# window.py
#
# Copyright 2022 Axel
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
import gi
gi.require_version('Adw', '1')
gi.require_version('WebKit2', '5.0')
from gi.repository import Gtk, Adw, WebKit2
from urllib import parse


@Gtk.Template(resource_path='/cu/axel/litebrowser/window.ui')
class LitebrowserWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'LitebrowserWindow'

    tab_view = Gtk.Template.Child()
    url_entry = Gtk.Template.Child()
    img_switch = Gtk.Template.Child()
    js_switch = Gtk.Template.Child()
    load_progress_bar = Gtk.Template.Child()
    load_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.block_js = False
        self.block_img = False
        self.img_switch.connect('state-set', self.on_img_switched)
        self.js_switch.connect('state-set', self.on_js_switched)
        self.tab_view.connect('notify::selected-page', self.on_tab_changed)
        self.url_entry.connect('activate', self.load_url)
        self.new_tab(None)

    @Gtk.Template.Callback()
    def new_tab(self, widget):
        web_view = WebKit2.WebView()
        tab_page = self.tab_view.append(web_view)
        web_view.connect('load-failed', self.on_load_error)
        web_view.connect('load-changed', self.on_load_changed, tab_page)
        #web_view.connect('resource-load-started', self.on_load_resource_started)
        tab_page.set_title('New tab')

    def on_tab_changed(self, tab_view, page):
        self.web_view = self.tab_view.get_selected_page().get_child()
        if (url:=self.web_view.get_uri()) is not None:
            self.url_entry.set_text(url)
        else:
            self.url_entry.set_text('')

    def load_url(self, widget):
        query = widget.get_text()
        print(query)

        if '.' in query and ' ' not in query:
            if 'http' not in query:
                query = 'http://' + query
        else:
            query = 'https://google.com/search?q=' + parse.quote_plus(query)

        print(query)

        self.web_view.load_uri(query)

    def load_web_settings(self):
        self.web_view.get_settings().set_auto_load_images(not self.block_img)
        self.web_view.get_settings().set_enable_javascript(not self.block_js)


    @Gtk.Template.Callback()
    def go_back(self, widget):
        if self.web_view.can_go_back():
            self.web_view.go_back()

    @Gtk.Template.Callback()
    def reload(self, widget):
        if not self.web_view.is_loading():
            self.web_view.reload()
        else:
            self.web_view.stop_loading()

    @Gtk.Template.Callback()
    def go_forward(self, widget):
         if self.web_view.can_go_forward():
            self.web_view.go_forward()

    def on_js_switched(self, widget, active):
        self.block_js = active
        self.load_web_settings()

    def on_img_switched(self, widget, active):
        self.block_img = active
        self.load_web_settings()

    def on_load_changed(self, web_view, load_event, tab_page):
        if load_event == WebKit2.LoadEvent.FINISHED:
            if (title := web_view.get_title()) is not None:
                tab_page.set_title(title)
                self.url_entry.set_text(web_view.get_uri())

        if web_view is self.web_view and (progress:=web_view.get_estimated_load_progress()) < 1.0:
            self.load_progress_bar.set_fraction(progress)
            self.load_progress_bar.set_visible(True)
            self.load_button.set_icon_name('gtk-cancel-symbolic')
        else:
            self.load_progress_bar.set_visible(False)
            self.load_button.set_icon_name('gtk-refresh-symbolic')

    def on_load_resource_started(self, web_view, resource, request):
        if 'css' in request.get_uri():
            pass


    def on_load_error(self, web_view, load_event, url, error):
        print(error)


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = 'Lite Browser'
        self.props.version = "0.1.0"
        self.props.authors = ['Axel']
        self.props.copyright = '2022 Axel'
        self.props.logo_icon_name = 'cu.axel.litebrowser'
        self.props.modal = True
        self.set_transient_for(parent)
