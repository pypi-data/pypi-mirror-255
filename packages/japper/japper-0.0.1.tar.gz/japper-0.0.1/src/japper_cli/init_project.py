import os
import shutil

from . import templates

DIRS_TO_CREATE = ['app', 'app/assets', 'app/commons', 'app/models', 'app/presenters', 'app/views']
EMPTY_FILES_TO_CREATE = ['app/commons/__init__.py', 'app/models/__init__.py', 'app/__init__.py']


def create_file(file_path, content=''):
    with open(file_path, 'w') as f:
        f.write(content)


def init_project():
    print("Initiating a new Japper project")

    # get project information
    while True:
        project_name = input("Enter project name (e.g. japper_project): ")
        if not project_name or ' ' in project_name:
            print("Project name cannot be empty or contain spaces")
            continue
        break
    while True:
        project_title = input("Enter project title (e.g. Japper Project): ")
        if not project_title:
            print("Project title cannot be empty")
            continue
        break

    # Create a new directory for the project
    for dir_str in DIRS_TO_CREATE:
        os.makedirs(dir_str, exist_ok=True)

    # Create a new file for the project
    for file in EMPTY_FILES_TO_CREATE:
        create_file(file)

    # copy files from static folder
    static_path = os.path.dirname(__file__) + '/static/'
    shutil.copyfile(static_path + 'icon.png', 'app/assets/icon.png')
    shutil.copyfile(static_path + 'logo.png', 'app/assets/logo.png')
    shutil.copyfile(static_path + 'app.ipynb', 'app.ipynb')
    shutil.copyfile(static_path + 'gitignore', '.gitignore')
    shutil.copytree(static_path + 'container', 'container')

    # create app_main.py
    create_file('app/__init__.py', "from .app_main import AppMain\n")
    create_file('app/app_main.py', templates.APP_MAIN)

    # create custom.html
    create_file('app/assets/custom.html', templates.CUSTOM_HTML)

    # create environment.yml
    create_file('environment.yml', templates.ENVIRONMENT_FILE)

    # create config.py
    create_file('app/commons/config.py', templates.CONFIG_FILE % project_title)

    # create home page
    create_file('app/presenters/home.py', templates.HOME_PRESENTER)
    create_file('app/views/home.py', templates.HOME_VIEW % project_title)

    # create tool page
    create_file('app/presenters/tool.py', templates.create_empty_presenter('Tool'))
    create_file('app/views/tool.py', templates.create_empty_view('Tool'))
    create_file('app/models/tool.py', templates.create_empty_model('Tool'))

    # create __init__.py files
    create_file('app/presenters/__init__.py', "from .home import HomePresenter\nfrom .tool import ToolPresenter\n\n")
    create_file('app/views/__init__.py', "from .home import HomeView\nfrom .tool import ToolView\n\n")
    create_file('app/models/__init__.py', "from .tool import ToolModel\n\n")
    create_file('app/commons/__init__.py', templates.COMMONS_INIT)

    # create docker-compose files
    create_file('container/dev/docker-compose.yml', templates.create_docker_compose_dev(project_name))
    create_file('container/prod/docker-compose.yml', templates.create_docker_compose_prod(project_name))

    # create Readme
    create_file('README.md', templates.README % project_title)

    print("Project initiated successfully")

    return project_name, project_title
