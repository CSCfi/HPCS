import argparse


def sbatch_from_template(options: argparse.Namespace, template_path: str) -> str:
    """Create an sbatch file from a template and an argument parser namespace and the path to the template

    Args:
        options (argparse.Namespace): argument parser namespace
        template_path (str): path to the template file

    Returns:
        str: path to the generated sbtach file
    """
    
    # Replace placeholders in template str
    sbatch = boostrap_from_template(options, template_path)

    # Write modified template to file
    sbatchfilename = f"/tmp/sbatch-{options.job_name.replace('/','_')}"
    with open(sbatchfilename, "w+") as sbatchfile:
        sbatchfile.write(sbatch)

    return sbatchfilename


def boostrap_from_template(options: argparse.Namespace, template_path: str) -> str:
    """Modifies a template with the arguments stored in the arguments parser

    Args:
        options (argparse.Namespace): argument parser namespace
        template_path (str): path to the template file

    Returns:
        str: the modified template as a string
    """
    with open(template_path, "r") as sbatchfile:
        sbatch = sbatchfile.read()
        
        # Add general info
        sbatch = sbatch.replace("JOB_NAME", options.job_name.replace("/", "_"))
        sbatch = sbatch.replace("NODES", options.nodes)
        sbatch = sbatch.replace("PARTITION", options.partition)
        sbatch = sbatch.replace("TIME", options.time)
        sbatch = sbatch.replace("ACCOUNT", options.account)
        sbatch = sbatch.replace("NODELIST", options.nodelist)
        sbatch = sbatch.replace("WORKDIR", options.workdir)
        sbatch = sbatch.replace("TRUST_DOMAIN", options.trust_domain)
        sbatch = sbatch.replace("VAULT_ADDRESS", options.vault_address)

        # Dataset info
        sbatch = sbatch.replace("DATA_PATH", options.data_path_at_rest)
        sbatch = sbatch.replace("DATA_SPIFFEID", options.data_spiffeID)
        sbatch = sbatch.replace("DATA_ACCESS_ROLE", options.data_access_role)
        sbatch = sbatch.replace("DATA_SECRET_PATH", options.data_secret_path)

        # Application info
        sbatch = sbatch.replace("APPLICATION_PATH", options.application_path_at_rest)
        sbatch = sbatch.replace("APPLICATION_SPIFFEID", options.application_spiffeID)
        sbatch = sbatch.replace(
            "APPLICATION_ACCESS_ROLE", options.application_access_role
        )
        sbatch = sbatch.replace(
            "APPLICATION_SECRET_PATH", options.application_secret_path
        )


        # Singularity info
        if options.singularity_supplementary_flags:
            sbatch = sbatch.replace(
                "SINGULARITY_SUPPLEMENTARY_FLAGS",
                options.singularity_supplementary_flags,
            )
        else:
            sbatch = sbatch.replace("SINGULARITY_SUPPLEMENTARY_FLAGS", "")

        # Application arguments
        if options.arguments:
            sbatch = sbatch.replace("APPLICATION_ARGUMENTS", f"-- {options.arguments}")
        else:
            sbatch = sbatch.replace("APPLICATION_ARGUMENTS", "")

        # Supplementary input scripts
        if options.supplementary_input_scripts:
            sbatch = sbatch.replace(
                "INPUT_SCRIPTS_DIR",
                f"--bind {options.supplementary_input_scripts}:/sd-container/tools/input_logic/jobs",
            )
        else:
            sbatch = sbatch.replace("INPUT_SCRIPTS_DIR", "")

        # Supplementary output scripts
        if options.supplementary_output_scripts:
            sbatch = sbatch.replace(
                "OUTPUT_SCRIPTS_DIR",
                f"--bind {options.supplementary_output_scripts}:/sd-container/tools/output_logic/jobs",
            )
        else:
            sbatch = sbatch.replace("OUTPUT_SCRIPTS_DIR", "")

        return sbatch
