def check_command_exists(command):
    import subprocess, shlex    
    '''
    Check if a command exists. 

    :param command: The command to test
    
    :return: Bool indicating if the command exists
    '''
    try:
        subprocess.run(shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--command", help="The command to check for",required=True)
    
    args=parser.parse_args()
    result = check_command_exists(args.command)
    if result is True:
        print(f"The '{args.command}' command was found.")
    else:
        print(f"The '{args.command}' command was not found.")