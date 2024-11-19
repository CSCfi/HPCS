# Job preparation

This step consists in the preparation of the secure job, followed by its execution. It requires two info files (one for the data, one for the secured container) and more settings about the runtime (arguments, parameters for the singularity container ...).

## Sequence diagram of this step

```mermaid
sequenceDiagram
    actor User
    participant Job Preparation container
    participant Login Node
    participant Scheduler

    User -->> Job Preparation container: spawns using docker-compose
    Job Preparation container ->> Login Node: Initiate SSH Connection
    rect rgb(191, 223, 255)
        note right of User: Job preparation
        Job Preparation container ->> Login Node: SCP Data's info file
        Login Node ->> Job Preparation container: Info file
        Job Preparation container ->> Job Preparation container: Parse info from info file
        Job Preparation container ->> Login Node: SCP Container image's info file
        Login Node ->> Job Preparation container: Info file
        Job Preparation container ->> Job Preparation container: Parse info from info file
        Job Preparation container ->> Job Preparation container: Generate SBATCH file from template based on info gathered
        Job Preparation container ->> Login Node: Copy SBATCH File and HPCS Configuration file
        Login Node ->> Job Preparation container:
        Job Preparation container ->> Job Preparation container: Generate keypair for output data
        Job Preparation container ->> Login Node: Copy encryption key
        Login Node ->> Job Preparation container:
    end

    rect rgb(191, 223, 255)
        note right of User: Job runtime
        Job Preparation container ->> Login Node: SSH Execute "sbatch SBATCHFILE"
        Login Node ->>+ Scheduler: sbatch SBATCHFILE
        Scheduler ->> Login Node: Job created + Job id
        Login Node ->> Job Preparation container: Job created + Job id
        Job Preparation container ->> Job Preparation container: Follows job output or job status
        activate Job Preparation container
        Scheduler ->> Scheduler: Scheduling job
        activate Scheduler
        deactivate Scheduler
        Scheduler ->> Compute node: Elect node - Execute SBATCHFILE
        Compute node ->> Compute node: Clone HPCS Github / Download age and gocryptfs binaries
        Compute node -->> Spire Agent: spawns using `spawn_agent.py`
        Spire Agent ->> Spire Server: Runs node attestation
        Spire Server ->> Spire Agent: Attests node, provide SVIDs for linked identities
        Compute node ->> Spire Agent: Fetches API to get an SVID
        Spire Agent ->> Compute node: Provides SVID
        Compute node ->> Vault: Log-in using SVID
        Vault ->> Compute node: Returns an authentication token (read only on container key's path)
        Compute node ->> Vault: Read container's key using authentication token
        Vault ->> Compute node: Returns container's key
        Compute node ->> Compute node: Decrypt container image
        Compute node ->> Compute node: Setup secure environment for runtime (Encrypted volumes, gather flags etc)
        Compute node ->> Spire Agent: Fetches API to get an SVID
        Spire Agent ->> Compute node: Provides SVID
        Compute node ->> Compute node: Export SVID and data secret path in a variable
        Compute node -->> Application container: spawns using `singularity run`
        Application container ->> Vault: Log-in using SVID
        Vault ->> Application container: Returns an authentication token (read only on data key's path)
        Application container ->> Vault: Read data's key using authentication token
        Vault ->> Application container: Returns data's key
        Application container ->> Application container: Decrypt data using key
        Application container ->> Application container: Runs input scripts
        Application container ->> Application container: Application runs
        Application container ->> Application container: Runs output scripts
        Application container ->> Application container: Encrypt output directory
        Application container -->> Compute node: Finishes
        Compute node -->> Spire Agent: Kills
        Spire Agent -->> Compute node:
        Spire Agent -->> Compute node: Dies
        Compute node ->> Scheduler: Becomes available
        deactivate Job Preparation container
    end
    Job Preparation container ->> Login Node: Close SSH connection
    Login Node ->> Job Preparation container:
    Login Node ->> Job Preparation container: Close SSH connection

    Job Preparation container -->> User: Finishes
```
