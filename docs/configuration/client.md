# Client

Client's configuration has to respect `ini` configuration format and essentially compiles informations for the client to connect to servers services.

## Example configuration :

```ini
[spire-server]
address = localhost
port = 31147
trust-domain = hpcs

[hpcs-server]
url = http://localhost:10080

[vault]
url = http://localhost:8200

[supercomputer]
address = lumi.csc.fi
username = etellier
```

## Reference

### `spire-server`

This section describes the connection to the spire-server
- `address` : address of the spire-server
- `port` : port nomber on which spire-server api is exposed
- `trust-domain` : `trust-domain` of the spire-server (from spire-server configuration or hpcs administration can provide it to you)

### `hpcs-server`

This section describes the hpcs-server
- `url` : complete base url to the hpcs server api

### `vault`

This section describes the vault
- `url` : complete base url to the vault


### `supercomputer`

This section describes the supercomputer to run jobs on
- `address` : the address to the supercomputer login-node
- `username` : the user to use to connect to the supercomputer
