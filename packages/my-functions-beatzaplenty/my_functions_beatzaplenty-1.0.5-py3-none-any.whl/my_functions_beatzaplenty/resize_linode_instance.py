import argparse, threading, configparser, os
import linode_api4 as linode_api
import my_linode_beatzaplenty as linode

def main(config=None,arg_direction=None,arg_monitor=False):
    """
    Resize Linode Instance.

    :param config: A configparser object containing the following config items:
                    api_key: api key for linde authentication
                    linode_name: Linode instance name to target
    :param arg_direction: must be "--up" or "--down"
    :param arg_monitor: Bool to monitor and wait for completion.
    """

    ################## Linode Data Aquisition ###########################
    try:
        api_client = linode_api.LinodeClient(os.environ['LINODE_API_KEY'])
        linodes = api_client.linode.instances(linode_api.Instance.label == config.get('linode_name'))
    except linode_api.errors.ApiError as e:
        print(f"Error during Linode API call: {e}")
    try:
        if len(linodes) == 1:
            linode_instance = linodes[0]
        else:
            raise ValueError(f"linode with label {config.get('linode_name')} not found")
    except ValueError as e:
        exit(e)

####################   Parse Command line arguments ##############################
    parser=argparse.ArgumentParser()
    parser.add_argument("--up", action='store_true')
    parser.add_argument("--down", action='store_true')
    parser.add_argument("--monitor", action='store_true')
    args=parser.parse_args()

    if args.up is True or arg_direction == '--up':
        arg_direction = config.get('big_type')
    if args.down is True or arg_direction == '--down':
        arg_direction = config.get('small_type')
    if args.monitor or arg_monitor:
        arg_monitor = True
    else:
        arg_monitor = False
    
    #################   Perform Actions #####################
    try:
        if arg_direction is not None:
            # create event poller
            event_poller = api_client.polling.event_poller_create('linode', 
                                                                  'linode_resize',
                                                                  entity_id=linode_instance.id)
            if arg_direction != linode_instance.type.id:
                # Resize instance
                linode_instance.resize(arg_direction, allow_auto_disk_resize=False)
                #Get type label for output string
                type_label = linode.get_type_label(api_client,arg_direction)
                # print resize message
                print(f"Linode instance {linode_instance.id} with label '{linode_instance.label}' has been resized to '{type_label}'.")
                # create polling thread
                polling_thread = threading.Thread(target=event_poller.wait_for_next_event_finished, daemon=True)
            else:
                # set type label for output string
                type_label = linode.get_type_label(api_client,arg_direction)
                # Print no action take message
                print(f"Linode instance {linode_instance.id} with label '{linode_instance.label}' is already sized to '{type_label}'. No Resize Performed.")
                # Create polling thread
                polling_thread = threading.Thread(target=api_client.polling.wait_for_entity_free, args=("linode",linode_instance.id), daemon=True)
        else:
            #create polling thread
            polling_thread = threading.Thread(target=api_client.polling.wait_for_entity_free, args=("linode",linode_instance.id), daemon=True)
    except linode_api.errors.ApiError as e:
        print(f"Error during Linode API call: {e}")

    if arg_monitor:
        linode.wait_for_completion(polling_thread)
        linode.wait_for_instance_state(api_client,linode_instance.id)

if __name__ == "__main__":
       ################  Static Variables ####################

        # Get script parent dir
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    config = configparser.ConfigParser()
    config.read(f'{parent_dir}/config.ini')
    config = config['default']
    main(config)