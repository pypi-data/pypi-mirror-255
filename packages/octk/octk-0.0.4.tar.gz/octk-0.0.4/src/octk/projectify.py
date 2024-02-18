import os
from octk.pytree import FileTree
from typing import Optional

from importlib.resources import files

gitignore_template_map = {
    "python": "Python.gitignore",
}

def get_gitignore_template(template_key="python"):
    template_name = gitignore_template_map[template_key]
    return files('octk.assets').joinpath(template_name).read_text()


def add_gitignore_file(
        folder=".", overwrite=False, template_keys=[], 
        custom_gitignore_template:Optional[str]=None, append=False
        ):
    """
    template_keys: list of keys to use to get gitignore templates. 
        Valid keys are: ["python", ]
    """
    
    open_mode = "a" if append else "w"

    gitignore_file = os.path.join(folder, ".gitignore")
    if os.path.exists(gitignore_file):
        if not overwrite:
            raise FileExistsError(f"File already exists: {gitignore_file}")

    gitignore_content = ""
    if custom_gitignore_template:
        with open(custom_gitignore_template, mode="r", encoding='utf-8') as file:
            gitignore_content += file.read()

    for template_key in template_keys:
        gitignore_content += get_gitignore_template(template_key)

    with open(gitignore_file, mode=open_mode, encoding='utf-8') as file:
        file.write(gitignore_content)


def create_readme(folder=".", show_files=True, overwrite=False):

    readme_file = os.path.join(folder, "README.md")
    if not overwrite and os.path.exists(readme_file):
        raise FileExistsError(f"File already exists: {readme_file}")

    readme_content = f"""
# My Project

This is a sample project.

## Installation

To install the project, run the following command:

## Usage

To use the project, run the following command:

## Dependencies

### Apps of Direct Interaction
- 

### Inhouse Python Packages
- 

### External Python Packages
-

## Contributing/Development

To contribute to the project, follow these steps:

"""
    
    if show_files:
        readme_content += get_file_tree_section(folder)

    readme_file = os.path.join(folder, "README.md")
    with open(readme_file, "w", encoding='utf-8') as file:
        file.write(readme_content)

def get_file_tree_section(folder="."):
    file_tree = FileTree(folder, all_files=False, exclude_dirs=["__pycache__", ".git", ".idea"], )
    section_text = f"""
## File Tree

{file_tree}
"""
    return section_text

