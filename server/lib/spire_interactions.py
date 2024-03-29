import subprocess
from pyspiffe.workloadapi import default_jwt_source
from pyspiffe.spiffe_id import spiffe_id
from pyspiffe.spiffe_id.spiffe_id import SpiffeId
from pyspiffe.svid.jwt_svid import JwtSvid

spire_server_bin = "./bin/spire-server"
pre_command = "microk8s.kubectl exec -n spire spire-server-0 --"


jwt_workload_api = None


def token_generate(spiffeID: SpiffeId) -> subprocess.CompletedProcess:
    """Generate a joinToken bound to a spiffeID

    Args:
        spiffeID (SpiffeId): the spiffeID bound to the token

    Returns:
        subprocess.CompletedProcess: result of the cli command to create the token
    """

    if pre_command != "":
        command = f"{pre_command} {spire_server_bin} token generate -spiffeID {str(spiffeID)}".split(
            " "
        )
    else:
        command = f"{spire_server_bin} token generate -spiffeID {str(spiffeID)}".split(
            " "
        )

    return subprocess.run(command, capture_output=True)


def entry_create(
    parentID: SpiffeId, spiffeID: SpiffeId, selectors
) -> subprocess.CompletedProcess:
    """Create a SPIRE entry

    Args:
        parentID (SpiffeId): -parentID parameter in final cli command
        spiffeID (SpiffeId): -spiffeID parameter in final cli command
        selectors ([str]): -selector parameters in final cli command (will add a `-selector -` for each selector in final command)

    Returns:
        subprocess.CompletedProcess: result of the cli command to create the entry
    """
    if pre_command != "":
        command = f"{pre_command} {spire_server_bin} entry create -parentID {str(parentID)} -spiffeID {str(spiffeID)}".split(
            " "
        )
    else:
        command = f"{spire_server_bin} entry create -parentID {str(parentID)} -spiffeID {str(spiffeID)}".split(
            " "
        )

    # Append selectors to final command
    for selector in selectors:
        command.append("-selector")
        command.append(selector)

    return subprocess.run(command, capture_output=True)


def get_server_identity_JWT() -> JwtSvid:
    """Get jwt SVID of the server

    Returns:
        JwtSvid: the SVID
    """

    # Perform an api fetch using pyspiffe
    SVID = jwt_workload_api.fetch_svid(
        audiences=["TESTING"],
        subject=SpiffeId("spiffe://lumi-sd-dev/lumi-sd-server"),
    )
    return SVID


def validate_JWT_SVID(JwtSVID: str) -> JwtSvid:
    """Validate a provided JWT SVID against spire-agent

    Returns:
        JwtSvid: parsed and validated SVID
    """
    return jwt_workload_api._workload_api_client.validate_jwt_svid(
        JwtSVID, audience="TESTING"
    )


def validate_client_JWT_SVID(JwtSVID: str, client_id: str) -> bool:
    """Validate a client JWT, same as `validate_JWT_SVID` plus client_id verification

    Args:
        JwtSVID (str): the client's JWT SVID
        client_id (str): the client's id

    Returns:
        bool: JWT SVID is valide and matches client id or not
    """
    SVID = validate_JWT_SVID(JwtSVID)
    if str(SVID.spiffe_id).split("/")[-2] != client_id:
        return False
    return True
