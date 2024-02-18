CUSTOM_HTML = """
<!--
    This file contains custom styles and scripts
-->
<html>

<style>
</style>

<script>
</script>

</html>
"""

ENVIRONMENT_FILE = """
name: japper_app
channels:
  - conda-forge
dependencies:
  - voila
  - ipyvuetify
  - ipywidgets
  - pandas
  - japper
  # add your dependencies here
"""

COMMONS_INIT = '''
"""
Commons package. This package contains all the common classes and functions that are used in the application.
"""
from .config import Config

'''

CONFIG_FILE = '''
"""
global configurations
"""


class Config:
    APP_NAME = '%s'  #: project title
    #: path to the icon. This will be used as the favicon and the navigation menu logo.
    ICON_PATH = 'app/assets/icon.png'
    #: path to the logo image. This will be used as the logo in the home page.
    LOGO_PATH = 'app/assets/logo.png'
'''

APP_MAIN = '''
"""
Main class of the app.
"""

from japper import JapperAppMain
from japper.widgets import NavigationMenuItem
from .presenters import HomePresenter, ToolPresenter
from .commons.config import Config


class AppMain(JapperAppMain):

    def __init__(self):
        """
        Create a new instance of AppMain. This is the main class of the app. It extends JapperAppMain, and it is used to
        create the navigation menu and start the app.
        """
        super().__init__(page_title=Config.APP_NAME, favicon_path=Config.ICON_PATH)

        # init presenters
        self.home_presenter = HomePresenter()
        self.tool_presenter = ToolPresenter()

        # create navigation menu
        self.create_navigation_menu(mode='top',  # mode can be 'top' or 'side'
                                    title=Config.APP_NAME,
                                    logo=Config.ICON_PATH,
                                    items=[
                                        NavigationMenuItem(title='Home', icon='mdi-home',
                                                           content_presenter=self.home_presenter),
                                        NavigationMenuItem(title='Tool', icon='mdi-settings',
                                                           content_presenter=self.tool_presenter),
                                    ])

    def start(self):
        """
        Start the app
        """
        super().start()
        self.nav_menu.move_to(0)  # show the first menu item

'''

README = """
"# %s

This is a Jupyter-based web application build by Japper

## Getting Started

1. Install Japper
    
    ```bash
    pip install japper
    ```
    
2. Run the app
    
    ```bash
    japper run dev
    ```
        
3. Open your browser and go to [http://localhost:8866](http://localhost:8866)


"""

HOME_PRESENTER = '''
"""
Home Presenter
"""
from japper import BasePresenter
from ..views import HomeView


class HomePresenter(BasePresenter):
    def __init__(self) -> None:
        """
        Create a new instance of HomePresenter. This class is used to manage the home page of the app.
        """
        super().__init__()
        self.view = HomeView()
        
'''

HOME_VIEW = '''
"""
This is a sample view for the home page.
"""
import ipyvuetify as v
from japper import BaseView
from japper.utils import get_nav_menu


class HomeView(BaseView):
    def __init__(self) -> None:
        """
        Create a new instance of HomeView. This is the view for the home page.
        """
        super().__init__()

    def render(self):
        """
        Render the view. This method is called by the framework to render the view.
        """

        btn_start = v.Btn(color='primary', children=['GET STARTED'], class_='mt-10', large=True)
        btn_start.on_event('click', lambda *_: get_nav_menu().move_to(1))

        self.children = [
            v.Row(class_='align-center justify-center', style_='width:1200px;height:60vh;margin:50px auto;',
                  children=[
                      v.Col(cols=7, children=[
                          v.Html(tag='div', children=[
                              v.Html(tag='p',
                                     class_='display-2 font-weight-bold',  # we can specify class directly
                                     children=['Welcome to %s!']),
                              v.Html(tag='p', style_='font-size:1.2em;',  # we can also specify class style
                                     children=['This is a Jupyter-based web application built by Japper. We hope you enjoy it!']),
                              btn_start
                          ]),
                      ]),
                      v.Col(cols=4, children=[
                          v.Img(src='/app/assets/logo.png', style_='width: 80%%;')
                      ]),
                  ]),
        ]

'''


def create_empty_presenter(name):
    return f"""
from japper import BasePresenter
from ..views import {name}View
from ..models import {name}Model


class {name}Presenter(BasePresenter):
    def __init__(self) -> None:
        super().__init__()
        self.view = {name}View()
        self.model = {name}Model()
    """


def create_empty_view(name):
    return f'''
import ipyvuetify as v
from japper import BaseView

class {name}View(BaseView):
    def __init__(self) -> None:
        super().__init__()
    
    def render(self):
        self.children = [
            v.Html(tag='h1', children=['{name}']),
        ]

'''


def create_empty_model(name):
    return f'''

class {name}Model:
    def __init__(self) -> None:
        pass
    '''


def create_docker_compose_dev(name):
    return f'''
name: {name}
services:
  {name}-dev:
    build:
      context: ../../
      dockerfile: ./container/dev/Dockerfile
    volumes:
      - ../..:/home/jovyan/japper_app
    ports:
      - "8888:8888"
      - "8889:8889"
    environment:
      JAPPER_APP_DEV: "true"

    '''


def create_docker_compose_prod(name):
    return f'''
name: {name}
services:
  {name}-prod:
    build:
      context: ../../
      dockerfile: ./container/prod/Dockerfile
    image: {name}
    ports:
      - "8888:8888"
    environment:
      JUPYTERHUB_USER: "jovyan"
'''
