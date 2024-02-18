def run_command(command):
    import subprocess
    '''
    Run any command and output to console. 

    :param command: A string. Command to run.
    :return: Bool for succesful execution
    '''
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read and print output in real-time
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            
        for line in iter(process.stderr.readline, ''):
            print(line, end='')
        
        process.wait()
        
        # Check for errors
        if process.returncode != 0:
            print("Error executing command. Return code: {}".format(process.returncode))
            return False
        
        return True
    
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("Error: {}".format(e))
        return False
    
    except Exception as e:
        print("Error: {}".format(e))
        raise
if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--command", nargs='+', help="The command to run",required=True)

    args=parser.parse_args()
    run_command(args.command)