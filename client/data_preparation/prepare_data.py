from client.data_preparation.tools.cli.cli import parse_arguments, check_arguments
from pyrage import x25519, encrypt
from os import path, remove
import tarfile

if __name__ == "__main__":
    # Parse arguments from cli
    options = parse_arguments()

    # For later usage
    input_path = options.input_path
    output_path = options.output_path

    # Check arguments
    input_is_file = check_arguments(input_path, output_path)

    # If input isn't a file, create a tar archive with it.
    if not input_is_file:
        output_file = f"{input_path.split('/')[-1]}.tgz"

        # Create tar archive and write inputs inside of it
        with tarfile.open(f"/tmp/{output_file}", "w:gz") as input_tar:
            input_tar.add(input_path, arcname=path.basename(input_path))

        # Update input path
        input_path = f"/tmp/{output_file}"
        print(f"Input is a directory, /tmp/{output_file} written.")

    # Generate necessary keys
    data_decryption_key = x25519.Identity.generate()
    data_enryption_key = data_decryption_key.to_public()

    # Encrypt input
    with open(input_path, "rb") as inputfile:
        encrypted = encrypt(inputfile.read(), [data_enryption_key])

    open(f"{output_path}/encrypted_{output_file}", "wb+").write(encrypted)

    print(f"File encrypted, written to {output_path}/encrypted_{output_file}")

    # Write private key to file
    with open("/tmp/keys", "w+") as keyfile:
        keyfile.write(str(data_decryption_key))

    remove(f"/tmp/{output_file}")

    print(f"Private key written to /tmp/keys")
