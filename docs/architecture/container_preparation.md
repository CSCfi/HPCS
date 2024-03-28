# Container preparation

This step consist in using an original OCI image to prepare it, encrypt it and ship it to the supercomputing site, it's decryption key to the vault.

## Sequence diagram of this step

```mermaid
sequenceDiagram
    actor User
    User -->> Container Preparation container: spawns using docker-compose
    Container Preparation container -->> Spire Agent: spawns using `spawn_agent.py`
    Spire Agent ->> Spire Server: Runs node attestation
    Spire Server ->> Spire Agent: Attests node, provide SVIDs for linked identities
    Container Preparation container ->> Container Preparation container: Prepare container, results in an encrypted image and a private key (see below)
    Container Preparation container ->> Spire Agent: Fetches API to get an SVID
    Spire Agent ->> Container Preparation container: Provides SVID
    Container Preparation container ->> Vault: Log-in using SVID
    Vault ->> Container Preparation container: Returns an authentication token (write only on client's path)
    Container Preparation container ->> Vault: Write private key using authentication token
    Vault ->> Container Preparation container: 
    Container Preparation container ->> HPCS Server: Request creation of workloads (compute nodes, users, groups ...) authorized to access the key and using SVID to authenticate
    HPCS Server ->> Spire Server: Validate SVID
    Spire Server ->> HPCS Spire Agent: 
    HPCS Spire Agent ->> Spire Server: Validate SVID
    Spire Server ->> HPCS Server: 
    HPCS Server ->> Spire Server: Create workloads identities to access the key
    Spire Server ->> HPCS Server: 
    HPCS Server ->> Vault: Create role and policy to access the key
    Vault ->> HPCS Server: 
    HPCS Server ->> Container Preparation container: SpiffeID & role to access the container, path to the secret
    Container Preparation container ->> Container Preparation container: Parse info file based on previous steps
    Container Preparation container ->> Supercomputer: Ship encrypted container
    Supercomputer ->> Container Preparation container: ' 
    Container Preparation container ->> Supercomputer: Ship info file
    Supercomputer ->> Container Preparation container: 
    Container Preparation container -->> Spire Agent: Kills
    Spire Agent -->> Container Preparation container: 
    Spire Agent -->> Container Preparation container: Dies
    Container Preparation container -->> User: Finishes
```

## Sequence diagram of the container's preparation (without shipping)

### Image is prepared and then encrypted (Encryption at rest)

This step is currently (3/2024) used to encrypt the container. It does not require changes on LUMI to work.

```mermaid
sequenceDiagram
    actor User
    User -->>HPCS Client: spawns using `python3 prepare_container.py [OPTIONS]`
    HPCS Client -->> Docker Client: spawns
    HPCS Client ->> HPCS Client: Create prepared Dockerfile
    HPCS Client ->> Docker Client: Create prepared OCI image using Dockerfile
    Docker Client ->> Docker Client: Builds prepared OCI image
    Docker Client ->> HPCS Client: Returns prepared OCI image tag
    HPCS Client ->> Docker Client: Create build environment container (provides prepared image tag)
    Docker Client -->> SD-Container Build-Env: Spawns
    SD-Container Build-Env ->> SD-Container Build-Env: Build final prepared SIF image
    SD-Container Build-Env ->> HPCS Client: Returns final prepared SIF image
    HPCS Client ->> HPCS Client: Generate public/private key
    HPCS Client ->> HPCS Client: Encrypt image file
```

### Image is prepared and SIF encrypted

When HPC nodes support encrypted containers, this process can be used.

```mermaid
sequenceDiagram
    actor User
    User -->>HPCS Client: spawns using `python3 prepare_container.py [OPTIONS]`
    HPCS Client -->> Docker Client: spawns
    HPCS Client ->> HPCS Client: Create prepared Dockerfile
    HPCS Client ->> Docker Client: Create prepared OCI image using Dockerfile
    Docker Client ->> Docker Client: Builds prepared OCI image
    Docker Client ->> HPCS Client: Returns prepared OCI image tag
    HPCS Client ->> HPCS Client: Generate public/private key
    HPCS Client ->> Docker Client: Create build environment container (provides prepared image tag, public key)
    Docker Client -->> Build-Env: Spawns
    Build-Env ->> Build-Env: Build final prepared and encrypted SIF image
    Build-Env ->> HPCS Client: Returns final prepared and encrypted SIF image
```
