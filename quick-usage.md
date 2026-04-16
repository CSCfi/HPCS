# Quick usage instructions

As of the dev-usability branch and :dev container tags, April 1st 2026.

## What you need

- Access to Lumi (and a project where you can run the compute job)
- The configuration files `local/hpcs-client.conf` and `docker-compose.yaml`. The contents are probably best generated with jinja2 / j2 from `local/hpcs-client.conf.j2` and `docker-compose.yaml.j2`, respectively. Edit at least the beginning of `config.yaml` and run

```
j2 local/hpcs-client.conf.j2 config.yaml > local/hpcs-client.conf
j2 docker-compose.yaml.j2 config.yaml > docker-compose.yaml
```

- Some input for the compute job. If you use the default job, talinx/jp2a, which generates ASCII art from bitmap files, this should be placed somewhere in `local/`. See `input_dir` in config.yaml.
- The container you want to run computation on. For talinx/jp2, run `docker pull talinx/jp2a`.
- `age` for decrypting the output
- Previously, this repository stored some binaries as LFS objects. Now, the LFS budget has run out, so that doesn't work anymore. If you already have the required binaries in `client/container_preparation/input_logic/`, that if fine, but otherwise you need to supply in that directory `age` and `jq`. `tar` and `curl` were also stored there, but don't appear to be necessary.

## How to run

`local/` will be mounted into the containers running on your laptop, and the decryption key for the output of the computation will be written there. In `HPCS/`, run

```
docker compose run --rm container-prep
docker compose run --rm data-prep
docker compose run --rm job-prep
```

If everything goes well, your data will now be in an encrypted file on HPC. If you have run everything in the most default way, you can retrieve it with

```
scp {{ username }}@{{ supercomputer_address }}:{{ scratch_dir }}/output/encrypted_output.tgz ./
```

And decrypt it into `output.tgz` with

```
age --decrypt -i local/private_key -o output.tgz encrypted_output.tgz
```

(See `config.yaml` for those variables).
