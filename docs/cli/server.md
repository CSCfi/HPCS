# Server

Using the cli directly isn't recommended, the supported way is through docker's entrypoint.

The server cli allows the user to invoke the server, passing the hpcs server configuration.

```
usage: app.py [-h] [--config CONFIG]

CLI Options

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Configuration file (INI Format) (default: /tmp/hpcs-server.conf)
```

Examples

```bash
# Show the help above
python3 ./server/app.py --help

# Run server, using ~/.config/hpcs-server.conf config file
python3 ./server/app.py --config ~/.config/hpcs-server.conf
```

For more information about the server configuration, see the [associated documentation](https://github.com/CSCfi/HPCS/tree/doc/readme_and_sequence_diagrams/docs/configuration/hpcs-server.md).
