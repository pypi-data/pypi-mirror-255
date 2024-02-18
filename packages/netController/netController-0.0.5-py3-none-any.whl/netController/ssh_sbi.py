from netmiko import ConnectHandler
from nas_inventory import get_host

allowed_commands = ["show access-lists", "show interfaces", "show ip route", "show ip bgp summary","show configuration","show running-config"]

def get_netmiko_connection(hostname:str):
    """
    Establishes a Netmiko SSH connection to a network device.

    Args:
        hostname (str): The hostname or IP address of the network device.

    Returns:
        net_connect (object): The Netmiko SSH connection object.

    Raises:
        Exception: If there is an error establishing the connection.

    """
    host = get_host(hostname=hostname)
    device_params = {
                "host": host["ip"],
                "username": host["user"],
                "password": host["password"],
                "device_type": "vyos" if host["vendor"] == "VyOS" else "cisco_ios"
            }
    try:
        net_connect = ConnectHandler(**device_params)
        return net_connect
    except Exception as e:
        print(f'Error: {e}')
        return None

def send_command(net_connect, command:str):
    """
    Sends a command to a network device using the provided Netmiko connection.

    Args:
        net_connect (Netmiko connection): The Netmiko connection object.
        command (str): The command to be sent to the network device.

    Returns:
        str: The output of the command execution.

    Raises:
        None

    """
    if command not in allowed_commands:
        return "Command not allowed"
    #net_connect = get_netmiko_connection(hostname=hostname)
    #if net_connect:
    try:
        output = net_connect.send_command(command)
        return output
    except Exception as e:
        print(f'Error: {e}')
    return None

def get_backup(hostname: str):
    """
    Retrieves the backup configuration from a network device.

    Args:
        hostname (str): The hostname or IP address of the network device.

    Returns:
        str: The backup configuration if successful, otherwise an error message.
    """
    net_connect = get_netmiko_connection(hostname)
    if net_connect:
        if net_connect.device_type == "vyos":
            output = send_command(net_connect, "show configuration")
        elif net_connect.device_type == "cisco":
            output = send_command(net_connect, "show running-config")
        if output:
            return output
        else:
            return "Error retrieving backup"
    else:
        return "Error connecting to the device"
