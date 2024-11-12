#!/bin/bash -eu
export XDG_RUNTIME_DIR=/run/user/1000

/usr/bin/dockerd-rootless-setuptool.sh install -f

MY_PUBLIC_IP=$(curl ifconfig.io 2> /dev/null)
export MY_PUBLIC_IP=${MY_PUBLIC_IP}
MY_PUBLIC_HOSTNAME=$(host "${MY_PUBLIC_IP}" | rev | cut -d " " -f 1 | tail -c +2 | rev)
export MY_PUBLIC_HOSTNAME=${MY_PUBLIC_HOSTNAME}
sed -e "s/MY_PUBLIC_IP/${MY_PUBLIC_IP}/" /etc/hpcs/hpcs-cluster.yaml > "${HOME}/hpcs-cluster.yaml"
sed -i -e "s/MY_PUBLIC_HOSTNAME/${MY_PUBLIC_HOSTNAME}/" "${HOME}/hpcs-cluster.yaml"
/usr/bin/kind create cluster --config "${HOME}/hpcs-cluster.yaml"

yq --yaml-output ".clusters[0].cluster.server = \"https://${MY_PUBLIC_HOSTNAME}:6444\"" "${HOME}/.kube/config" > "${HOME}/.kube/remote-config"

helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard
kubectl apply -f /etc/hpcs/admin-user.yaml
