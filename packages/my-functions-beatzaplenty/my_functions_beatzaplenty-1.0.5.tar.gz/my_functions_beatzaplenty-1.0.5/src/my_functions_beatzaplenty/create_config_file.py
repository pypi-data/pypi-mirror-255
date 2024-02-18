def create_config_file(config_data, file_path):
    import configparser
    '''
    Create a config file. 
    param: config_data: the data to use in the file as a dictionary EG: {'Section1': {'key1': 'value1','key2': 'value2'},'Section2': {'key3': 'value3','key4': 'value4'}}
    param: file_path: Where to put the file
    '''
    if not isinstance(config_data, dict):
        raise TypeError("config_data must be a dictionary")
    
    config = configparser.ConfigParser()

    for section, settings in config_data.items():
        config[section] = settings

    try:
        with open(file_path, 'w') as config_file:
            config.write(config_file)
        print(f"Config file successfully created at {file_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import argparse, ast, os

    parser=argparse.ArgumentParser()

    parser.add_argument("--path", help="Where to create the config file",required=True)
    parser.add_argument("--data", help="Data to put in the file as a dictionary EG: {'Section1': {'key1': 'value1','key2': 'value2'},'Section2': {'key3': 'value3','key4': 'value4'}}",
                        required=True)

    args=parser.parse_args()

    try:
        config_data = ast.literal_eval(args.data)
    except (ValueError, SyntaxError):
        print("Invalid dictionary format.")
        exit(1)

    file_path = args.path

    if os.path.exists(file_path):
        user_input = input(f"A file already exists at {file_path}. Do you want to continue and replace the file? (yes/no/cancel): ").lower()
        if user_input == 'cancel':
            print("Operation canceled.")
        elif user_input == 'yes':
            create_config_file(config_data, file_path)
        elif user_input == 'no':
            new_path = input("Enter a new path for the config file: ")
            create_config_file(config_data, new_path)
        else:
            print("Invalid input. Operation canceled.")
    else:
        create_config_file(config_data, file_path)