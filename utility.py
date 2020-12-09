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

    # Gets the content that matches the type
    if argument_type == "file":
        files = get_folder_content(path)[0]
    elif argument_type == "dir":
        files = get_folder_content(path)[1]
    elif argument_type == "both":
        files = get_folder_content(path)[0]
        files.extend(get_folder_content(path)[1])
    else:
        return False

    # Searches through the gathered files to sees if the content matches
    convention_target = to_convention(target)
    found = False
    file_path = None
    for file in files:
        if to_convention(file) == convention_target:
            found = True
            file_path = path + "\\" + file
            break

    # Raises log error in case that the input was invalid
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

    # Checks if the arguments are valid
    if len(arguments) != 0:
        print('Invalid Syntax! "ls" does not receive arguments\n')
        return

    # Gets the content
    files, directories = get_folder_content(path)

    # Prints the content
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

    # Checks if the arguments are valid
    if len(arguments) != 1:
        print('Invalid Syntax! "cd" receives only an argument: "cd <dir_target>"\n')
        return path

    target = arguments[0]

    # Special case if the user wants to go backwards
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

    # Checks if the arguments are valid
    if len(arguments) < 2:
        print('Invalid Syntax! "create_archive" needs at least 2 arguments: ')
        print('"create_archive <archive_name> [file[0] | dir[0], file[1] | dir[1], ...]"\n')
        return

    archive_name = arguments[0] + ".aky_zip"

    argument_type = []

    # Gets the current files and directories
    files, directories = get_folder_content(path)
    for argument in arguments[1:]:
        convention_argument = to_convention(argument)

        # Checks if the given name is a file and saves its position
        found = False
        for pos, file in enumerate(files):
            if to_convention(file) == convention_argument:
                # saves the files position in the interval (-INF, -1]
                argument_type.append(-pos - 1)
                found = True
                break

        if found:
            continue

        # Checks if the given name is a directory and saves its position
        for pos, directory in enumerate(directories):
            if to_convention(directory) == convention_argument:
                # saves the files position in the interval [0, INF)
                argument_type.append(pos)
                found = True
                break

        # Raises log error and stops from further execution
        if not found:
            print('Invalid file | dir. There is no such file or directory as "', argument, '"\n', sep="")
            return

    # Gets all the files directly from the saves positions and
    # walks in the directories to grab all files recursively
    to_archive_files = []
    for i, argument in enumerate(arguments[1:]):

        # It is a file based on its saved position
        if argument_type[i] < 0:
            # Restores the saved position and saves the file
            pos = -argument_type[i] - 1
            to_archive_files.append(path + "\\" + files[pos])

        # It is a directory
        else:
            pos = argument_type[i]
            # Grab all the files from the given directories
            walk_path = path + "\\" + directories[pos]
            for (dir_path, dir_names, file_names) in walk(walk_path):
                for name in file_names:
                    to_archive_files.append(os.path.join(dir_path, name))

    # Prepares the archive to be written
    with open(path + "\\" + archive_name, "wb") as file:

        # Goes through the location of each file that needs to be saved in the archive
        for file_location in to_archive_files:

            # Reads the file size to get all the bytes at once
            file_size = os.path.getsize(file_location)
            with open(file_location, "rb") as reader:
                file_bytes = reader.read(file_size)

            # Gets the size of the read content
            file_len = len(file_bytes)

            # Gets the number of bytes that it is required to write the size
            file_len_log = int(math.ceil(math.log(file_len + 1, 2))) if file_len != 0 else 1

            # Gets the bytes information that needs the be written
            file_len_bytes = file_len.to_bytes(file_len_log, 'little')
            file_len_log_bytes = file_len_log.to_bytes(1, 'little')

            # Converts the file's name into bytes
            file_name = file_location[file_location.rfind("\\") + 1:]
            string_bytes = bytes(file_name, 'utf-8')

            # Get the size of the file's name
            string_len = len(string_bytes)

            # Gets the number of bytes that is is required to write the size
            string_len_log = int(math.ceil(math.log(string_len + 1, 2))) if file_len != 0 else 1

            # Gets the bytes information that needs the be written
            string_len_bytes = string_len.to_bytes(string_len_log, 'little')
            string_len_log_bytes = string_len_log.to_bytes(1, "little")

            # Writes the details about the file's name
            file.write(string_len_log_bytes)
            file.write(string_len_bytes)
            file.write(string_bytes)

            # Writes the details about the file's content
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

    # Checks if the arguments are valid
    if len(arguments) != 1:
        print('Invalid Syntax! "list_content" receives only one argument:')
        print('list_content <archive_dir>\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    # Checks if the archive exists
    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    # Gets the size of the file to know when to stop iterating
    archive_size = os.path.getsize(path + "\\" + target_zip)

    # Opens the archive
    with open(path + "\\" + target_zip, "rb") as file:

        # Checks if it covered all the files from the archive
        while file.tell() < archive_size:

            # Reads the first byte that will tell how many bytes needs to be read for the file's name length
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            # Reads the file's name length to know how many bytes needs to be read for the file's name
            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            # Reads the file's name
            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            # Prints the file's name
            print('"', string, '"', end=" | ", sep="")

            # Reads the first byte that will tell how many bytes needs to be read for the file's content length
            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            # Reads the file's content length to know how many bytes needs to be read for the file's content
            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            # Moves the cursor over the file's content, since we do not need this information
            file.seek(file_len, 1)

    print()


def full_unpack(path, arguments):
    """
    This command unpacks every file from an archive given as argument

    :param path: the current path
    :param arguments: a list containing a single argument specifying the archive's name (without extension)

    :return: nothing
    """

    # Checks if the arguments are valid
    if len(arguments) != 1:
        print('Invalid Syntax! "full_unpack" receives only one argument:')
        print('full_unpack <archive_name>\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    # Checks if the archive exists
    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    # Gets the size of the file to know when to stop iterating
    archive_size = os.path.getsize(path + "\\" + target_zip)

    # Opens the archive
    with open(path + "\\" + target_zip, "rb") as file:

        # Checks if it covered all the files from the archive
        while file.tell() < archive_size:

            # Reads the first byte that will tell how many bytes needs to be read for the file's name length
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            # Reads the file's name length to know how many bytes needs to be read for the file's name
            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            # Reads the file's name
            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            # Reads the first byte that will tell how many bytes needs to be read for the file's content length
            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            # Reads the file's content length to know how many bytes needs to be read for the file's content
            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            # Reads the file's content
            file_bytes = file.read(file_len)

            # Splits the file's name from the file's extension
            file_name = string[:string.rfind(".")]
            extension = string[string.rfind("."):]

            # Makes sure that it doesn't override any existent file
            i = 0
            while os.path.exists(path + "\\" + file_name + str(i) + extension):
                i += 1

            # Extracts the file
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

    # Checks if the arguments are valid
    if len(arguments) < 2:
        print('Invalid Syntax! "unpack" receives at least two arguments:')
        print('unpack <archive_name> <file_name[0]> <file_name[1]> ...\n')
        return

    target_zip = arguments[0] + ".aky_zip"

    # Checks if the archive exists
    found = is_in_dir(path, target_zip, "file", ("zip_target", "archive"))[0]

    if not found:
        return

    # Gets the size of the file to know when to stop iterating
    archive_size = os.path.getsize(path + "\\" + target_zip)

    # Opens the archive
    with open(path + "\\" + target_zip, "rb") as file:

        # Checks if it covered all the files from the archive
        while file.tell() < archive_size:

            # Reads the first byte that will tell how many bytes needs to be read for the file's name length
            string_len_log_bytes = file.read(1)
            string_len_log = struct.unpack('<B', string_len_log_bytes)[0]

            # Reads the file's name length to know how many bytes needs to be read for the file's name
            string_len_bytes = file.read(string_len_log)
            string_len = sum(string_len_bytes[i] << (i * 8) for i in range(string_len_log))

            # Reads the file's name
            string_bytes = file.read(string_len)
            string = string_bytes.decode("utf-8")

            # Reads the first byte that will tell how many bytes needs to be read for the file's content length
            file_len_log_bytes = file.read(1)
            file_len_log = struct.unpack('<B', file_len_log_bytes)[0]

            # Reads the file's content length to know how many bytes needs to be read for the file's content
            file_len_bytes = file.read(file_len_log)
            file_len = sum(file_len_bytes[i] << (i * 8) for i in range(file_len_log))

            # Checks if it is within the given files to extract or not
            if string not in arguments[1:]:
                # If it is not, then we skip over that file
                file.seek(file_len, 1)
                continue

            # If it is in, it extracts its content
            file_bytes = file.read(file_len)

            # Splits the file's name from the file's extension
            file_name = string[:string.rfind(".")]
            extension = string[string.rfind("."):]

            # Makes sure that it doesn't override any existent file
            i = 0
            while os.path.exists(path + "\\" + file_name + str(i) + extension):
                i += 1

            # Extracts the file
            with open(path + "\\" + file_name + str(i) + extension, "wb") as writer:
                writer.write(file_bytes)


def display_help(path, arguments):
    print("display_help")
    pass
