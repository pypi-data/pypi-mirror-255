def execute_ssh_command(ssh, command):
    '''
    Execute a command via SSH and output to console. 
    
    :param ssh: A paramiko.SSHClient object created using the create_ssh_connection function
    :param command: The command to run
    '''
    try:
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.exec_command(command)

        # Print each line of the command output in real-time
        while True:
            if channel.recv_ready():
                line = channel.recv(1024).decode()
                if not line:
                    break
                print(line.strip())

            if channel.exit_status_ready():
                break

        # Print any errors
        error_output = channel.recv_stderr(1024).decode()
        if error_output:
            print(f"Error: {error_output}")
        return channel.recv_exit_status()
    
    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the SSH connection
        ssh.close()

if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--connection", help="A paramiko.SSHClient object created using the create_ssh_connection function",required=True)
    parser.add_argument("--command", nargs='+', help="The command to run",required=True)

    args=parser.parse_args()
    execute_ssh_command(ssh=args.connection,command=args.command)