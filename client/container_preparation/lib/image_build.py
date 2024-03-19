from dockerfile_parse import DockerfileParser
import os, sys
from tools.docker.docker_utils import build_build_env, check_build_env_exists

sys.path.append(os.path.expanduser("../../../"))  # For cli usage
sys.path.append(os.path.expanduser("../../"))  # For inside-container usage
from utils.crypto_utils import generate_crypto_keys, private_bytes, public_bytes
from docker import DockerClient
from pyrage import x25519, encrypt


def generate_prepared_dockerfile(
    base_image_tag, docker_client: DockerClient
) -> DockerfileParser:
    """Generates an sd-container prepared Dockerfile from a base image

    Args:
        base_image_tag (string): The tag of the original OCI image

    Returns:
        DockerfileParser: The parsed Dockerfile object
    """
    # Loading base_image attributes and checking it exists
    base_image = docker_client.images.get(base_image_tag)

    # Read the current image to extract the entrypoint
    # Depending on image configuration, Entrypoint can be found at different place
    base_entrypoint = base_image.attrs["ContainerConfig"]["Entrypoint"]
    if base_entrypoint == None:
        base_entrypoint = base_image.attrs["Config"]["Entrypoint"]

    # Starting to write the prepared container Dockerfile
    dfp = DockerfileParser(path="/tmp")
    # Reset the content
    dfp.content = "FROM base"
    dfp.baseimage = base_image_tag

    dfp.add_lines(f"RUN mkdir /sd-container")

    # Adding ingress / egress / tools / key management directories creation to the receipe
    for directories in [
        "/sd-container/input",
        "/sd-container/output",
        "/sd-container/scratch",
        "/sd-container/tools",
        "/sd-container/keys",
    ]:
        dfp.add_lines(f"RUN mkdir -p {directories}")

    # Exposing the ouput directory as a volume (avoid losing data if output isn't mounted from bare-metal)
    dfp.add_lines("VOLUME /sd-container/output")

    # Exposing the input directory as a volume (to force user to mount it's input data)
    dfp.add_lines("VOLUME /sd-container/input")

    # Adding input/output scripts to the container, these scripts are made to run every underlying input/output scripts
    dfp.add_lines(f"COPY input_logic /sd-container/tools/input_logic")
    dfp.add_lines(f"COPY output_logic /sd-container/tools/output_logic")

    # Rewrite the entrypoint to run the input/output scripts
    dfp.add_lines(
        f"ENTRYPOINT /sd-container/tools/input_logic/run.sh && {' '.join(base_entrypoint)} $@ > /sd-container/output/stdout 2> /sd-container/output/stderr ; echo $? > /sd-container/output/exit_code ; /sd-container/tools/output_logic/run.sh"
    )

    return dfp


def build_prepared_image(base_image_tag, docker_client: DockerClient):
    """Builds an OCI sd-container prepared image out of any other OCI image

    Args:
        base_image_tag (string): The tag of the original OCI image

    Returns:
        string: The tag of the prepared image
    """
    # Generate prepared Dockerfile
    dockerfile_obj = generate_prepared_dockerfile(
        base_image_tag, docker_client=docker_client
    )

    # Creating new image tag
    prepared_image_tag = (
        f"sd-container/prepared_{dockerfile_obj.baseimage.split('/')[-1]}:latest"
    )

    # Build the image
    docker_client.images.build(
        path=".", dockerfile=dockerfile_obj.dockerfile_path, tag=prepared_image_tag
    )

    # Clean up Dockerfile
    os.remove(dockerfile_obj.dockerfile_path)

    # Return image tag
    return prepared_image_tag


def create_sif_image(
    prepared_image_tag,
    destination_path,
    docker_client: DockerClient,
    docker_socket_path: str,
    encrypted=False,
):
    """Creates an Apptainer SIF image (encrypted or not) using the sd-container/build_env
    out of a prepared OCI image.

    Args:
        prepared_image_tag (string): The OCI Image tag (i.e sd-container/prepared_cowsay)
        destination_path (string): The path where the .sif image will be written (i.e /tmp => /tmp/prepared_cowsay.sif)
        encrypted (bool, optional): Wether or not to encrypt the container, keys are generated relatively to the current path, and are called "keys, keys.pub". Defaults to False.
    """
    # Check that the build environment exists
    build_env_exists = check_build_env_exists(docker_client=docker_client)
    if not build_env_exists:
        print("Build environment container image doesn't exist, building it")
        build_build_env(docker_client=docker_client)
        build_env_exists = check_build_env_exists(docker_client=docker_client)

    # Fixing the build environment image tag
    build_env_image_tag = build_env_exists.attrs["RepoTags"][0]

    # Fixing the prepared image name out of it's tag
    prepared_image_name = prepared_image_tag.split("/")[-1].split(":")[0]

    # Composing the final command to run (the build env consists in apptainer build + the command var)
    command = f"/output/{prepared_image_name}.sif docker-daemon://{prepared_image_tag}"

    # Composing the dictionary of volumes (docker socket for image reading, output directory for result image)
    volumes = [
        f"{docker_socket_path}:{docker_socket_path}",
        f"{destination_path}:/output",
        "/etc/passwd:/etc/passwd",
        "/etc/group:/etc/group",
    ]

    # Run the secured container build
    if not encrypted:
        docker_client.containers.run(
            image=build_env_image_tag,
            command=command,
            volumes=volumes,
            remove=True,
            user=os.getuid(),
            group_add=[f"{os.stat(docker_socket_path).st_gid}"],
        )
        
    # Keeping the if/else for easy code rollback if encrypted containers can be used (that's why we don't have only one "docker_client.containers.run()")
    else:
        docker_client.containers.run(
            image=build_env_image_tag,
            command=command,
            volumes=volumes,
            remove=True,
            user=os.getuid(),
            group_add=[f"{os.stat(docker_socket_path).st_gid}"],
        )

        # Generate necessary keys to encrypt the SIF file
        sif_decryption_key = x25519.Identity.generate()
        sif_enryption_key = sif_decryption_key.to_public()

        # Encrypt the SIF image
        with open(f"/tmp/{prepared_image_name}.sif", "rb") as inputfile:
            encrypted = encrypt(inputfile.read(), [sif_enryption_key])

        # Write the encrypted SIF image to the encrypted SIF file
        open(f"/tmp/encrypted_{prepared_image_name}.sif", "wb+").write(encrypted)

        # Remove the unencrypted image
        os.remove(f"/tmp/{prepared_image_name}.sif")

        print(
            f"SIF image encrypted, written to /tmp/encrypted_{prepared_image_name}.sif"
        )

        open(f"/tmp/keys", "w+").write(str(sif_decryption_key))

        print(f"Encryption : Keys written to /tmp/keys")

        # Commenting out the encrypted container runtime part since we can't run them atm
        # # Define pem path
        # pem_path = f"/tmp"

        # # Generate public and private keys to encrypt the container
        # privateKey, publicKey = generate_crypto_keys()
        # open(f"{pem_path}/keys.pub", "w+").write(
        #     public_bytes(publicKey).decode("utf-8")
        # )

        # # Adding the public key to the mounted volumes (to encrypt the .sif)
        # volumes.append(f"{destination_path}/keys.pub:/encryption_key.pub")

        # # Run the build
        # docker_client.containers.run(
        #     image=build_env_image_tag,
        #     command=f"--pem-path=/encryption_key.pub {command}",
        #     volumes=volumes,
        #     cap_add=["MKNOD", "SYS_ADMIN"],
        #     devices=["/dev/fuse"],
        #     security_opt=["apparmor:unconfined"],
        #     remove=True,
        #     user=os.getuid(),
        #     group_add=[f"{os.stat(docker_socket_path).st_gid}"],
        # )

        # # Clean up public key (remove file)
        # os.remove(f"{pem_path}/keys.pub")

        # # Write the decryption key to a file (Temporarily)
        # open(f"{pem_path}/keys", "w+").write(private_bytes(privateKey).decode("utf-8"))
        # print(f"Encryption : Keys written to {pem_path}/keys[.pub]")
