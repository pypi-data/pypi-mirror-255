import ipyvuetify as v
from ..base_presenter import BasePresenter
from functools import partial
from ..config import Config


class NavigationMenu:
    """
        Menu implementation using Vuetify's NavigationDrawer for the left side menu, and Toolbar for the top menu.
    """

    def __init__(self, title: str = None, subtitle: str = None, items: list = None, nav_width: str = '230px',
                 mode: str = 'top', logo=None):
        """
        :param title: Title of the navigation menu
        :param subtitle: Subtitle of the navigation menu
        :param items: List of NavigationMenuItem
        :param nav_width: Width of the navigation menu
        :param mode: 'top' or 'side'
        :param logo: Logo of the navigation menu
        """
        self.title = title
        if subtitle is None:
            self.subtitle = ''
        else:
            self.subtitle = subtitle

        if items is None:
            self.items = []
        else:
            self.items = items

        self.mode = mode
        self.logo = logo
        self.nav_width = nav_width

        self.view = self.create_navigation_menu(mode)
        self.main_view = None

    def create_navigation_menu(self, mode):
        if mode == 'top':
            return self.create_navigation_bar()
        else:
            return self.create_navigation_drawer()

    def create_navigation_drawer(self):
        nav_menu = v.NavigationDrawer(fixed=True,
                                      mini_variant=False,
                                      permanent=True,
                                      width=self.nav_width,
                                      )

        if self.title is not None:
            nav_menu.children = [
                v.List(class_='my-3', children=[
                    v.ListItem(children=[
                        v.Img(src=self.logo, width=Config.NavigationMenu.logo_size,
                              height=Config.NavigationMenu.logo_size, class_='mr-2') if self.logo else '',
                        v.ListItemTitle(class_='logo-text', style_=Config.NavigationMenu.title_text_style, children=[
                            self.title
                        ])
                    ]),

                ]),
                # v.Divider()
            ]

        nav_items = []
        for item in self.items:
            nav_items.append(v.ListItem(class_='py-1', link=True, children=[
                v.ListItemIcon(class_='mx-2', children=[
                    v.Icon(children=[item.icon], color=item.icon_color, size='16px')
                ]),
                v.ListItemContent(children=[
                    v.ListItemTitle(style_="color:#2A3547", children=[
                        item.title
                    ])
                ])
            ]))
            item.view_component = nav_items[-1]

        nav_menu.children = nav_menu.children + [v.List(dense=True, nav=True, children=nav_items)]
        return nav_menu

    def create_navigation_bar(self):
        nav_bar = v.Toolbar(app=True,
                            style_=f"""
                            position:fixed;
                            width:100%;
                            height:64px;
                            z-index: 10;
                            padding: 0 calc((100% - {Config.Content.width['top_nav_mode']}) / 2);"""
                            )

        nav_items = []
        for item in self.items:
            nav_item = v.Btn(
                height='50px !important',
                flat=True,
                text=True,
                style_="color:#2A3547;border-radius:20px !important;",
                children=[
                    v.Icon(children=[item.icon], color=item.icon_color, left=True),
                    item.title
                ]
            )
            item.view_component = nav_item
            nav_items.append(nav_item)

        nav_bar.children = [
            v.ToolbarTitle(class_='d-flex', children=[
                v.Img(src=self.logo, class_='mr-2', width=Config.NavigationMenu.logo_size,
                      height=Config.NavigationMenu.logo_size) if self.logo else '',
                v.Html(tag='span', class_='logo-text', style_=Config.NavigationMenu.title_text_style,
                       children=[self.title if self.title else ''])
            ]),
            v.Spacer(),
            v.ToolbarItems(children=nav_items, class_='align-center')
        ]
        return nav_bar

    def connect_to_main_view(self, main_view):
        self.main_view = main_view
        for item in self.items:
            item.view_component.on_event('click', partial(self.on_nav_clicked, item))

    def on_nav_clicked(self, clicked_item, *_):
        self.main_view.set_content(clicked_item.get_content())
        for nav_item in self.items:
            nav_item.view_component.class_list.remove('v-nav-active')
        clicked_item.view_component.class_list.add('v-nav-active')

    def preload_contents(self):
        for item in self.items:
            item.get_content()

    def move_to(self, item_index):
        self.on_nav_clicked(self.items[item_index])


class NavigationMenuItem:
    """
        A single item for navigation menu.
    """

    def __init__(self, title: str, icon: str, icon_color: str = 'rgb(42, 53, 71)',
                 content_presenter: BasePresenter = None):
        """
        :param title: Title of the navigation menu item
        :param content_presenter: Presenter class instance
        :param icon: material icon name
        :param icon_color: icon color
        """
        self.title = title
        self.icon = icon
        self.icon_color = icon_color
        self.content_presenter = content_presenter
        self.rendered = False
        self.view_component = None

    def get_content(self):
        """
        Returns the content of the navigation menu item.
        :return: view of the controller
        """
        if self.content_presenter is None:
            return ""

        if not self.rendered:
            self.rendered = True
            self.content_presenter.render()

        return self.content_presenter.view
