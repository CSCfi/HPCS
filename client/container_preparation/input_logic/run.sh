#!/bin/sh

# Useful binaries
PATH="$PATH:/sd-container/tools/input_logic/"

# Before checking anything, we decrypt the data inside of the container
echo "[SD-Container][Input-Logic] : Getting data decryption key from vault"

# Get token via vault login. The data_login environment variable need to be exported from calling script
data_token=$(curl -s --request POST --data "$data_login" $vault/v1/auth/jwt/login | jq '.auth.client_token' -r) || exit 1

# Use the token to access the key. The data_path environment variable needs to be exported from calling script
data_key=$(curl -s -H "X-Vault-Token: $data_token" $vault/v1/kv/data/${data_path} | jq '.data.data.key' -r) || exit 1

# Write the key in an encrypted volume
echo "$data_key" >/sd-container/encrypted/decryption_key

echo "[SD-Container][Input-Logic] : Decrypting data with the key from the vault"

# Reinvest the key to decrypt the encrypted data in an encrypted volume
age --decrypt -i /sd-container/encrypted/decryption_key -o /sd-container/encrypted/decrypted_data.tgz /sd-container/input/data.tgz || exit 1

# Remove the not-anymore-needed key
rm /sd-container/encrypted/decryption_key

echo "[SD-Container][Input-Logic] : Data decrypted"

# Untar the not anymore encrypted archive
cd /sd-container/encrypted
tar xvf /sd-container/encrypted/decrypted_data.tgz || exit 1

echo "[SD-Container][Input-Logic] : Data untared"

for input_logic_script in $(find /sd-container/tools/input_logic | grep ".sh" | grep -v "run.sh"); do
	echo "[SD-Container][Input-Logic] : Running ${input_logic_script}"
	$input_logic_script || echo "${input_logic_script} failed, aborting."
	echo "[SD-Container][Input-Logic] : End of ${input_logic_script}"
done
