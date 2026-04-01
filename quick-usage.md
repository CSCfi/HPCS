# Instructions for running HPCS as of the dev-fixes branch and :dev tags, April 1st 2025

## What you need

- Access to Lumi (and a project where you can run the compute job)
- The unversioned configuration-containing files `local/hpcs-client.conf` and `docker-compose.yaml`. The contents are probably best generated with jinja2 / j2 from `local/hpcs-client.conf` and `docker-compose.yaml`, respectively. Edit at least the beginning of `config.yaml` and run

```
j2 local/hpcs-client.conf.j2 config.yaml > local/hpcs-client.conf
j2 docker-compose.yaml.j2 config.yaml > docker-compose.yaml
```

- Some input for the compute job. If you use the default job, talinx/jp2a, which generates ASCII art from bitmap files, this should be placed somewhere in `local/`. See `input_dir` in config.yaml.
- The container you want to run computation on. For talinx/jp2, run `docker pull talinx/jp2a`.
- `age` for decrypting the output

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
