# kind VM recipe

Recipe to deploy a simple VM with a running [kind](https://kind.sigs.k8s.io/) in Pouta.

## VM deployment

The VM is defined in [Terraform](https://www.terraform.io/) with state stored in `<project name>-terraform-state` bucket deployed under you project in allas.

To deploy/update, download a config file from Pouta for authentication (the `<project name>-openrc.sh`).
You will also need `S3` credentials for accessing the bucket, in the below recipe it assumes you have them nicely stored in [pass](https://www.passwordstore.org/).
Currently the VM also needs 2 secrets:

- host SSH private key
- host SSH public key (not really secret but we have it classified as such)

Code is looking for them in following locations:

- `secrets/ssh_host_ed25519_key`
- `secrets/ssh_host_ed25519_key.pub`

After cloning the repository unlock the secrets with

    -> git-crypt unlock

Put public SSH keys with admin access to the `secrets/public_keys` file.
If you want some users to have just access to tunnel ports from the VM, add their keys to the `secrets/tunnel_keys` file, if not just `touch secrets/tunnel_keys`.
After both of those files are present, you should be able to deploy the VM.
Authenticate first:

    # authenticate
    -> source project_2007468-openrc.sh
    # for simplicity of this example we just export S3 creentials
    -> export AWS_ACCESS_KEY_ID=$(pass fancy_project/aws_key)
    -> export AWS_SECRET_ACCESS_KEY=$(pass fancy_project/aws_secret)

For clean environment on the backend, instance name is defined using an included script `set-name.sh`.
Backend doesn't allow to just use variables for the backend file name, that is why we need to define it before executing `Terraform`.

    -> ./set-name.sh --name kitten --project <project id>
    Call: terraform init [-reconfigure] -backend-config=tf-backend.tfvars
    -> terraform init -reconfigure -backend-config=tf-backend.tfvars

Now you can just deploy

    -> terraform apply

And wait for things to finish, including package udpates and installations on the VM.
As one of the outputs you should see the address of your VM, e.g.:

    Outputs:

    address = "128.214.254.127"

## Connecting to kind

It takes a few moments for everything to finish setting up on the VM.
Once it finishes the VM should be running a configured `kind` cluster with a dashboard running.
You can download you config file and access the cluster, notice the access to the API is restricted to trusted networks only

    -> scp ubuntu@128.214.254.127:.kube/remote-config .
    -> export KUBECONFIG=$(pwd)/remote-config
    -> kubectl auth whoami
    ATTRIBUTE   VALUE
    Username    kubernetes-admin
    Groups      [kubeadm:cluster-admins system:authenticated]

To, for example, check if the dashboard is ready

    -> kubectl get all --namespace kubernetes-dashboard
    NAME                                                       READY   STATUS    RESTARTS   AGE
    pod/kubernetes-dashboard-api-5cd64dbc99-xjbj8              1/1     Running   0          2m54s
    pod/kubernetes-dashboard-auth-5c8859fcbd-zt2lm             1/1     Running   0          2m54s
    pod/kubernetes-dashboard-kong-57d45c4f69-5gv2d             1/1     Running   0          2m54s
    pod/kubernetes-dashboard-metrics-scraper-df869c886-chxx4   1/1     Running   0          2m54s
    pod/kubernetes-dashboard-web-6ccf8d967-fsctp               1/1     Running   0          2m54s

    NAME                                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
    service/kubernetes-dashboard-api               ClusterIP   10.96.149.208   <none>        8000/TCP   2m55s
    service/kubernetes-dashboard-auth              ClusterIP   10.96.140.195   <none>        8000/TCP   2m55s
    service/kubernetes-dashboard-kong-proxy        ClusterIP   10.96.35.136    <none>        443/TCP    2m55s
    service/kubernetes-dashboard-metrics-scraper   ClusterIP   10.96.222.176   <none>        8000/TCP   2m55s
    service/kubernetes-dashboard-web               ClusterIP   10.96.139.1     <none>        8000/TCP   2m55s

    NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
    deployment.apps/kubernetes-dashboard-api               1/1     1            1           2m54s
    deployment.apps/kubernetes-dashboard-auth              1/1     1            1           2m54s
    deployment.apps/kubernetes-dashboard-kong              1/1     1            1           2m54s
    deployment.apps/kubernetes-dashboard-metrics-scraper   1/1     1            1           2m54s
    deployment.apps/kubernetes-dashboard-web               1/1     1            1           2m54s

    NAME                                                             DESIRED   CURRENT   READY   AGE
    replicaset.apps/kubernetes-dashboard-api-5cd64dbc99              1         1         1       2m54s
    replicaset.apps/kubernetes-dashboard-auth-5c8859fcbd             1         1         1       2m54s
    replicaset.apps/kubernetes-dashboard-kong-57d45c4f69             1         1         1       2m54s
    replicaset.apps/kubernetes-dashboard-metrics-scraper-df869c886   1         1         1       2m54s
    replicaset.apps/kubernetes-dashboard-web-6ccf8d967               1         1         1       2m54s

Dashboard by default in this case is not overly secure so the external route is not setup, to access:

    # Generate a token to login to the dashboard with
    -> kubectl -n kubernetes-dashboard create token admin-user
    # Forward the dashboard to your machine
    -> kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443
    Forwarding from 127.0.0.1:8443 -> 8443
    Forwarding from [::1]:8443 -> 8443

And view the dashboard in your browser under `https://localhost:8443` using the generated token to login.
Note that the cluster and the dashboard use a self signed certificate so your browser is not going to like it.
