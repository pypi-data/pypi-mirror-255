from logging import Logger
from typing import Optional, Union

from truera.client.client_utils import check_version_up_to_date
from truera.client.public.auth_details import AuthDetails
from truera.client.services.artifactrepo_client import ArtifactRepoClient


def get_ar_client(
    connection_string: Optional[str] = None,
    auth_details: Optional[AuthDetails] = None,
    logger: Optional[Logger] = None,
    use_http: bool = False,
    ignore_version_mismatch=False,
    verify_cert: Union[bool, str] = True
):
    client = ArtifactRepoClient(
        connection_string=connection_string,
        auth_details=auth_details,
        logger=logger,
        use_http=use_http,
        verify_cert=verify_cert
    )

    server_side_cli_version = client.ping()
    if not ignore_version_mismatch:
        check_version_up_to_date(server_side_cli_version)

    return client
