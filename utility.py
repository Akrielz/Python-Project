import os
from os import walk
import math
import struct


def is_in_dir(path, argument, argument_type="file", explanation_file=("<file_target>", "file")):
    """
    Checks if a file or directory is in the given path

    :param path: where the file / directory is located on disk
    :param argument: the target file / directory
    :param argument_type: specifies the type of the file(it can be "dir", "file", "both")
    :param explanation_file: a tuple that wil be used for the error message.

    :return: (found, file_path) - if it has been found or not, and its location
    """
    target = argument

    if argument_type == "file":
        files = get_folder_content(path)[0]
    elif argument_type == "dir":
        files = get_folder_content(path)[1]
    elif argument_type == "both":
        files = get_folder_content(path)[0]
        files.extend(get_folder_content(path)[1])
    else:
        return False

    convention_target = to_convention(target)
    found = False
    file_path = None
    for file in files:
        if to_convention(file) == convention_target:
            found = True
            file_path = path + "\\" + file
            break

    if not found:
        print('Invalid ' + explanation_file[0] + '. There is no such ' + explanation_file[1] + ' as "',
              target, '"\n', sep="")

    return found, file_path


def to_convention(folder_name):
    """
    Converts a file/folder name by making it lower and replacing each '_' with ' '

    :param folder_name: the name over which to apply the convention

    :return: the converted form of the name
    """

    return folder_name.lower().replace("_", " ")


def get_folder_content(path):
    """
    Get the names of all files and directories from the given path

    :param path: where the content is located on disk

    :return: (files, directories) - a tuple with an array of files and an array of directories
    """

    files = []
    directories = []
    for (dir_path, dir_names, file_names) in walk(path):
        files.extend(file_names)
        directories.extend(dir_names)
        break

    return files, directories


def ls(path, arguments):
    """
    This command will print all the files and directories from the given path

    :param path: the current path
    :param arguments: a list with no elements

    :return: nothing
    """

    if len(arguments) != 0:
        print('Invalid Syntax! "ls" does not receive arguments\n')
        return

    files, directories = get_folder_content(path)

    print("Files: ")
    for file in files:
        print('"', file, '"', end=" | ", sep="")
    print("")

    print("Directories: ")
    for directory in directories:
        print('"', directory, '"', end=" | ", sep="")
    print("\n")


def cd(path, arguments):
    """
    This command changes the current path hto the given target directory

    :param path: the current path
    :param arguments: a list with only one element, the target directory's name

    :return: either the current directory if there was an error, or the target directory
    """

    if len(arguments) != 1:
        print('Invalid Syntax! "cd" receives only an argument: "cd <dir_target>"\n')
        return path

    target = arguments[0]

    if target == "..":
        return path[:path.rfind("\\")]

    found, target_path = is_in_dir(path, target, "dir", ("dir_target", "directory"))

    if found:
        return target_path
    return path


def create_archive(path, arguments):
    """
    This command creates an archive with all the files given as arguments

    :param path: the current path
    :param arguments: a list containing the following:
    [archive_name, file[0] | dir[0]], file[1] | dir[1], ...]
    Where
    archive_name is the name of the archive (without extension);
    file[i] | dir[i] is the name of the chosen file / directory;

    :return: nothing
    """

    # create_archive <archive_name> [file[0] | dir[0], file[1] | dir[1] ...]
    if len(arguments) < 2:
        print('Invalid Syntax! "create_archive" needs at least 2 arguments: ')
        print('"create_archive <archive_name> [file[0] | dir[0], file[1] | dir[1], ...]"\n')
        return

    archive_name = arguments[0] + ".aky_zip"

    argument_type = []

    files, directories = get_folder_content(path)
    for argument in arguments[1:]:
        convention_argument = to_convention(argument)

        found = False
        for pos, file in enumerate(files):
            if to_convention(file) == convention_argument:
                argument_type.append(-pos - 1)
                found = True
                break

        if found:
            continue

        for pos, directory in enumerate(directories):
            if to_convention(directory) == convention_argument:
                argument_type.append(pos)
                found = True
                break

        if not found:
            print('Invalid file | dir. There is no such file or directory as "', argument, '"\n', sep="")
            return

    to_archive_files = []
    for i, argument in enumerate(arguments[1:]):
        if argument_type[i] < 0:
            pos = -argument_type[i] - 1
            to_archive_files.append(path + "\\" + files[pos])
        else:
            pos = argument_type[i]
            walk_path = path + "\\" + directories[pos]
            for (dir_path, dir_names, file_names) in walk(walk_path):
                for name in file_names:
                    to_archive_files.append(os.path.join(dir_path, name))

    with open(path + "\\" + archive_name, "wb") as file:
        for file_location in to_archive_files:
            file_size = os.path.getsize(file_location)
            with open(file_location, "rb") as reader:
                file_bytes = reader.read(file_size)

            # print(content)
            file_len = len(file_bytes)
            file_len_log = int(math.ceil(math.log(file_len + 1, 2))) if file_len != 0 else 1

            file_len_bytes = file_len.to_bytes(file_len_log, 'little')
            file_len_log_bytes = file_len_log.to_bytes(1, 'little')

            file_name = file_location[file_location.rfind("\\") + 1:]
            string_bytes = bytes(file_name, 'utf-8')

            string_len = len(string_bytes)
            string_len_log = int(math.ceil(math.log(string_len + 1, 2))) if file_len != 0 else 1

            string_len_bytes = string_len.to_bytes(string_len_log, 'little')
            string_len_log_bytes = string_len_log.to_bytes(1, "little")

            # File Name
            file.write(string_len_log_bytes)
            file.write(string_len_bytes)
            file.write(string_bytes)

            # File Content
            file.write(file_len_log_bytes)
            file.write(file_len_bytes)
            file.write(file_bytes)


def list_content(path, arguments):
    """
    This command lists the content of an archive given as argument

    :param path: the current path
    :param arguments: a list containing a single argument specifying the archive's name (without extension)

    :return: nothing
    """

    if len(arguments) != 1:
        print('Invalid Syntax! "list_content" receives only one argument:')
        print('list_content <archive_dir>\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    archive_size = os.path.getsize(path + "\\" + target_zip)
    with open(path + "\\" + target_zip, "rb") as file:
        while file.tell() < archive_size:
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            print('"', string, '"', end=" | ", sep="")

            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            # file_bytes = file.read(file_len)

            file.seek(file_len, 1)

    print()


def full_unpack(path, arguments):
    """
    This command unpacks every file from an archive given as argument

    :param path: the current path
    :param arguments: a list containing a single argument specifying the archive's name (without extension)

    :return: nothing
    """

    if len(arguments) != 1:
        print('Invalid Syntax! "full_unpack" receives only one argument:')
        print('full_unpack <archive_name>\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    archive_size = os.path.getsize(path + "\\" + target_zip)

    with open(path + "\\" + target_zip, "rb") as file:
        while file.tell() < archive_size:
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            file_bytes = file.read(file_len)

            file_name = string[:string.rfind(".")]
            extension = string[string.rfind("."):]

            i = 0
            while os.path.exists(path + "\\" + file_name + str(i) + extension):
                i += 1

            with open(path + "\\" + file_name + str(i) + extension, "wb") as writer:
                writer.write(file_bytes)


def unpack(path, arguments):
    """
    This command unpacks only the demanded files from an archive given as arguments

    :param path: the current path
    :param arguments: a list containing the following:
    [archive_name, file[0], file[1], ...]
    Where:
    archive_name is the archive's name (without extension);
    file[i] is the file's name from inside the content

    :return: nothing
    """
    if len(arguments) < 2:
        print('Invalid Syntax! "unpack" receives at least two arguments:')
        print('unpack <archive_name> <file_name[0]> <file_name[1]> ...\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    archive_size = os.path.getsize(path + "\\" + target_zip)

    with open(path + "\\" + target_zip, "rb") as file:
        while file.tell() < archive_size:
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            if string not in arguments[1:]:
                file.seek(file_len, 1)
                continue

            file_bytes = file.read(file_len)

            file_name = string[:string.rfind(".")]
            extension = string[string.rfind("."):]

            i = 0
            while os.path.exists(path + "\\" + file_name + str(i) + extension):
                i += 1

            with open(path + "\\" + file_name + str(i) + extension, "wb") as writer:
                writer.write(file_bytes)


def display_help(path, arguments):
    print("display_help")
    pass
