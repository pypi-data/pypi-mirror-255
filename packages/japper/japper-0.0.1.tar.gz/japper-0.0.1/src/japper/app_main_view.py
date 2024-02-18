import ipyvuetify as v
from .widgets import LoadingDialog, ToastAlert
from .config import Config
from .debug import is_dev


class AppMainView(v.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toast_alert = None
        self.loading_dialog = None
        self.content = None
        self.nav_menu = None
        self.style_ = f'background-color: {Config.Content.background_color};'

    def set_nav_menu(self, nav_menu):
        self.nav_menu = nav_menu
        self.children = [self.nav_menu.view] + self.children

    def render(self):
        self.content = self.make_content_area()
        self.loading_dialog = LoadingDialog()
        self.toast_alert = ToastAlert(self)

        self.children = [
            self.nav_menu.view if self.nav_menu is not None else '',
            self.content,
            self.loading_dialog
        ]

        # if is_dev():
        #     self.style_ += 'padding-bottom: 60px;'

    def make_content_area(self):
        content_width = Config.Content.width['top_nav_mode']
        content_margin = '0 auto'
        if self.nav_menu.mode == 'side':
            content_width = f'calc({Config.Content.width["side_nav_mode"]} - {self.nav_menu.nav_width})'
            content_margin = f'0 0 0 {self.nav_menu.nav_width}'
        if self.nav_menu.mode == 'top':
            content_margin = '64px auto 0 auto'

        return v.Html(
            style_=f'height:100%; width: {content_width}; margin: {content_margin}; padding: {Config.Content.padding};',
            tag='div',
            children=[])

    def set_content(self, content):
        self.content.children = [content]
