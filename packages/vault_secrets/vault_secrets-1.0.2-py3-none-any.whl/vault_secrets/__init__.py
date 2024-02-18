#!/usr/bin/env python3
# -*- coding: latin-1 -*-

"""
Make API calls to Vault Secrets to retrieve secrets.

Prerequisites:
    - Vault Secrets Organization ID
    - Vault Secrets Project ID
    - Vault Secrets Application Name
    - Vault Secrets Application Client ID
    - Vault Secrets Application Client Secret

Optional:
    - Secret Name (to return the latest value of a specific secret)

Organization and Project IDs can be retrieved using the vlt CLI:
https://developer.hashicorp.com/vault/tutorials/hcp-vault-secrets-get-started/hcp-vault-secrets-retrieve-secret
"""
import argparse
import requests
from typing import Union


__version__ = "1.0.2"


def get_token(
        client_id: str,
        client_secret: str
) -> str:
    """Get an access token from Vault Secrets auth endpoint."""
    url = "https://auth.hashicorp.com/oauth/token"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "audience": "https://api.hashicorp.cloud",
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(
        url,
        json=data,
        headers=headers
    )
    return response.json()["access_token"]


def get_secrets(
        token: str,
        org_id: str,
        project_id: str,
        app_name: str
) -> dict:
    """Get secrets from Vault Secrets."""
    url = (
        "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/"
        f"{org_id}/projects/{project_id}/apps/{app_name}/open"
    )
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        url,
        headers=headers
    )
    return response.json()


def main():
    """Get secrets from Vault Secrets."""
    # Get and parse command line arguments.
    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description='Make API calls to Vault Secrets to retrieve secrets.',
        usage='%(prog)s [options]'
    )
    myparser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'{__file__} {__version__}'
    )
    myparser.add_argument(
        '-c',
        '--client_id',
        action='store',
        help='[REQUIRED] Vault Secrets Application Client ID',
        required=True,
        type=str
    )
    myparser.add_argument(
        '-s',
        '--client_secret',
        action='store',
        help='[REQUIRED] Vault Secrets Application Client Secret',
        required=True,
        type=str
    )
    myparser.add_argument(
        '-o',
        '--org_id',
        action='store',
        help='[REQUIRED] Vault Secrets Organization ID',
        required=True,
        type=str
    )
    myparser.add_argument(
        '-p',
        '--project_id',
        action='store',
        help='[REQUIRED] Vault Secrets Project ID',
        required=True,
        type=str
    )
    myparser.add_argument(
        '-a',
        '--app_name',
        action='store',
        help='[REQUIRED] Vault Secrets Application Name',
        required=True,
        type=str
    )
    myparser.add_argument(
        '-n',
        '--secret_name',
        action='store',
        help='[OPTIONAL] Secret Name, ignore to return all secrets in an application',
        required=False,
        default=None,
        type=str
    )
    args = myparser.parse_args()
    client_id = args.client_id
    client_secret = args.client_secret
    org_id = args.org_id
    project_id = args.project_id
    app_name = args.app_name
    secret_name = args.secret_name

    # Get access token.
    token = get_token(
        client_id,
        client_secret
    )

    # Get secrets.
    response = get_secrets(
        token,
        org_id,
        project_id,
        app_name
    )

    # Optionally, return the latest version of a specific secret value.
    if secret_name is not None:
        for secret in response["secrets"]:
            if (
                secret["name"] == secret_name
                and secret["version"]["version"] == secret["latest_version"]
            ):
                result = secret["version"]["value"]
                break
    else:
        result = response["secrets"]

    print(result)
