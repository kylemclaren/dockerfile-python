import argparse
from .scanner import RepoScanner
from .docker_generator import DockerGenerator

def main():
    parser = argparse.ArgumentParser(description="Python repository scanner and Dockerfile generator")
    parser.add_argument("--repo-path", default=".", help="The path to the Python repository to scan")
    parser.add_argument("--base-image", default="python:3.8-buster", help="Base image to use for Dockerfile")
    parser.add_argument("--ignore-files", nargs="*", default=[], help="Files or directories to ignore in Dockerfile")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing Dockerfiles")
    # Add more arguments as needed

    args = parser.parse_args()

    # Define the paths
    repo_path = args.repo_path

    # Initialize the scanner and scan the repo
    scanner = RepoScanner(repo_path)
    scanner.scan()

    # Initialize the Docker generator and generate Dockerfile and related files
    docker_generator = DockerGenerator(repo_path, args.base_image, args.ignore_files, args.force, scanner=scanner)   
    docker_generator.generate()
