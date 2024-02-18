# to compress new Comm package issue on Sphinx https://github.com/jupyter-widgets/ipywidgets/pull/3533
import ipykernel.ipkernel  # noqa

from IPython.display import HTML
from IPython.display import display
import ipywidgets as ipyw

from .app_main_view import AppMainView
from . import utils
from .debug import is_dev, debug_view
from .widgets import NavigationMenu


def init_js_output():
    """
    Initialize the output widget for JS. We need this approach to avoid blank space at the bottom of the page when
    new JS is executed.
    """
    output = ipyw.Output(layout={'display': 'none'})
    display(output)
    utils.set_js_output(output)


def inject_files():
    utils.inject_html('global.html')


class JapperAppMain:

    def __init__(self, page_title='Japper App', favicon_path=None):
        init_js_output()
        self.main_view = AppMainView()
        self.nav_menu = None
        self.set_page_title(page_title)
        if favicon_path:
            self.set_favicon(favicon_path)

        self.add_custom_html('app/assets/custom.html')

        # if dev mode, show the debug view
        if is_dev():
            debug_view.display_debug_view()

    def start(self):
        """
        Start the app
        """

        inject_files()
        self.main_view.render()

        self.connect_util_funcs()
        display(self.main_view)

    def add_custom_html(self, filepath):
        display(HTML(filename=filepath))

    def set_nav_menu(self, nav_menu):
        self.nav_menu = nav_menu
        self.main_view.set_nav_menu(nav_menu)
        self.nav_menu.connect_to_main_view(self.main_view)
        utils.set_nav_menu(self.nav_menu)

        # preload all contents
        self.nav_menu.preload_contents()

    def connect_util_funcs(self):
        """
        Connect utility functions from the main controller
        """
        utils.set_message_funcs(
            self.main_view.loading_dialog.show_loading,
            self.main_view.loading_dialog.hide_loading,
            self.main_view.toast_alert.alert
        )

    def set_page_title(self, title):
        """
        Set the page title using JS
        """
        display(HTML(f'<script>document.title = "{title}";</script>'))

    def set_favicon(self, filepath):
        """
        Set the favicon using JS
        """
        display(HTML(f"""<script>
            var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
            link.type = 'image/png';
            link.rel = 'shortcut icon';
            link.href = '{filepath}';
            document.getElementsByTagName('head')[0].appendChild(link);
            </script>
        """))

    def create_navigation_menu(self, mode, title, logo, items):
        nav_menu = NavigationMenu(mode=mode,
                                  title=title,
                                  logo=logo,
                                  items=items)
        self.set_nav_menu(nav_menu)
