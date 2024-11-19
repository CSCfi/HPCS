# Job preparation

Using the cli directly isn't recommended, the supported way is through docker's entrypoint.

The job preparation cli allows the user to run the secure job. It will gather the necessary informations using the info files before connecting to the supercomputer to run a template-generated sbatch file.

```
usage: prepare_job.py [-h] --config CONFIG [--job-name JOB_NAME] --nodes NODES --partition PARTITION --time TIME --account ACCOUNT --nodelist NODELIST --workdir WORKDIR --application-info APPLICATION_INFO --data-info
                      DATA_INFO --supplementary-input-scripts SUPPLEMENTARY_INPUT_SCRIPTS --supplementary-output-scripts SUPPLEMENTARY_OUTPUT_SCRIPTS
                      [--singularity-supplementary-flags SINGULARITY_SUPPLEMENTARY_FLAGS] [--arguments ARGUMENTS] [--follow]

CLI Options

options:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file (INI Format) (default: /tmp/hpcs-client.conf)
  --job-name JOB_NAME, -J JOB_NAME
                        name of the job
  --nodes NODES, -N NODES
                        count of nodes on which to run
  --partition PARTITION, -p PARTITION
                        partition requested
  --time TIME, -t TIME  time limit
  --account ACCOUNT, -A ACCOUNT
                        account to bill the job to
  --nodelist NODELIST, -w NODELIST
                        request a specific list of hosts
  --workdir WORKDIR, -s WORKDIR
                        directory to work in (LUMI-SD specific -> different from chdir)
  --application-info APPLICATION_INFO, -ai APPLICATION_INFO
                        path to the info file for the image to run on supercomputer
  --data-info DATA_INFO, -di DATA_INFO
                        path to the info file for the dataset to use on supercomputer
  --supplementary-input-scripts SUPPLEMENTARY_INPUT_SCRIPTS, -i SUPPLEMENTARY_INPUT_SCRIPTS
                        path to your input verification scripts directory
  --supplementary-output-scripts SUPPLEMENTARY_OUTPUT_SCRIPTS, -o SUPPLEMENTARY_OUTPUT_SCRIPTS
                        path to your output verification scripts directory
  --singularity-supplementary-flags SINGULARITY_SUPPLEMENTARY_FLAGS, -flags SINGULARITY_SUPPLEMENTARY_FLAGS
                        supplementary arguments to pass to singularity
  --arguments ARGUMENTS, -args ARGUMENTS
                        supplementary arguments to pass to the application
  --follow, -f          Follow job's output (default : False)
```

The standard command format would be like this :

```bash
python3 ./client/job_preparation/prepare_job.py [SLURM OPTIONS] --workdir [WORKDIR] --application-info [PATH TO INFO FILE] --data-info [PATH TO INFO FILE] --supplementary-input-scripts [PATH TO SUPPLEMENTARY SCRIPTS TO RUN BEFORE APPLICATION] --supplementary-output-scripts [PATH TO SUPPLEMENTARY SCRIPTS TO RUN AFTER APPLICATION] --singularity-supplementary-flags [FLAGS TO MANUALLY PASS TO SINGULARITY] --arguments [ARGUMENTS FOR THE FINAL APPLICATION]
```

Examples

```bash
python3 ./prepare_job.py -u etellier -N 1 -p standard -t "00:60:00" -A project_462000031 --nodelist nid001791 --workdir /scratch/project_462000031/etellier -ai /pfs/lustrep4/scratch/project_462000031/etellier/encrypted_prepared_jp2a.sif.info.yaml  -di /pfs/lustrep4/scratch/project_462000031/etellier/encrypted_jp2a_input.tgz.info.yaml -args "\" /sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result \"" -i /pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts -o /pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts -flags "--env TERM=xterm-256color" -f
```

Will create a slurm job with the following configuration :
- 1 node (nid001791)
- On partition "standard"
- As etellier
- for an hour

Also :
- HPCS will run the job using `/scratch/project_462000031/etellier` as its workdir
- The application will be handled using info file at `/pfs/lustrep4/scratch/project_462000031/etellier/encrypted_prepared_jp2a.sif.info.yaml`
- The application will be handled using info file at `/pfs/lustrep4/scratch/project_462000031/etellier/encrypted_jp2a_input.tgz.info.yaml`
- "`--env TERM=xterm-256color`" will be passed to `singularity run` when creating the final container
- The scripts available under the `/pfs/lustrep4/scratch/project_462000031/etellier/verification_scripts` directory will be mounted in the final container in order to run them before and after the container's application
- `\" /sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result \"` will be passed to the `singularity run` command, i.e : `singularity run prepared_jp2a.sif -- \" /sd-container/encrypted/jp2a_input/image.png --width=100 --output=/sd-container/output/result \"`
- The client will follow the output of the job, because of the `-f` flag

For more information about the server configuration, see the [associated documentation](https://github.com/CSCfi/HPCS/tree/doc/readme_and_sequence_diagrams/docs/configuration/hpcs-client.md).
