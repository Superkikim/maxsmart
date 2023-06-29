devices = [
    {'sn': 'SWP6023002003697', 'name': 'Salon', 'pname': ['Bravia', 'Ampli', 'HUE', 'Transporter', 'HP', 'Wifi'], 'ip': '172.30.47.165', 'ver': '1.30'}, 
    {'sn': 'SWP1023002004971', 'name': 'Chambre', 'pname': None, 'ip': '172.30.47.99', 'ver': '1.30'}, 
    {'sn': 'SWP6023002002386', 'name': 'Veranda', 'pname': ['Radio', 'Artemide', 'Port3', 'Port4', 'Skull', 'Port6'], 'ip': '172.30.47.162', 'ver': '1.30'}, 
    {'sn': 'SWP6023002002359', 'name': 'Cuisine', 'pname': ['Frigo', 'Hotte', 'port vide 3', 'starfleet', 'PORT5', 'PORT6'], 'ip': '172.30.47.161', 'ver': '1.30'}, 
    {'sn': 'SWP6023002002468', 'name': 'LocalVelo', 'pname': ['Ulysse', 'Congélateur', 'PORT3', 'PORT4', 'PORT5', 'PORT6'], 'ip': '172.30.47.164', 'ver': '1.30'}, 
    {'sn': 'SWP6023002002463', 'name': 'Office', 'pname': ['NUC', 'Stargazer', 'Bureau', 'Lampe', 'Cochrane', 'Ecran'], 'ip': '172.30.47.163', 'ver': '1.30'}
]

def handle_devices(devices):
    prepared_devices = []
    for device in devices:
        sn, ip, name, pname = device['sn'], device['ip'], device['name'], device['pname']  # assuming device is a tuple or list
        device_dict = {
            "device_unique_id": sn,
            "device_ip": ip,
            "device_name": name,
            "ports": {
                "master": {
                    "port_id": 0,
                    "port_name": "Master"
                },
                "individual_ports": []
            }
        }
        if pname is None:
            device_dict["ports"]["individual_ports"].append({"port_id": 1, "port_name": "Port 1"})
        else:
            device_dict["ports"]["individual_ports"] = [
                {"port_id": i+1, "port_name": pname[i]} for i in range(len(pname))
            ]
        prepared_devices.append(device_dict)
    return prepared_devices

transformed_data = handle_devices(devices)
print(transformed_data)
