def install_required_modules(requirements):
    import importlib, subprocess, os
    '''
    Install required python modules. 
    
    :param requirements: The requirements.txt to use
    '''
    if not os.path.exists(requirements):
        raise FileNotFoundError(f"The requirements file '{requirements}' does not exist.")

    with open(requirements) as f:
        required_modules = f.read().splitlines()

    for module in required_modules:
        name = module.split("==")[0]

        spec = importlib.util.find_spec(name)
        if spec is None:
            print(f"Module {name} not found. Installing...")
            subprocess.call(['pip', 'install', module])
        else:
            print(f"Module {name} is already installed.")

if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--requirements", help="Path to the requirements.txt file to reference",required=True)
    
    args=parser.parse_args()
    install_required_modules(args.requirements)