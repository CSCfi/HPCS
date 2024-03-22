from utils.cli.cli import parse_arguments, check_arguments
from lib.sbatch_generation import sbatch_from_template
from lib.info_file import get_info_from_infofile
import sys, os

sys.path.append(os.path.expanduser("../../../"))  # For cli usage
sys.path.append(os.path.expanduser("../../"))  # For inside-container usage
from utils.ssh_utils import ssh_connect, ssh_copy_file, ssh_run_command
from utils.conf.client.conf import parse_configuration
from time import sleep
from pyrage import x25519

if __name__ == "__main__":
    # Parse arguments
    options = parse_arguments()

    # Parse configuration
    configuration = parse_configuration(options.config)
    
    # Parse configuration as options
    options.username = configuration['supercomputer']['username']
    options.trust_domain = configuration['spire-server']['trust-domain']
    options.vault_address = configuration['vault']['url']
    
    # Check arguments
    options = check_arguments(options)

    # Connect via SSH to supercomputer
    ssh_client = ssh_connect(options.username)

    # Check infos from application
    print("Getting info from info file for application")
    (
        options.application_path_at_rest,
        options.application_spiffeID,
        options.application_access_role,
        options.application_secret_path,
    ) = get_info_from_infofile(ssh_client=ssh_client, path=options.application_info)

    # And data
    print("Getting info from info file for data")
    (
        options.data_path_at_rest,
        options.data_spiffeID,
        options.data_access_role,
        options.data_secret_path,
    ) = get_info_from_infofile(ssh_client=ssh_client, path=options.data_info)

    # Write sbatch file
    sbatch_path = sbatch_from_template(options, "utils/sbatch.template")

    # Copy SBATCH to supercomputer
    ssh_copy_file(ssh_client, sbatch_path, f"~/")
    
    # Copy config file to supercomputer
    ssh_copy_file(ssh_client, options.config, f"~/.config/hpcs-client.conf")

    # Create public encryption key for output data
    ident = x25519.Identity.generate()

    # Write public key to temp file
    with open("/tmp/output_key", "w+") as public_key_file:
        public_key_file.write(str(ident.to_public()))

    # Write private key to current directory
    with open("/tmp/private_key", "w+") as private_key_file:
        private_key_file.write(str(ident))

    # Copy public key to supercomputer
    ssh_copy_file(ssh_client, "/tmp/output_key", f"~/")

    # Parse command
    sbatch_filename = f"{sbatch_path.split('/')[-1]}"
    command = f"cd ~ ; sbatch {sbatch_filename}"

    # Run slurm job
    stdin, stdout, stderr = ssh_run_command(ssh_client, command)
    stdin.close()

    stderr = stderr.read().decode()
    # Check for errors
    if stderr != "":
        print("Error while running sbatch :")
        print(stderr)
        exit(1)

    # Extract job id from stdout
    jobid = stdout.read().decode().split(" ")[-1].replace("\n", "")
    print(f"Job successfully created with id {jobid}")

    # If user asked to follow the logs of the job
    if options.follow:
        # Follow the job's output
        command = f"cd {options.workdir} ; touch {options.job_name}.out ; tail -f -n 0 {options.job_name}.out"
        stdin, stdout, stderr = ssh_run_command(ssh_client, command, True)
        stdin.close()

        # Keep read alive
        for line in iter(stdout.readline, ""):
            print(line, end="")

    # If user doesn't follow job's logs
    else:
        # Still, follow the job's status at fixed interval
        print(
            f"Waiting for the job to run. You can now exit this script if needed, outputs will be available in {options.workdir}/output when finished"
        )
        
        # Specific output format squeue command to parse informations about submitted job
        command = f"squeue -o '%A;%u;%T' | grep {options.username} | grep {jobid}"

        # Run first status update
        stdin, stdout, stderr = ssh_run_command(ssh_client, command, True)
        job_status = ""
        stdout = stdout.read().decode().replace("\n", "")
        stdin.close()
        
        # While job runs (while it has an entry in squeue)
        while stdout != "":
            # If status has changed
            if job_status != stdout.split(";")[-1]:
                job_status = stdout.split(";")[-1]
                print(f"Job's state changed, job is now in state : {job_status}")

            # Wait
            sleep(10)

            # Run status update
            stdin, stdout, stderr = ssh_run_command(ssh_client, command, True)
            stdout = stdout.read().decode().replace("\n", "")
            stdin.close()

    # Job is over
    print(f"Job finished, please find outputs in {options.workdir}/output")
    ssh_client.close()
