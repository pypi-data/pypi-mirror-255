def is_repo_up_to_date(path):
    import subprocess, os
    '''
    Check if your Git Hub repo is up to date. 
    :param path: THe path to check
    '''
    try:
        cwd = os.getcwd()
        os.chdir(path)
        # Check if the local repository is up to date
        subprocess.run(['git', 'fetch'], check=True)
        result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True, check=True)

        # If the repository is not up to date, pull the changes
        if "Your branch is behind" in result.stdout:
            print("Local repository is not up to date. Pulling changes...")
            subprocess.run(['git', 'pull'], check=True)
            print("Changes pulled successfully.")
        else:
            print("Local repository is up to date.")
        os.chdir(cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import os, argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--path", help="Path to the repo to check. Defaults to the current directory.",
                            required=False,
                            default=os.getcwd())
    
    args=parser.parse_args()
    is_repo_up_to_date(args.path)