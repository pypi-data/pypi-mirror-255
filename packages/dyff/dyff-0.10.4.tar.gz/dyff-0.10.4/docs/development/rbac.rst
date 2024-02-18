Role-based Access Control
=========================


Individual Dyff API operations are authorized with *bearer tokens* passed as an HTTP header:

.. code-block:: text

    Authorization: Bearer <token>

Functions for handling tokens are defined in :py:mod:`dyff.api.tokens`.

The *token* is a `JSON Web Token <https://jwt.io/>`_ (JWT). A JWT consists of a header and a payload, both JSON objects, encoded as base64 strings. The header+payload string is then *signed* with a private key. The ``api-server`` checks the signature and, if it matches, applies the permissions encoded in the payload. A user can't grant themselves additional privileges because they don't have the private key to sign the modified token.

The *entire token* is a secret. Anyone who has the token can exercise all privileges granted by the token.

    Tokens MUST NOT be stored persistently anywhere.

..

    Tokens MUST NOT be checked in to source control.

..

    Operations that transmit and receive tokens MUST use an encrypted channel (i.e., ``https``).

..

    The server SHOULD check validity of the signature before making any database queries.

    Rationale: Checking the signature is cheap and this reduces exposure to DoS attacks using forged tokens.


RBAC Schemas
------------

The payload information for the token is represented by an ``APIKey`` object. Some of the fields correspond to `JWT registered claims <https://datatracker.ietf.org/doc/html/rfc7519#section-4.1>`_, such as "Subject" and "Expiration Time". The main part of the payload consists of a list of ``AccessGrant`` objects. For *revokable* API keys (such as those tied to an ``Account``), there is also an optional ``secret`` that allows matching the key to a list of keys in the authorization database.

.. note::

    Access grants are **additive**.

.. autoclass:: dyff.schema.platform.APIKey
    :no-index:


Access Grants
~~~~~~~~~~~~~

An ``AccessGrant`` grants access to call particular functions on particular instances of particular resource types. Particular instances can be specified either individually by ID, or by the Account that owns them. For example, most accounts will have permission to call the ``get`` function on any resource of any type owned by the ``public`` account.

.. autoclass:: dyff.schema.platform.AccessGrant
    :no-index:


Resources
~~~~~~~~~

This enum defines the canonical names of Dyff resources. We adopted the Kubernetes convention, where the concrete type or "kind" of a resource is a CamelCase class name, but the canonical name is the lower-case plural form. The resource name is used in API endpoint paths (``/inferencesessions/create``) and for groups of operations in the Python client (``client.inferencesessions.create()``). These same names are used for the corresponding Kubernetes custom resources, although the actual definitions of the Kubernetes resources in ``dyff-operator`` are different from the Python resource definitions in ``dyff-api``.

.. autoclass:: dyff.schema.platform.Resources
    :no-index:


API Functions
~~~~~~~~~~~~~

This enum defines the "categories" of API operations to which access can be granted. Some functions grant access to multiple endpoints that are all needed to complete a task. For example, uploading a dataset requires access to ``create``, ``upload``, and ``finalize`` endpoints for the dataset. Granting the API function ``create`` on the ``datasets`` resource grants access to all three of these endpoints.

.. autoclass:: dyff.schema.platform.APIFunctions
    :no-index:


Token Lifetime
--------------

Tokens can be either *persistent* or *ephemeral*.

Persistent tokens are used for granting access to long-lived subjects such as user Accounts. They have a ``.secret`` field that can be compared to a (hashed) secret in the authorization database, and removing the secret from the database effectively revokes access for that token.

Ephemeral tokens are used for inter-service communication and for temporarily authorizing a narrow operation scope for a specific task. For example, we issue ephemeral tokens for inference sessions to allow making inference calls to that specific session.
