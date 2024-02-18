def create_ssh_connection(hostname, username, keyfile, max_retries=10, retry_interval=5, port=22):
    import paramiko, time
    '''
    Create an SSH connection. 
    
    :param hostname: the hostname to connect to
    :param username: the username to connect as
    :param keyfile: the keyfile to use in the conneciton attempt. Auto discovers any keys in $HOME/.ssh
    :param max_retries: default is 10
    :param retry_interval: Specified in seconds. Default is 5 seconds.
    :param port: Port to connect to. Default is 22
    
    :return: A paramiko.SSHClient object that can be used to execute commands
    '''
    retries = 0
    while retries < max_retries:
        try:
            # Create an SSH client
            ssh = paramiko.SSHClient()
            # Automatically add the server's host key (this is insecure, see comments below)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            print(f"Connecting to {hostname} with username {username} and keyfile {keyfile}")
            # Connect to the server with the specified keyfile
            ssh.connect(hostname, username=username, key_filename=keyfile,port=port)

            return ssh

        except Exception as e:
            print(f"Error creating SSH connection: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)

    raise RuntimeError(f"Failed to create SSH connection after {max_retries} attempts.")

if __name__ == "__main__":
    import argparse, os

    parser=argparse.ArgumentParser()

    parser.add_argument("--hostname", help="DNS Hostname or IP address to connect to",required=True)
    parser.add_argument("--username", help="Username to connect with",required=True)
    parser.add_argument("--keyfile", help=f"public keyfile to use for authentication. Default is {os.environ['HOME']}/.ssh/id_rsa.pub",default=f"{os.environ['HOME']}/.ssh/id_rsa.pub")
    parser.add_argument("--max_retries", help="Maximum number of retries. Default is 10",default=10)
    parser.add_argument("--retry_interval", help="Time to wait in seconds between connection attempts. Default is 5 seconds",default=5)
    parser.add_argument("--port", help="Port to connect to. Default is 22",default=22)

    args=parser.parse_args()

    create_ssh_connection(hostname=args.hostname,
                                username=args.username,
                                keyfile=args.keyfile,
                                max_retries=args.max_retries,
                                retry_interval=args.retry_interval,
                                port=args.port)
    