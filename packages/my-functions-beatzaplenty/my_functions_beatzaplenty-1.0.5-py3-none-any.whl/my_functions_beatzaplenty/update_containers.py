#!/usr/bin/env python3


def main(services):
    from my_functions_beatzaplenty import run_command
    from datetime import datetime
    """
    Update Docker Containers.

    :param services: An array of service names to be updated
    """
    try:
        now = datetime.now()
        now_string = now.strftime("%d/%m/%Y %H:%M")
        print(f'******** Update started: {now_string} *****************')
        for service in services:
            path = f"/docker/{service}/docker-compose.yml"
            pull_command = ["docker-compose", "--file", path, "pull"]
            up_command = ["docker-compose", "--file", path, "up", "-d"]
            print(f'************* Updating {service} ************')
            if not run_command.run_command(pull_command):
                continue
            
            if not run_command.run_command(up_command):
                continue
        prune_command = ["docker","system","prune","-f"]
        run_command.run_command(prune_command)

    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--containers", nargs='+', help="Containers to update",required=True)

    args=parser.parse_args()
    main(args.containers)  # Replace with your list of services