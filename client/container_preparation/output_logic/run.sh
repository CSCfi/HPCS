#!/bin/sh

for input_logic_script in $(find /sd-container/tools/output_logic | grep ".sh" | grep -v "run.sh"); do
    echo "[SD-Container][Output-Logic] : Running ${input_logic_script}"
    $input_logic_script     || echo "${input_logic_script} failed, aborting."
    echo "[SD-Container][Output-Logic] : End of ${input_logic_script}"
done

PATH="$PATH:/sd-container/tools/input_logic/"

# Finish the job by securing output data
echo "[SD-Container][Output-Logic] : Creating output archive"

# Creating output archive
tar -czvf /sd-container/encrypted/output.tgz /sd-container/output

echo "[SD-Container][Output-Logic] : Encrypting output archive"

# Encrypting the archive, the output key needs to be stored in the $HOME directory, automatically mounted on singularity run
# since it's a public key, no further security logic is needed for this key
age --encrypt -R ~/output_key -o /tmp/output/encrypted_output.tgz /sd-container/encrypted/output.tgz

echo "[SD-Container][Output-Logic] : Output archive encrypted"
