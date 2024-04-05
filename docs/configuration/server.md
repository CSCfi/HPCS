# Client

Client's configuration has to respect `ini` configuration format and essentially compiles informations for the client to connect to servers services.

## Example configuration :

```ini
[spire-server]
address = "localhost"
port = 8081
trust-domain = hpcs
pre-command = ""
spire-server-bin = spire-server
socket-path = /var/run/sockets/server/api.sock

[spire-agent]
spire-agent-socket = /tmp/spire-agent/public/api.sock
hpcs-server-spiffeid = spiffe://hpcs/hpcs-server/workload

[vault]
url = http://vault-host:10297
server-role = hpcs-server
```

## Reference

### `spire-server` 

This section describes the connection to the spire-server
- `address` : address of the spire-server
- `port` : port nomber on which spire-server api is exposed
- `trust-domain` : `trust-domain` of the spire-server (from spire-server configuration or hpcs administration can provide it to you)
- `spire-server` commands are executed directly in a subshell in order to cover various type of setups, these configs allow user to change the final command :
  - `pre-command` :  text to add before running spire-server cli command
  - `spire-server-bin` :  path to spire-server binary
  - `socket-path` :  path to spire-server socket (will be append after `-socketPath`)

### `spire-agent`

This section describes the spire-agent setup to allow hpcs-server to use it to get and validate SVIDs
- `spire-agent-socket` : path to spire agent socket, used to create spire-agent client connecting via the socket
- `hpcs-server-spiffeid` : spiffeID identifying the hpcs-server workload, in general : `spiffe://hpcs/hpcs-server/workload`

### `vault`

This section describes the vault
- `url` : complete base url to the vault
- `server-role` : name of the role registered into the vault to create and update vault policies/roles and bound to the `hpcs-server-spiffeid`
