from utility import *


def get_input():
    current_directory = os.getcwd()
    while True:
        print(current_directory, ">>", end=" ")
        command = input()
        command_arguments = command.split()

        if len(command_arguments) == 0:
            continue

        main_command = command_arguments[0]

        if main_command == "ls":
            ls(current_directory, command_arguments[1:])

        elif main_command == "cd":
            current_directory = cd(current_directory, command_arguments[1:])

        elif main_command == "create_archive":
            create_archive(current_directory, command_arguments[1:])

        elif main_command == "list_content":
            list_content(current_directory, command_arguments[1:])

        elif main_command == "full_unpack":
            full_unpack(current_directory, command_arguments[1:])

        elif main_command == "unpack":
            unpack(current_directory, command_arguments[1:])

        elif main_command == "help":
            display_help(current_directory, command_arguments[1:])

        elif main_command == "exit":
            break

        else:
            print('Command not recognised. Consider typing "help".')


if __name__ == '__main__':
    get_input()
