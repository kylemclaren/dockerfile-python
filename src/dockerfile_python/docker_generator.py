import os
import pkg_resources
from .scanner import RepoScanner

class DockerGenerator:
    SYSTEM_DEPENDENCIES = {
        'numpy': ['libatlas-base-dev', 'gfortran'],
        'pillow': ['libjpeg8-dev'],
        # Add more packages and their dependencies as needed
    }

    def __init__(self, repo_path, base_image=None, ignore_files=None, force=False, scanner=None):
        self.repo_path = repo_path
        self.base_image = base_image
        self.ignore_files = ignore_files
        self.force = force
        self.scanner = scanner if scanner is not None else RepoScanner(repo_path)
        self.templates_path = pkg_resources.resource_filename('dockerfile_python', 'templates')

    def generate_dockerfile(self):
        base_image = self.base_image or 'python:3.8'
        if self.scanner.framework == 'django':
            base_image = 'python:3.9-slim-buster'
        elif 'pandas' in self.scanner.requirements or 'numpy' in self.scanner.requirements:
            base_image = 'jupyter/scipy-notebook'
        # Choose base image based on detected framework or libraries

        install_commands = 'pip install -r requirements.txt'
        system_dependencies = []
        for package in self.scanner.requirements:
            if package in self.SYSTEM_DEPENDENCIES:
                system_dependencies.extend(self.SYSTEM_DEPENDENCIES[package])
        if system_dependencies:
            install_commands = f'apt-get update && apt-get install -y {" ".join(system_dependencies)} && ' + install_commands
        # Add system dependencies installation to install_commands if necessary

        if self.scanner.framework == 'flask' and 'gunicorn' in self.scanner.requirements:
            entrypoint_command = 'gunicorn -w 4 -b :8080 app:app'  # adjust as necessary for your app
        elif self.scanner.framework == 'django':
            entrypoint_command = 'gunicorn -w 4 -b :8080 projectname.wsgi:application'  # adjust as necessary for your app
        else:
            entrypoint_command = f'python {self.scanner.main_file}'

        dockerfile_template_path = os.path.join(self.templates_path, "Dockerfile.template")
        dockerfile_path = os.path.join(self.repo_path, "Dockerfile")

        with open(dockerfile_template_path, "r") as template_file:
            dockerfile_content = template_file.read()

        dockerfile_content = dockerfile_content.format(
            BASE_IMAGE=base_image,
            INSTALL_COMMANDS=install_commands,
            ENTRYPOINT_COMMAND=entrypoint_command
        )

        with open(dockerfile_path, "w") as dockerfile_file:
            dockerfile_file.write(dockerfile_content)

    def generate_dockerignore(self):
        dockerignore_template_path = os.path.join(self.templates_path, ".dockerignore.template")
        dockerignore_path = os.path.join(self.repo_path, ".dockerignore")

        with open(dockerignore_template_path, "r") as template_file:
            dockerignore_content = template_file.read()

        with open(dockerignore_path, "w") as dockerignore_file:
            dockerignore_file.write(dockerignore_content)

    def generate_entrypoint(self):
        if self.scanner.framework == 'flask' and 'gunicorn' in self.scanner.requirements:
            start_command = 'gunicorn -w 4 -b :8080 app:app'  # adjust as necessary for your app
        elif self.scanner.framework == 'django':
            start_command = 'gunicorn -w 4 -b :8080 projectname.wsgi:application'  # adjust as necessary for your app
        else:
            start_command = f'python {self.scanner.main_file}'

        entrypoint_template_path = os.path.join(self.templates_path, "entrypoint.sh.template")
        entrypoint_path = os.path.join(self.repo_path, "entrypoint.sh")

        with open(entrypoint_template_path, "r") as template_file:
            entrypoint_content = template_file.read()

        entrypoint_content = entrypoint_content.format(START_COMMAND=start_command)

        with open(entrypoint_path, "w") as entrypoint_file:
            entrypoint_file.write(entrypoint_content)
            os.chmod(entrypoint_path, 0o755)  # Make the entrypoint.sh executable

    def generate(self):
        self.generate_dockerfile()
        self.generate_dockerignore()
        self.generate_entrypoint()
