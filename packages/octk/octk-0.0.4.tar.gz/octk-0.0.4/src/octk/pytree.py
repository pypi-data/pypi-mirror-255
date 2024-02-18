from pathlib import Path
from itertools import islice
import re
from typing import Optional, Union


# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '


# def tree(dir_path: Path, prefix: str=''):
#     """A recursive generator, given a directory Path object
#     will yield a visual tree structure line by line
#     with each line prefixed by the same characters
#     """    
#     contents = list(dir_path.iterdir())
#     # contents each get pointers that are ├── with a final └── :
#     pointers = [tee] * (len(contents) - 1) + [last]
#     for pointer, path in zip(pointers, contents):
#         yield prefix + pointer + path.name
#         if path.is_dir(): # extend the prefix and recurse:
#             extension = branch if pointer == tee else space 
#             # i.e. space because last, └── , above so no more |
#             yield from tree(path, prefix=prefix+extension)



def remove_matching_paths(path_list, regex_pattern):
    return [path for path in path_list if not re.match(regex_pattern, path.name)]


def remove_if_begins_with_dot(path_list):
    return remove_matching_paths(path_list, r'^\.')


def remove_if_contains_pattern(path_list, pattern):
    return remove_matching_paths(path_list, pattern)


def remove_files_with_extension(path_list, extensions: list):
    return [path for path in path_list if path.suffix not in extensions]


def remove_files_without_extension(path_list, extensions: list):
    return [path for path in path_list if path.suffix in extensions or path.is_dir()]


def remove_dirs_with_name(path_list, names: list):
    return [path for path in path_list if path.name not in names if path.is_dir()]


class FileTree:

    def filter_contents(self, contents):
        if not self.all_files:
            contents = remove_if_begins_with_dot(contents)
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                contents = remove_if_contains_pattern(contents, pattern)
        if self.exclude_extensions:
            contents = remove_files_with_extension(contents, self.exclude_extensions)
        if self.include_extensions:
            contents = remove_files_without_extension(contents, self.include_extensions)

        return contents

    def __init__(
            self, dir_path: Union[Path, str], level: int=-4, limit_to_directories: bool=False, 
            all_files: bool=False, 
            exclude_patterns: Optional[list]=None,
            exclude_dirs: Optional[list]=None, 
            exclude_extensions: Optional[list]=None,
            include_extensions: Optional[list]=None,
            length_limit: int=1000
            ):
        
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        
        if exclude_extensions and include_extensions:
            raise ValueError('Cannot have both exclude and include extensions')
        
        self.all_files = all_files
        self.exclude_patterns = exclude_patterns
        self.exclude_dirs = exclude_dirs
        self.exclude_extensions = exclude_extensions
        self.include_extensions = include_extensions

        self.output_tree_lines = []
        self.output_message_lines = []
        
        """Given a directory Path object print a visual tree structure"""
        dir_path = Path(dir_path) # accept string coerceable to Path
        files = 0
        directories = 0
        def inner(dir_path: Path, prefix: str='', level=-1):
            nonlocal files, directories
            if not level: 
                return # 0, stop iterating
            if limit_to_directories:
                contents = [d for d in dir_path.iterdir() if d.is_dir()]
            else: 
                contents = list(dir_path.iterdir())
            contents = self.filter_contents(contents)
            pointers = [tee] * (len(contents) - 1) + [last]
            for pointer, path in zip(pointers, contents):
                if path.is_dir():
                    yield prefix + pointer + path.name
                    directories += 1
                    # Add a branch to end of the new prefix unless it is the last item
                    extension = branch if pointer == tee else space 
                    yield from inner(path, prefix=prefix+extension, level=level-1)
                elif not limit_to_directories:
                    yield prefix + pointer + path.name
                    files += 1
        # print(dir_path.name)
        self.output_tree_lines.append(dir_path.name)
        
        iterator = inner(dir_path, level=level)
        for line in islice(iterator, length_limit):
            self.output_tree_lines.append(line)
        if next(iterator, None):
            self.output_message_lines.append(f'... length_limit, {length_limit}, reached, counted:')
        self.output_message_lines.append(f'\n{directories} directories' + (f', {files} files' if files else ''))

    def __str__(self):
        return '\n'.join(self.output_tree_lines + self.output_message_lines)

if __name__ == '__main__':
    test_path = r'test'

    print(FileTree(Path(test_path), include_extensions=['.py']))