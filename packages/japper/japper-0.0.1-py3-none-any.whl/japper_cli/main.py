import argparse
import yaml
import os, subprocess
from .init_project import init_project

CONFIG_FILENAME = '.japper.yml'
WORKING_DIR = os.getcwd().replace('\\', '/')


class STDOUT_COLOR:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def run_command(cmd, fail_msg=None, print_cmd=False):
    if print_cmd:
        print(f'Running command: {cmd}')
    ret = os.system(cmd)
    if ret != 0:
        if fail_msg:
            print_console(fail_msg)
        exit(-1)
    return ret


def get_input(prompt, default=None, optional=False, allow_spaces=False):
    while True:
        if default:
            user_input = input(f"{prompt}: ({default}) ")
            if not user_input:
                user_input = default
        else:
            user_input = input(prompt + ': ')
            if not user_input:
                if optional:
                    return None
                else:
                    print("This field is required")
                    continue

        if not allow_spaces and ' ' in user_input:
            print("It cannot contain spaces")
            continue

        return user_input


def save_config(config):
    with open(CONFIG_FILENAME, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def load_config():
    if not os.path.exists(CONFIG_FILENAME):
        return {}
    with open(CONFIG_FILENAME, 'r') as f:
        return yaml.safe_load(f)


def print_console(msg):
    print(STDOUT_COLOR.HEADER + '[Japper] ' + STDOUT_COLOR.ENDC + msg)


def build_docker_image(dest, quiet=False):
    print_console('Building the Docker image...')
    cmd = f'cd container/{dest} && docker-compose build'
    if quiet:
        cmd += ' -q'
    ret = os.system(cmd)
    if ret != 0:
        print_console('Failed to build the Docker image')
        exit(-1)


def handle_build(args, config):
    """Handle build subcommand"""
    build_docker_image(args.dest)


def handle_doc(args, config):
    print_console("Generating documentation")
    ret = os.system('pdoc --html --config show_source_code=False -o docs --force app ')
    if ret != 0:
        exit(-1)
    print_console("\nDocumentation generated at docs/app/index.html\n"
                  + f"   Open in browser: file:///{WORKING_DIR}/docs/app/index.html")


def handle_run(args, config):
    """Handle run subcommand"""
    dest = args.dest

    if dest == 'prod':
        print_console("Running the project in production preview mode (user is set to jovyan)")
    elif dest == 'dev':
        print_console("Running the project in development mode")

    # docker image build
    build_docker_image(dest, quiet=not args.verbose)

    # docker-compose up
    if dest == 'dev':
        print_console("Your app will be running at http://localhost:8888\n"
                      + "\t You can also access JuptyerLab at http://localhost:8889/lab")
    elif dest == 'prod':
        print_console("Your app will be running at http://localhost:8888/user/jovyan/")

    print_console("Starting the Docker container (this may take a while) ...")
    if not args.verbose:
        print(f"\t Docker compose logs are being written to file:///{WORKING_DIR}/container/{dest}/docker-compose.log\n"
              + "\t You can use -v or --verbose option to see the logs.")
    print_console("Press Ctrl+C to stop the container")
    cmd = f'cd container/{dest} && docker-compose up --remove-orphans'
    if not args.verbose:
        cmd += ' &> docker-compose.log'
    ret = os.system(cmd)
    if ret != 0 and ret != 33280 and not args.verbose:
        print_console(
            f'Failed to start the Docker container. Please check the logs in file:///{WORKING_DIR}/container/{dest}/docker-compose.log')
        exit(-1)


def handle_deploy(args, config):
    """Handle deploy subcommand"""
    if args.target == 'registry':
        if 'registry_url' not in config:
            registry_url = get_input("Enter the Docker registry URL", 'docker.io')
            if registry_url == 'docker.io':
                registry_namespace = get_input("Enter the docker.io username")
            else:
                registry_namespace = get_input("Enter the Docker registry namespace (optional)", optional=True)

            registry_image_name = get_input("Enter the remote image name", config['project_name'])

            config['registry_url'] = registry_url
            config['registry_namespace'] = registry_namespace
            config['registry_image_name'] = registry_image_name
            save_config(config)
        else:
            config = load_config()
            registry_url = config['registry_url']
            registry_namespace = config['registry_namespace']
            registry_image_name = config['registry_image_name']

        project_name = config['project_name']

        ret = subprocess.run(['docker', 'images', '-q', 'jpr'], stdout=subprocess.PIPE)
        if ret.stdout.decode('utf-8') == '':
            # print_console('No Docker image found. Please run "japper build prod" first.')
            print_console('No Docker image found. Building the Docker image...')
            build_docker_image('prod')

        print_console("Logging in to the Docker registry...")
        run_command(f'docker login {config["registry_url"]}', 'Failed to login to the Docker registry', print_cmd=True)

        print_console("Tagging the Docker image...")
        if registry_url == 'docker.io':
            full_image_name = f'{registry_namespace}/{registry_image_name}:{args.tag}'
        else:
            if registry_namespace:
                full_image_name = f'{registry_url}/{registry_namespace}/{registry_image_name}:{args.tag}'
            else:
                full_image_name = f'{registry_url}/{registry_image_name}:{args.tag}'
        run_command(f'docker tag {project_name} {full_image_name}', 'Failed to tag the Docker image', print_cmd=True)

        print_console("Uploading the Docker image to the registry...")
        run_command(f'docker push {full_image_name}', 'Failed to upload the Docker image', print_cmd=True)

        print_console(f"Successfully uploaded the Docker image to {full_image_name}")


def main():
    """
    japper command line interface main parser
    """
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers(dest='subcommand', required=True)
    subparsers.add_parser('init', help="Initiate a new Japper project")
    parser = subparsers.add_parser('build', help="Build this Japper project")
    parser.add_argument('dest', choices=['dev', 'prod'], help="destination")

    parser = subparsers.add_parser('run', help="Run this Japper project using Docker")
    parser.add_argument('dest', choices=['dev', 'prod'], help="destination")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose mode", default=False)

    parser = subparsers.add_parser('deploy', help="Deploy this Japper project")
    parser.add_argument('target', choices=['registry'], help="target")

    parser = subparsers.add_parser('doc', help="Generate documentation")

    args = main_parser.parse_args()

    if args.subcommand == 'init':
        project_name, project_title = init_project()
        # save inputs to japper config file
        save_config({'project_name': project_name, 'project_title': project_title})
    else:  # other than init
        config = load_config()
        if 'project_name' not in config:
            print("No project found. Please run 'japper init' first.")
            exit(-1)
        if args.subcommand == 'build':
            handle_build(args, config)
        elif args.subcommand == 'run':
            handle_run(args, config)
        elif args.subcommand == 'deploy':
            handle_deploy(args, config)
        elif args.subcommand == 'doc':
            handle_doc(args, config)


if __name__ == '__main__':
    main()
