import os
import pprint
import Tools


class File:
    def __init__(self, name, lines):
        self.name = name

        self.code_lines = lines.code
        self.comment_lines = lines.comment
        self.whitespace_lines = lines.whitespace


class Folder:
    def __init__(self, dirpath, files, subfolder_names):
        self.name = dirpath.split(os.path.sep)[-1]
        self.dirpath = dirpath
        self.files = files
        self.subfolder_names = subfolder_names

        self.code_lines = 0
        self.comment_lines = 0
        self.whitespace_lines = 0
        for file in self.files:
            self.code_lines += file.code_lines
            self.comment_lines += file.comment_lines
            self.whitespace_lines += file.whitespace_lines

    def add_lines_from_subfolders(self, all_folders):
        for subfolder_name in self.subfolder_names:
            subfolder_path = os.path.join(self.dirpath, subfolder_name)
            subfolder = all_folders[subfolder_path]
            self.code_lines += subfolder.code_lines
            self.comment_lines += subfolder.comment_lines
            self.whitespace_lines += subfolder.whitespace_lines

    # TODO: Improve this! (See TODO below)
    def __repr__(self):
        return ' | '.join(map(str, (self.code_lines, self.comment_lines, self.whitespace_lines)))


def file_count(file_path, file_type='py'):
    if file_type != 'py':
        raise NotImplementedError('Only supports .py files at the moment!')

    lines = Tools.Object(code=0, comment=0, whitespace=0)
    currently_in_docstring = False

    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if currently_in_docstring:
                lines.comment += 1
                if line.endswith('"""'):
                    currently_in_docstring = False
            elif line == '':
                lines.whitespace += 1
            elif line.startswith('#'):
                lines.comment += 1
            elif line.startswith('"""'):
                lines.comment += 1
                if line == '"""' or not line.endswith('"""'):
                    currently_in_docstring = True
            else:
                lines.code += 1

    return lines


def folder_count(folder_path, file_type='py', hidden_files=False, hidden_folders=False, pretty_print=True, return_val=False):
    """
    Counts the number of lines of code in a folder.

    :str folder_path: The path to the folder.
    :str file_type: Optional, a file extension, specifying the kind of file to count the lines of code from. Defaults
        to 'py'.
    :bool hidden_files: Optional, whether to count hidden files. Defaults to False.
    :bool hidden_folders: Optional, whether to count hidden folders. Defaults to False.
    :bool pretty_print: Optional, whether to print out the results in a pretty format at the end. Defaults to True.
    :bool return_val: Optional, whether to return a dictionary of the results. Defaults to False.
    :return: If return_val is truthy, then it is a dictionary, with the keys being the paths to folders, and the values
        being 'Folder' objects as above.
    """

    folders = {}
    for dirpath, subdirnames, filenames in os.walk(folder_path):
        unhidden_subdirnames = []
        for subdirname in subdirnames:
            if not hidden_folders and subdirname.startswith('.'):
                # Hidden folder
                continue
            if subdirname == '__pycache__':
                continue
            unhidden_subdirnames.append(subdirname)
        subdirnames[:] = unhidden_subdirnames

        files = []
        for filename in filenames:
            if not hidden_files and filename.startswith('.'):
                # Hidden file
                continue
            if filename.endswith(file_type):
                file_path = os.path.join(dirpath, filename)
                file_lines = file_count(file_path, file_type)
                file = File(filename, file_lines)
                files.append(file)

        folders[dirpath] = Folder(dirpath, files, subdirnames)

    for folder_name, folder in sorted(folders.items(), key=lambda x: len(x[0]))[::-1]:
        folder.add_lines_from_subfolders(folders)

    # TODO: Improve this! (See TODO above)
    if pretty_print:
        pprint.pprint(folders)

    if return_val:
        return folders


def count(*args, **kwargs):
    """Run folder_count in the current folder"""
    return folder_count('.', *args, **kwargs)


# Test by running it against itself
if __name__ == '__main__':
    count()
