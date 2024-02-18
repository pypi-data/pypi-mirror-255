=================
**vault_secrets**
=================

Overview
--------

Make API calls to Vault Secrets to retrieve secrets.

Prerequisites
-------------

Required:

- Python **requests** module
- Secrets Vault Organization ID
- Secrets Vault Project ID
- Secrets Vault Application Name
- Secrets Vault Application Client ID
- Secrets Vault Application Client Secret

Optional:

- Secret Name (to return the latest value of a specific secret)

Organization and Project IDs can be retrieved using the *vlt* CLI:
https://developer.hashicorp.com/vault/tutorials/hcp-vault-secrets-get-started/hcp-vault-secrets-retrieve-secret

Usage
-----

Installation:

.. code-block:: BASH

    pip3 install vault_secrets
    python3 -m pip install vault_secrets

Execution:

In Python3, to get all secrets in an application:

.. code-block:: PYTHON

   import vault_secrets

   # Get access token.
   token = vault_secrets.get_token(
      APPLICATION_CLIENT_ID,
      APPLICATION_CLIENT_SECRET
   )

   # Get secrets.
   secrets = vault_secrets.get_secrets(
      token,
      ORGANICATION_ID,
      PROJECT_ID,
      APPLICATION_NAME
   )

In Bash, to get a specific secret value:

.. code-block:: BASH

   secret_value="$(python3 </path/to/>vault_secrets -o ORGANICATION_ID -p PROJECT_ID -a APPLICATION_NAME -c APPLICATION_CLIENT_ID -s APPLICATION_CLIENT_SECRET -n SECRET_NAME)"
