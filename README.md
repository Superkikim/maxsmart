# MaxSmart

MaxSmart is a Python module for operating network-connected power strips. It provides functionality to turn on/off sockets, check their state, and retrieve power consumption data.

## Installation

You can install MaxSmart via pip from PyPI:

```shell
pip install maxsmart
```

## Usage

First, you need to import the MaxSmart module and create a MaxSmart object:

```python
from maxsmart import MaxSmart

power_strip = MaxSmart('ip_address', 'sn')
```

Replace `'ip_address'` and `'sn'` with the IP address and the serial number of your power strip, respectively.

Here are a few examples of how you can use the methods of the `MaxSmart` object to control your power strip:

```python
# Turn on socket 1
power_strip.turn_on(1)

# Turn off socket 1
power_strip.turn_off(1)

# Check the state of all sockets
state = power_strip.check_state()
print(state)  # [0, 1, 0, 1, 0, 1] for example

# Check the state of socket 1
socket_state = power_strip.check_port_state(1)
print(socket_state)  # 0 for example

# Get the hourly data of socket 1
hourly_data = power_strip.get_hourly_data(1)
print(hourly_data)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update the tests as appropriate.

## License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
```

Notez que la section "License" fait référence à un fichier `LICENSE` dans le même répertoire que le fichier `README.md`. Vous pouvez cliquer sur le lien pour voir le contenu du fichier de licence. Assurez-vous de créer ce fichier et de copier le texte de la licence MIT à l'intérieur, comme je l'ai expliqué dans mon message précédent.