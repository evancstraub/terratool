import argparse
import os
import json
import subprocess
from rich import print
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from shutil import rmtree

# Constants for file tracking and console
TRACKING_FILE = 'build_terraform_tracking.json'
console = Console()

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def add_main_tf_to_empty_dirs(path):
    created_paths = []

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(path):
        # Check if the directory is empty
        if not dirs and not files:
            # Call the function to create main.tf in the empty directory
            create_main_tf(root)
            created_paths.append(root)

    return created_paths


def create_main_tf(path) -> None:
    file_path = path + "/main.tf"
    if not os.path.exists(file_path):
        open(file_path, 'a').close()

def create_module_structure(module_name, create_main_tf):
    # Base path for the module
    base_path = f"modules/{module_name}"

    # Create the base directory for the module
    created_base = create_directory(base_path)

    # Subdirectories and files to create
    subdirectories = ['examples', module_name]
    files_to_create = ['README.md']

    if create_main_tf:
        # Additional Terraform files inside the module-named subdirectory
        files_to_create += [f"{module_name}/main.tf", f"{module_name}/outputs.tf", f"{module_name}/variables.tf"]

    created_files = []
    for subdir in subdirectories:
        # Create each subdirectory
        create_directory(os.path.join(base_path, subdir))

    for file in files_to_create:
        # Create each file
        file_path = os.path.join(base_path, file)
        open(file_path, 'a').close()
        created_files.append(file_path)

    return base_path, created_files if created_base else None


def create_live_structure(envs, lives, create_main_tf):
    changes = []
    for env in envs:
        for live in lives:
            path = f"{env}/{live}"
            created = create_directory(path)
            file_path = None
            if created and create_main_tf:
                file_path = os.path.join(path, 'main.tf')
                open(file_path, 'a').close()
            changes.append((path, file_path))
    return changes

def git_add_files(files):
    git_added = []
    for file in files:
        try:
            subprocess.run(['git', 'add', file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            git_added.append(True)
        except subprocess.CalledProcessError:
            git_added.append(False)
    return git_added

def track_changes(changes):
    with open(TRACKING_FILE, 'w') as file:
        json.dump(changes, file)

def read_tracked_changes():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as file:
            return json.load(file)
    return {}

def revert_changes():
    changes = read_tracked_changes()
    for change in changes.get('created', []):
        if os.path.exists(change):
            if os.path.isdir(change):
                rmtree(change)
            else:
                os.remove(change)
            print(f"[red]Removed[/red]: {change}")





def main():
    # setup and interpret parsing
    parser = argparse.ArgumentParser(description='Build Terraform Directory Structure')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity')
    parser.add_argument('--modules', nargs='+', help='List of module directories to create')
    parser.add_argument('--live', nargs='+', help='List of live directories to create')
    parser.add_argument('-e', '--env', nargs='+', help='List of environments for live directories')
    parser.add_argument('--no-main', action='store_true', help='Do not create main.tf files')
    parser.add_argument('--mains-only', nargs=1, help='Supply directory to recursively add main files')
    parser.add_argument('--git-add', action='store_true', help='Add created main.tf files to Git')
    parser.add_argument('--revert', action='store_true', help='Revert the last changes')

    args = parser.parse_args()

    if args.verbose > 0:
        console.log("[yellow]Verbose mode activated[/yellow]")

    if args.revert:
        if args.verbose > 0:
            console.log("[yellow]Reverting changes[/yellow]")
        revert_changes()
        return


    changes = {'created': []}

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="dim")
    table.add_column("main.tf Added")

    if args.git_add:
        table.add_column("Git Added")

    if args.mains_only and len(args.mains_only) > 0:
        changes['created'] = add_main_tf_to_empty_dirs(args.mains_only[0])
        for change in changes['created']:
            table.add_row(change, "[green]Done[/green]")

    else:
        if args.modules:
            for module in args.modules:
                dir_path, file_created = create_module_structure(module, not args.no_main)
                changes['created'].append(dir_path)
                if file_created:
                    changes['created'].append(file_created)
                    git_status = '[green]Added[/green]' if git_add_files([file_created])[0] else '[red]No Git Repo[/red]'
                    table.add_row(module, '[green]Done[/green]', git_status if args.git_add else '')

        if args.live:
            live_changes = create_live_structure(args.env, args.live, not args.no_main)
            for dir_path, file_created in live_changes:
                changes['created'].append(dir_path)
                if file_created:
                    changes['created'].append(file_created)
                    git_status = '[green]Added[/green]' if git_add_files([file_created])[0] else '[red]No Git Repo[/red]'
                    table.add_row(f"{dir_path}", '[green]Done[/green]', git_status if args.git_add else '')

        else:
            if args.verbose > 0:
                console.log("[yellow]Adding main.tf to all empty directories[/yellow]")
            for file_created in create_main_tf(".", not args.no_main):
                changes['created'].append(file_created)
                if args.verbose > 0:
                    console.log(f"[green]Created[/green]: {file_created}")
                if args.git_add:
                    git_status = '[green]Added[/green]' if git_add_files([file_created])[0] else '[red]No Git Repo[/red]'
                    table.add_row(file_created, '[green]Done[/green]', git_status)
                else:
                    table.add_row(file_created, '[green]Done[/green]')

    track_changes(changes)

    console.print(table)

if __name__ == "__main__":
    main()
