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

We recommand using docker-compose to run the process. Here is an example of a docker-compose file :
It's composed of 3 sections, covering the three main steps of the process.
- Prepare, encrypt and ship the `talinx/jp2a` image for the user `etellier` on node `nid003044`
- Prepare, encrypt and ship the input data under `./workdir/jp2a_input` for the user `etellier` on node `nid003044`
- Run the `jp2a` preapred image on the supercomputer `nid003044` node, specifying application args `/sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result` (the `jp2a_input` prepared dataset will be available under `/sd-container/encrypted/jp2a_input` at runtime). You also can specify your verifications scripts to run before and after the application here : `/pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts`

In depth documentation of the cli of the 3 jobs are available [here](https://github.com/CSCfi/HPCS/docs/cli).

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

## Limitations