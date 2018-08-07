import json
import os
import tools


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
        """Goes through all of this folder's immediate subfolders and adds on their current counts for their lines of
        code/comment/whitespace."""

        for subfolder_name in self.subfolder_names:
            subfolder_path = os.path.join(self.dirpath, subfolder_name)
            subfolder = all_folders[subfolder_path]
            self.code_lines += subfolder.code_lines
            self.comment_lines += subfolder.comment_lines
            self.whitespace_lines += subfolder.whitespace_lines


def file_count(file_path):
    """Counts the lines of Python code, comments and whitespace in a file located at :file_path:."""

    line_count = tools.Object(code=0, comment=0, whitespace=0)
    currently_in_docstring = False

    with open(file_path, 'r') as f:
        if file_path.endswith('.py'):
            lines = f.readlines()
        elif file_path.endswith('ipynb'):
            lines = []
            cells = json.load(f)['cells']
            for cell in cells:
                if cell['cell_type'] == 'code':
                    lines.extend(cell['source'])
        else:
            raise RuntimeError("Unrecognised file type at '{}'".format(file_path))

        for line in lines:
            line = line.strip()
            if currently_in_docstring:
                line_count.comment += 1
                if line.endswith('"""'):
                    currently_in_docstring = False
            elif line == '':
                line_count.whitespace += 1
            elif line.startswith('#'):
                line_count.comment += 1
            elif line.startswith('"""'):
                line_count.comment += 1
                if line == '"""' or not line.endswith('"""'):
                    currently_in_docstring = True
            else:
                line_count.code += 1

    return line_count


def count(folder_path='.', hidden_files=False, hidden_folders=False, print_result=True, include_zero=False,
          add_subfolders=True):
    """
    Counts the number of lines of code in a folder.

    :str folder_path: The path to the folder. Defaults to the current folder.
    :bool hidden_files: Optional, whether to count hidden files. Defaults to False.
    :bool hidden_folders: Optional, whether to count hidden folders. Defaults to False.
    :bool print_result: Optional, whether to print out the results in a pretty format at the end. Defaults to True.
    :bool include_zero: Optional, whether to include lines containing zero lines of code.
    :bool add_subfolders: Optional, whether to include the amount of code in subfolders when stating the amount of lines
        of code/comment/whitespace in a folder.
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
            if filename.endswith('.py') or filename.endswith('.ipynb'):
                file_path = os.path.join(dirpath, filename)
                file_lines = file_count(file_path)
                file = File(filename, file_lines)
                files.append(file)

        folders[dirpath] = Folder(dirpath, files, subdirnames)

    if add_subfolders:
        # Go through in order of length of path, as a string, from longest to shortest. This guarantees that we evaluate
        # all deeper folders before we evaluate shallower ones.
        for folder_name, folder in sorted(folders.items(), key=lambda x: len(x[0]))[::-1]:
            folder.add_lines_from_subfolders(folders)

    if print_result:
        max_folder_loc = len("Folder location")
        max_code = len("Code")
        max_comment = len("Comment")
        max_whitespace = len("Whitespace")
        max_all = len("Total")
        for folder_loc, folder in folders.items():
            if include_zero or folder.code_lines != 0:
                max_folder_loc = max(max_folder_loc, len(folder_loc))
                max_code = max(max_code, tools.num_digits(folder.code_lines))
                max_comment = max(max_comment, tools.num_digits(folder.comment_lines))
                max_whitespace = max(max_whitespace, tools.num_digits(folder.whitespace_lines))
                max_all = max(max_all,
                              tools.num_digits(folder.code_lines + folder.comment_lines + folder.whitespace_lines))
        print_str = ("{:<%s} | {:%s} | {:%s} | {:%s} | {:%s}" % (max_folder_loc, max_code, max_comment, max_whitespace,
                                                                max_all)
                     ).format("Folder location", "Code", "Comment", "Whitespace", "Total")
        print(print_str)
        print("-" * (max_folder_loc + 1) + "+" + "-" * (max_code + 2) + "+" + "-" * (max_comment + 2) + "+" +
              "-" * (max_whitespace + 2) + "+" + "-" * (max_all + 1))
        for folder_loc, folder in folders.items():
            if include_zero or folder.code_lines != 0:
                print_str = ("{:<%s} | {:%s} | {:%s} | {:%s} | {:%s}" % (max_folder_loc, max_code, max_comment,
                                                                         max_whitespace, max_all)
                             ).format(folder_loc, folder.code_lines, folder.comment_lines, folder.whitespace_lines,
                                      folder.code_lines + folder.comment_lines + folder.whitespace_lines)
                print(print_str)

    return folders

    
if __name__ == '__main__':
    count()
