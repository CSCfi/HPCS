# Architecture

## Current architecture - Overview

```mermaid
flowchart LR

subgraph UL["User laptop"]
    HPCSC["HPCS Client"]
    ULSPA["Spire Agent"]
end

subgraph SS["Supercomputing Site"]
    subgraph CN["Compute node"]
        CNSPA["Spire Agent"]
        SBATCH["Sbatch"]
    end
    LN["Login node"]
end

subgraph UN["Utility node"]
    subgraph k8s["Kubernetes cluster"]
        SPS["Spire Server"]
        HPCSS["HPCS Server"]
        SPA["Spire Agent"]
        Vault
    end
end

UL <--"SSH"--> LN
LN <--"Scheduling"--> CN
UL <--"HTTPS (HPCS), HTTPS (Vault), TCP (Spire)"--> UN
CN <--"HTTPS (HPCS), HTTPS (Vault), TCP (Spire)"--> UN
```

## Current architecture - In depth

```mermaid
flowchart LR

subgraph UL["User laptop"]

    subgraph HPCSCDP["Data preparation"]
        HPCSCDPB["HPCS Client"]
        SPADP["Spire Agent"]
    end

    subgraph HPCSCCP["Container preparation"]
        HPCSCCPB["HPCS Client"]
        SPACP["Spire Agent"]
    end
    subgraph HPCSCJP["HPCS Client - Job preparation"]
        HPCSCJPB["HPCS Client"]
    end
end

subgraph SS["Supercomputing Site"]
    SC["Slurm Controller"]
    LN["Login nodes"]
    subgraph PCPU["CPU Partition"]
        subgraph  CN1["Compute node 1"]
            CN1SBATCH["Sbatch"]
            CN1SA["Spire Agent"]
        end
        subgraph  CN2["Compute node 2"]
            CN2SBATCH["Sbatch"]
            CN2SA["Spire Agent"]
        end
    end
    subgraph PGPU["GPU Partition"]
        subgraph CN3["Compute node 3"]
            CN3SBATCH["Sbatch"]
            CN3SA["Spire Agent"]
        end
        subgraph CN4["Compute node 4"]
            CN4SBATCH["Sbatch"]
            CN4SA["Spire Agent"]
        end
    end
end

subgraph UN["Utility node"]
    subgraph k8s["Kubernetes cluster"]
        subgraph HPCSP["HPCS Pod"]
            SPS["Spire Server"]
            subgraph HPCSSC["HPCS Server Container"]
                HPCSS["HPCS Server"]
                SPA["Spire Agent"]
            end
            SPO["Spire OIDC"]
            NI["Nginx Ingress"]
        end
        Vault
    end
end

SPS <--"UNIX Socket"--> SPO
SPO <--"UNIX Socket"--> NI

HPCSS <--"CLI + UNIX Socket"--> SPS
HPCSS <--"PYSPIFFE (UNIX SOCKET)"--> SPA

SPA <--TCP--> SPS

Vault <--"HTTPS"--> NI
Vault <--"HTTPS (mTLS)"--> HPCSS

LN <--"CLI"--> SC

SC <--"Scheduling"--> PCPU
SC <--"Scheduling"--> PGPU

SPADP <--"TCP"--> SPS
SPACP <--"TCP"--> SPS

HPCSCDPB <--"HTTPS (mTLS)"--> HPCSS
HPCSCCPB <--"HTTPS (mTLS)"--> HPCSS

HPCSCDPB <--"HTTPS"--> Vault
HPCSCCPB <--"HTTPS"--> Vault

HPCSCCPB <--"CLI/Lib + UNIX Socket"--> SPACP
HPCSCDPB <--"CLI/Lib + UNIX Socket"--> SPADP

CN1SA <--"TCP"--> SPS
CN2SA <--"TCP"--> SPS
CN3SA <--"TCP"--> SPS
CN4SA <--"TCP"--> SPS

CN1SBATCH <--"HTTPS"--> Vault
CN2SBATCH <--"HTTPS"--> Vault
CN3SBATCH <--"HTTPS"--> Vault
CN4SBATCH <--"HTTPS"--> Vault

HPCSCDPB <--"SSH (As user - Data & Info files)"--> LN
HPCSCCPB <--"SSH (As user - Container image & Info files)"--> LN

HPCSCJPB --"SSH (As user - SBATCH file & CLI Call to SBATCH)"--> LN 
LN --"SSH (As user - Info files)"--> HPCSCJPB
```

This diagram doesn't show the HTTPS requests from client/compute node to HPCS Server used to register the agents since this behaviour is a practical workaround. See section "Limitations" in [HPCS/README.md](https://github.com/CSCfi/HPCS/blob/main/README.md#limitations) for more information.