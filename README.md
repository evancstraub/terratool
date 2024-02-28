# terratool
CLI tool to deploy terra[form|grunt] modules quickly

This script is designed to build Terraform directory structures quickly and efficiently. I threw this together to get some terraform modules spun up quickly, and I figured others might also want a similar tool.

## Project Status: Pre-Initial Release
This project is highly volatile, and subject to change at the moment. If people start using it I will try and make less breaking changes, but 

## Features
- Automatically adds generated files to git
- Quickly generate multi-environment terraform modules
- Files generated are tracked in a file to revert changes -- kinda works
- Will eventually support terragrunt probably

## Usage

### Development

#### Install from source

```bash
git clone git@github.com:evancstraub/terratool.git
poetry install
```

#### Development Usage
```bash
python terratool [options]
```

### Normal Usage
### *Currently not working*
```bash
terratool [options]
```

## Options

- `-v, --verbose`: Increase verbosity. Can be used multiple times for increased verbosity.
- `--modules`: List of module directories to create.
- `--live`: List of live directories to create.
- `-e, --env`: List of environments for live directories.
- `--no-main`: Do not create `main.tf` files.
- `--mains-only`: Supply directory to recursively add main files.
- `--git-add`: Add created `main.tf` files to Git.
- `--revert`: Revert the last changes.

## Compatibility and Tested Status

```
| Platform | Compatibility | Tested Status |
|----------|---------------|---------------|
| Ubuntu   | ✅            | Tested-ish    |
| macOS    | ✅            | Untested      |
| Windows  | ❌            | UnTested      |
|----------|---------------|---------------|
```
