def parse_tuple(input):
    '''
    Parse a Tuple from a CSV list. 
    
    :param input: The input to Parse
    
    :return: A Tuple
    '''
    return tuple(k.strip() for k in input[1:-1].split(','))

if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--data", help="Data to convert as CSV",required=True, nargs='+')
    
    args=parser.parse_args()
    parse_tuple(args.data)