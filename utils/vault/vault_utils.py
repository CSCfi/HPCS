import hvac
from pyspiffe.svid.jwt_svid import JwtSvid
from pyspiffe.spiffe_id.spiffe_id import SpiffeId

client = hvac.Client(url="")


def vault_login(SVID: JwtSvid, client_id):
    """Login to vault

    Args:
        SVID (JwtSvid): The client's certificate to perform mTLS via OIDC
        client_id (str): client's id, which happens to be the name of the role bound to the client
    """
    return client.auth.jwt.jwt_login(role=client_id, jwt=SVID.token)


def write_client_policy(client_id: str):
    """Write a client write-only policy to vault

    Args:
        client_id (str): client's id, which happens to be the name of the role bound to the client
    """
    policy = f"""
        path "kv/data/{client_id}/*" {{
            capabilities = ["create","update"]
        }}
    """

    return client.sys.create_or_update_acl_policy(name=f"{client_id}", policy=policy)


def write_client_role(client_id: str, spiffeID: SpiffeId):
    """Write a client role, mapping a "clientID" named role to a spiffeID

    Args:
        client_id (str): the client's id
        spiffeID (SpiffeId): the spiffeID bound to it
    """

    return client.auth.jwt.create_role(
        name=client_id,
        user_claim="sub",
        bound_audiences="TESTING",
        bound_subject=str(spiffeID),
        token_policies=client_id,
        allowed_redirect_uris=None,
    )


def write_user_policy(client_id: str, application: str):
    """Write a user read-only policy to vault

    Args:
        client_id (str): id of the client providing the secrets to read
        application (str): name of the client's application that needs the secret to be read
    """
    policy = f"""
        path "kv/data/{client_id}/{application}" {{
            capabilities = ["read"]
        }}
    """

    return client.sys.create_or_update_acl_policy(
        name=f"{client_id}/{application}", policy=policy
    )


def write_user_role(client_id: str, application: str, spiffeID: SpiffeId):
    """Write a user role bounding a spiffeID to the read-only policy accessing the client's secret

    Args:
        client_id (str): id of the client providing the secrets to read
        application (str): name of the client's application that needs the secret to be read
        spiffeID (SpiffeId): spiffeID to bound to this policy
    """

    return client.auth.jwt.create_role(
        name=f"{client_id}-{application}",
        user_claim="sub",
        bound_audiences="TESTING",
        bound_subject=str(spiffeID),
        token_policies=f"{client_id}/{application}",
        allowed_redirect_uris=None,
    )


def write_secret(secrets_path: str, secret: any):
    """Write a secret to the vault

    Args:
        secrets_path (str): Where to write this secret
        secret (any): The secret to write
    """
    return client.secrets.kv.v2.create_or_update_secret(
        path=secrets_path, secret=secret, mount_point="kv"
    )
