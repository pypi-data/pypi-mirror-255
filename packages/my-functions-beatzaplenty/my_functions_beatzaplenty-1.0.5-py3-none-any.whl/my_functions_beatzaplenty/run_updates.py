def run_updates(containers):
    import platform
    from my_functions_beatzaplenty import update_containers, run_command, check_command_exists
    '''
    Run updates on machine. Runs all apt, flatpak and spice updates and updates given containers. 
    
    :param containers: the containers to update
    '''
    os_release_id = platform.freedesktop_os_release().get('ID')

    update_commands = [('sudo','apt-get','update'),
                        ('sudo','apt-get','upgrade','-y'),
                        ('sudo','apt-get','autoremove','-y')]
                # Add flatpaks and spices if mint
    if os_release_id == "linuxmint":
        update_commands+=[('flatpak','update','-y'),
                        ('sudo','flatpak','remove','--unused','-y'),
                        ('cinnamon-spice-updater','--update-all')]
    try:
        for cmd in update_commands:
            run_command(cmd)
        if check_command_exists("docker"):
            update_containers.main(containers)
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--containers", nargs='+', help="The containers to update",required=False)

    args=parser.parse_args()
    run_updates(args.containers)