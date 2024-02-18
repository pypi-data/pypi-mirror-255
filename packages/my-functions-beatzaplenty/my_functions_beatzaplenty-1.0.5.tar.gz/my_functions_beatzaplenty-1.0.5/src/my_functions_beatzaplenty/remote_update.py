def remote_update(config):
    from my_functions_beatzaplenty import create_ssh_connection, execute_ssh_command
    '''
    Run Updates on remote machine. .
    
    :param config: A configparser config section
    '''
    if config.get("ssh_port") is None:
        ssh_port = 22
    else:
        ssh_port =  config.get("ssh_port") 
    if config.get('update_script') is None:
        update_script = f"-m my_functions_beatzaplenty.run_updates {config.get('containers')}"
    else:
        update_script = config.get('update_script')
    
    print(f"****************** Updating {config.get('ssh_username')} *******************")
    ssh = create_ssh_connection(config.get('ssh_hostname'), 
                        config.get('ssh_username'),
                        config.get('keyfile'),
                        port=ssh_port)
    execute_ssh_command(ssh, command=f"python3 {update_script}")

if __name__ == "__main__":
    import argparse, os, configparser

    parser=argparse.ArgumentParser()

    parser.add_argument("--config", help="The configparser section to use as config for the execution",required=True)

    args=parser.parse_args()

    # Get script parent dir
    parent_dir = os.path.dirname(os.path.abspath(__file__))

    #Get Configurations
    config = configparser.ConfigParser()
    config.read(f'{parent_dir}/config.ini')


    remote_update(config=config[args.config])