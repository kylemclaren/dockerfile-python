import os
import re

class RepoScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.requirements = []
        self.python_version = None
        self.framework = None
        self.has_database = False
        self.main_file = None

    def scan_requirements(self):
        req_file_path = os.path.join(self.repo_path, 'requirements.txt')
        if os.path.isfile(req_file_path):
            with open(req_file_path, 'r') as file:
                self.requirements = [line.split('==')[0].strip() for line in file.readlines()]

    def scan_for_python_version(self):
        py_file_path = os.path.join(self.repo_path, '.python-version')
        if os.path.isfile(py_file_path):
            with open(py_file_path, 'r') as file:
                self.python_version = file.read().strip()
        else:
            runtime_file_path = os.path.join(self.repo_path, 'runtime.txt')
            if os.path.isfile(runtime_file_path):
                with open(runtime_file_path, 'r') as file:
                    runtime_content = file.read().strip()
                    if runtime_content.startswith('python-'):
                        self.python_version = runtime_content.split('python-')[1]

            pipenv_lock_path = os.path.join(self.repo_path, 'Pipfile.lock')
            if os.path.isfile(pipenv_lock_path):
                with open(pipenv_lock_path, 'r') as file:
                    pipenv_content = file.read()
                    match = re.search(r'"python_version": "(\d+\.\d+)"', pipenv_content)
                    if match:
                        self.python_version = match.group(1)

    def scan_for_framework(self):
        known_frameworks = {
            "flask": ["app.py", "wsgi.py"],
            "django": ["manage.py"],
            "fastapi": ["main.py", "app.py", "wsgi.py"]
        }
        for framework, files in known_frameworks.items():
            for file in files:
                if os.path.isfile(os.path.join(self.repo_path, file)):
                    self.framework = framework
                    break

    def scan_for_database(self):
        known_databases = {
            "sqlalchemy": ["migrations"],
            "psycopg2": [],
            "mysql-connector-python": [],
            "pymongo": []
        }
        for db, dirs in known_databases.items():
            for dir in dirs:
                if os.path.isdir(os.path.join(self.repo_path, dir)):
                    self.has_database = True
                    return

    def scan_for_main_file(self):
        common_main_files = ["main.py", "app.py", "wsgi.py", "run.py", "server.py"]
        other_python_files = []

        for file in os.listdir(self.repo_path):
            if file in common_main_files:
                self.main_file = file
                return
            elif file.endswith('.py'):
                other_python_files.append(file)

        if len(other_python_files) == 1:
            # If there's only one Python file, assume it's the main file
            self.main_file = other_python_files[0]
        elif len(other_python_files) > 1:
            raise Exception("Multiple Python files found and none match common main file names. Please specify the main file.")
        else:
            raise Exception("No Python files found in the repository. Please ensure the project contains a Python file.")


    def scan(self):
        self.scan_requirements()
        self.scan_for_python_version()
        self.scan_for_framework()
        self.scan_for_database()
        self.scan_for_main_file()