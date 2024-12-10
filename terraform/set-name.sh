#!/bin/bash -eu

usage_error() {
    echo "Usage: $0 --name <instance_name> --project <project id>" >&2
    exit 1
}

if [ "${#}" -ne 4 ] ; then
    usage_error
fi

instance_name=
project_id=
while [ "${#}" -ge 1 ] && [ -n "${1}" ]; do
    case "${1}" in
        --name ) instance_name=$2; shift 2;;
        --project ) project_id=$2; shift 2;;
        -- ) shift; break;;
        * ) break;;
    esac
done

dir=$(dirname "$0")
# Need to use two different files because the backend is picky about
# variables it does not know about. The two files are of different "type"
# because backend initialization doesn't automatically recognize "auto"
# variables.
backend_vars_name=tf-backend.tfvars
root_autovars_name=server-name.auto.tfvars
backend_vars_file=${dir}/${backend_vars_name}
root_autovars_file=${dir}/${root_autovars_name}

cat <<EOF > "${backend_vars_file}"
bucket = "${project_id}-terraform-state"
key    = "${instance_name}.tfstate"
EOF
echo 'instance_name = "'"${instance_name}"'"' >"${root_autovars_file}"
echo 'Call: terraform init [-reconfigure] -backend-config='"${backend_vars_name}"
