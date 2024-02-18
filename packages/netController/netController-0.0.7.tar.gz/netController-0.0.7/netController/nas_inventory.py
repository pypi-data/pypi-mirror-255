from mat import Inventory, crypto

def get_credentials(mathost):
    """
    Retrieves the credentials for a given mathost.

    Args:
        mathost (dict): The mathost dictionary containing the credentials.

    Returns:
        tuple: A tuple containing the username and password.
    """
    if "ansible_user" in mathost:
        user = mathost["ansible_user"]
        password = crypto.aes256.MATCipher().decrypt(mathost["ansible_ssh_pass"])
    else:
        if "storedCredentials" in mathost:
            credential_base = mathost["storedCredentials"]["data"]
        elif "matcredentials" in mathost["vendorModel"]["data"]:
            credential_base = mathost["vendorModel"]["data"]["matcredentials"]["data"]
        elif "matcredentials" in mathost["networkRole"]["data"]:
            credential_base = mathost["networkRole"]["data"]["matcredentials"]["data"]
        else:
            return "",""
                
        user = credential_base["username"]
        password = crypto.aes256.MATCipher().decrypt(credential_base["password"])
                
    return user,password

def get_host(ne_id="", ip="", hostname="", credential_name=""):
    """
    Retrieves information about a network host based on the provided parameters.

    Args:
        ne_id (str): The ID of the network element.
        ip (str): The IP address of the network host.
        hostname (str): The hostname of the network host.
        credential_name (str): The name of the credential to be used.

    Returns:
        dict: A dictionary containing the following information about the network host:
            - ip (str): The management IP address.
            - hostname (str): The hostname.
            - vendor (str): The vendor of the network host.
            - model (str): The model of the network host.
            - networkRole (str): The network role of the network host.
            - ne_id (str): The network element ID.
            - freeze (bool): The freeze status of the network host.
            - Additional tags and environment variables associated with the network host.
    Raises:
        Exception: If ne_id, ip, or hostname is not provided.
        Exception: If the specified query is not found in the Network Elements.
        Exception: If the specified credential name is not found in the Network Credentials.
    """
    # Function implementation...    
    if ne_id:
        query=f'data.networkElementId={ne_id}'
    elif ip:
        query=f'data.managementIp={ip}'
    elif hostname:
        query=f'data.hostname={hostname}'
    else:
        raise Exception("ne_id, ip or hostname needed.")
    
    host = {}
    inv = Inventory()
    mathost = inv.get("mathost", query=query)
    
    if mathost:
        mathost = mathost[0]["data"]
    else:
        raise Exception(f"query: {query} not found in Network Elements. (Check if it is enabled).")
        
    host = {
        "ip": mathost["managementIp"],
        "hostname": mathost["hostname"],
        "vendor": mathost["vendorModel"]["data"].get("vendor",""),
        "model": mathost["vendorModel"]["data"].get("model",""),
        "networkRole": mathost["networkRole"]["data"]["name"],
        "ne_id": mathost["networkElementId"],
        "freeze": mathost["freeze"]
    }
    
    # Recorro los tags del NE, y los agrego al dict host
    for tag in mathost["tags"]: 
        host[tag["key"]] = tag["value"]
    
    # Recorro las vars del NE, y los agrego al dict host    
    for env_var in mathost["env_vars"]: 
        host[env_var["name"]] = env_var["value"]
    
    
    # Manejo de credenciales, si me proveen una credencial tomo esa, sino uso las definidas en el inventario (teniendo en cuenta las jerarquias)
    if not credential_name:        
        host["user"],host["password"] = get_credentials(mathost)
    else:
        matcredentials = inv.get("matcredentials", query=f"data.credentialName={credential_name}")
        if matcredentials:
            matcredentials = matcredentials[0]["data"]
        else:
            raise Exception(f"Credential Name: {credential_name} not found in Network Credentials.")
            
        host["user"] = matcredentials["username"]
        host["password"] = crypto.aes256.MATCipher().decrypt(matcredentials["password"])
        
    return host
