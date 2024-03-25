# HPCS High Performance Computing Secured

## Main goal

### Project

This partnership project involving CSC and Hewlett Packard Enterprise aims to enable HPC users to run secured jobs. It provides tools to enable anyone running secured jobs with encrypted data and specific confidential containers on a supercomputing site, leveraging (non exhaustively) :

- [SPIFFE/SPIRE](https://github.com/spiffe/spire)
- [Hashicorp Vault](https://github.com/hashicorp/vault)
- [Singularity / Apptainer encryption](https://github.com/apptainer/apptainer)
- [age encryption](https://github.com/FiloSottile/age)

### Architecture

In-depth architecture documentation is available [here](https://github.com/CSCfi/HPCS/docs/architecture)

## Demonstration

[![asciicast](https://asciinema.org/a/PWDzxlaVQmfGjbh30KKNTRO1f.svg)](https://asciinema.org/a/PWDzxlaVQmfGjbh30KKNTRO1f)

## Quickstart

### Client

Assuming that the HPCS server is setup. (See [Server](#Server)).

To start using HPCS Client, the supported method has two requirements, docker and docker-compose.

#### Pulling images

Start by pulling the three images.

```bash
docker pull ghcr.io/cscfi/hpcs/[container/data/job]-prep:['branch-name'/latest]
```

```bash
docker pull ghcr.io/cscfi/hpcs/container-prep:latest
docker pull ghcr.io/cscfi/hpcs/data-prep:latest
docker pull ghcr.io/cscfi/hpcs/job-prep:latest
```

#### Configuring the client

Informations about Spire-Server, HPCS-Server and Vault depends on the server installation and the setup choices made on it's side. If you don't know those informations, please contact your HPCS-Server service provider.

The client configuration is made of 4 main sections, in INI format. In depth description of the configuration files is available [here](https://github.com/CSCfi/HPCS/docs/configuration).

Example of client configuration :

```ini
[spire-server]
address = spire.lumi.csc.fi
port = port
trust-domain = spire-trust-domain

[hpcs-server]
url = https://hpcs-server:port

[vault]
url = https://vault-provider:port

[supercomputer]
address = lumi.csc.fi
username = etellier
```
Please replace `spire-server` section configuration with the informations relative to your Spire Server.
You will also need to replace `hpcs-server` with the address of your HPCS server, eventually the `port` with the port on which HPCS server is exposed.
The `vault` is the same as the `hpcs-server` section, please complete it with your vault informations.
Finally, configure the supercomputer to use in the `supercomputer` section, specifying it's address under `address` and your `username` on the system. Your SSH Key needs to be setup.

#### Prepare the runtime

We recommend using docker-compose to run the process. Here is an example of a docker-compose file :
It's composed of 3 sections, covering the three main steps of the process.
- Prepare, encrypt and ship the `talinx/jp2a` image for the user `etellier` on node `nid003044`
- Prepare, encrypt and ship the input data under `./workdir/jp2a_input` for the user `etellier` on node `nid003044`
- Run the `jp2a` preapred image on the supercomputer `nid003044` node, specifying application args `/sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result` (the `jp2a_input` prepared dataset will be available under `/sd-container/encrypted/jp2a_input` at runtime). You also can specify your verifications scripts to run before and after the application here : `[-i/-o] /pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts`

In depth documentation of the cli of the 3 parts are available [here](https://github.com/CSCfi/HPCS/docs/cli).

```yaml
version: '2.4'

services:
  container-prep:
    image: ghcr.io/cscfi/hpcs/container-prep:latest
    command:
      - "--config"
      - "/tmp/hpcs-client.conf"
      - "-b"
      - "talinx/jp2a"
      - "-s"
      - "/Users/telliere/secure_job/workdir"
      - "-e"
      - "-u"
      - "etellier"
      - "-c"
      - "nid003044"
      - "--data-path"
      - "/tmp/encrypted_prepared_jp2a.sif"
      - "--data-path-at-rest"
      - "/scratch/project_462000031/etellier/"
      - "--username"
      - "etellier"
    volumes:
      - /etc/group:/etc/group
      - /etc/passwd:/etc/passwd
      - /var/run/docker.sock:/var/run/docker.sock
      - $PWD/workdir:/tmp
      - $HOME/.ssh:/tmp/.ssh
    environment:
      - PWD=${PWD}
      - HOME=${HOME}
    user: "1001" # On Linux : Your uid (gathered using `id`). Remove on MacOS
    group_add:
     -  "120"    # The docker daemon group. Remove on MacOS


  data-prep:
    image: ghcr.io/cscfi/hpcs/data-prep:latest
    command:
      - "--config"
      - "/tmp/hpcs-client.conf"
      - "-i"
      - "/tmp/jp2a_input"
      - "-o"
      - "/tmp/"
      - "-u"
      - "etellier"
      - "-c"
      - "nid003044"
      - "--data-path"
      - "/tmp/encrypted_jp2a_input.tgz"
      - "--data-path-at-rest"
      - "/scratch/project_462000031/etellier/"
      - "--username"
      - "etellier"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $PWD/workdir:/tmp
      - $HOME/.ssh:/tmp/.ssh
    environment:
      - PWD=${PWD}
      - HOME=${HOME}

  job-prep:
    image: ghcr.io/cscfi/hpcs/job-prep:latest
    command:
      - "--config"
      - "/tmp/hpcs-client.conf"
      - "-N"
      - "1"
      - "-p"
      - "standard"
      - "-t"
      - "\"00:60:00\""
      - "-A"
      - "project_462000031"
      - "--nodelist"
      - "nid003044"
      - "--workdir"
      - "/scratch/project_462000031/etellier"
      - "-ai"
      - "/scratch/project_462000031/etellier/encrypted_prepared_jp2a.sif.info.yaml"
      - "-di"
      - "/scratch/project_462000031/etellier/encrypted_jp2a_input.tgz.info.yaml"
      - "-args"
      - "\"\\\" /sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result \\\"\""
      - "-i"
      - "/pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts"
      - "-o"
      - "/pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts"
      - "-flags"
      - "--env TERM=xterm-256color"
      - "-f"
    volumes:
      - $PWD/workdir:/tmp
      - $HOME/.ssh:/tmp/.ssh
    environment:
      - PWD=${PWD}
      - HOME=${HOME}
```

#### Run the preparations and the job

To run one of the containers :

```bash
docker compose run --rm [data/container/job]-prep
```

If you want to run the whole process by yourself : 

```bash
docker compose run --rm data-prep
docker compose run --rm container-prep
docker compose run --rm job-prep
```

An example demonstration is available [here](https://asciinema.org/a/PWDzxlaVQmfGjbh30KKNTRO1f).

### Server

HPCS Server is an API, interfacing HPCS client with Vault and Spire. This section needs basic knowledge of [SPIFFE/SPIRE](https://spiffe.io/) and [HashiCorp Vault](https://www.vaultproject.io/). 

For k8s, we only consider `kubectl` and `ansible` as available tools and that `kubectl` can create pods. Vault roles, spire identities are created automatically.

For docker-compose, we consider the Vault and the Spire Server as setup and the Spire-OIDC provider implemented to allow login to the vault using SVID identity. We also consider that proper roles are created in Vault to authorize HPCS Server to write roles and policies to the Vault, using a server SPIFFEID.

#### K8s

WIP

#### Docker-compose

:warning: This method is not the officially supporter method for HPCS Server

Pull server's image using Docker pull :

```bash
docker pull ghcr.io/cscfi/hpcs/server:latest
```

The server configuration is made of 2 main sections, in INI format. In depth description of the configuration files is available [here](https://github.com/CSCfi/HPCS/docs/configuration).

You'll be able to configure your Spire Server interfacing specifying :
- Address and port of the spire-server API.
- Spire trust domain.
- pre-command and spire-server-bin : f.e pre-command = "`kubectl exec -n spire spire-server-0 -- `" and spire-server-bin = "`spire-server`" will then be used to create cli interactions with the Spire Server socket (i.e : `kubectl exec -n spire spire-server-0 -- spire-server entry show`). Please keep this part as-it-is when running docker standalone and mount the spire-server directory at it's default path (`/tmp/spire-server`).

And vault configuration will work the same as for the client (using a base `url` config). The main difference is that you need to specify the name of the spire-server role in the Vault. This role needs to be created manually and needs to be bound to a policy allowing it to create policies and roles for clients (data/container preparation) and workloads (accessing data/container).

```ini
[spire-server]
address = "spire.lumi.csc.fi"
port = PORT
trust-domain = TRUST_DOMAIN
pre-command = ""
spire-server-bin = spire-server

[vault]
url = https://vault-provider:port
server-role = hpcs-server
```

The server image comes with a non-configured agent, it's configuration is assumed to be mounted under `/tmp/spire-agent.conf`. Several [node attestation methods](https://github.com/spiffe/spire/tree/main/doc) (see `plugin_agent_nodeattestor`) are available, the goal is to register the HPCS server Spire agent under a specific identity to provide workload identities for the server (then used to write policies and roles in vault).

An example configuration, using `join_token` attestation method :

```hcl
agent {
    data_dir = "./data/agent"
    log_level = "DEBUG"
    trust_domain = "TRUST_DOMAIN"
    server_address = ""
    server_port = PORT
    socket_path = "/tmp/spire-agent/public/api.sock"
    join_token = "TOKEN"
    insecure_bootstrap = true
}

plugins {
   KeyManager "disk" {
        plugin_data {
            directory = "./data/agent"
        }
    }

    NodeAttestor "join_token" {
        plugin_data {}
    }

    WorkloadAttestor "unix" {
        plugin_data {
            discover_workload_path = true
        }
    }
}
```


To run the server as a standalone Docker, we recommend using docker-compose.

An in depth documentation of the server's cli is available [here](https://github.com/CSCfi/HPCS/docs/configuration).

This docker-compose file specifies the proper spire-agent configuration to use, the mountpoint of the spire-server directory and the path to the mounted hpcs configuration.

```yaml
version: '2.4'

services:
  server:
    image: ghcr.io/cscfi/hpcs/server:dockerfile_everywhere
    command:
      - "--config"
      - "/tmp/hpcs-server.conf"
    ports:
      - 10080:10080
    volumes:
      - $PWD:/tmp
      - $PWD/spire-agent.conf:/tmp/agent.conf
      - /tmp/spire-server:/tmp/spire-server
    environment:
      - PWD=${PWD}
```

You can then run it using :
```bash
docker-compose run server
```

## Limitations