def check_outgoing_ports(hostname,ports = [465, 587]):
    import socket
    '''
    Check status of outgoing ports.

    :param hostname: the hostname to query against
    :param ports: the ports to be checked. Default is 465 and 587. Format as an array EG: [465, 587]

    :return: An array of Statuses. Either "Open" or "Closed"
    '''
    results = {}

    for port in ports:
        try:
            with socket.create_connection((hostname, port), timeout=5) as connection:
                results[port] = "Open"
        except (socket.timeout, ConnectionRefusedError):
            results[port] = "Closed"
        except OSError as e:
            if "unreachable" in str(e).lower():
                results[port] = "Closed"
            else:
                # If it's a different OSError, propagate the exception
                raise

    return results

if __name__ == '__main__':
    import argparse

    parser=argparse.ArgumentParser()

    parser.add_argument("--hostname", help="DNS Hostname to check",required=True)
    parser.add_argument("--ports", nargs='+', help="Ports to check. Default is 465 and 587",default=[465,587],required=False)

    args=parser.parse_args()

    status_results = check_outgoing_ports(args.hostname,args.ports)

    for port, status in status_results.items():
        print(f"Port {port}: {status}")