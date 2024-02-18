Management CLI
==============

.. click:: dyff.api.mgmt.__main__:main
   :prog: python3 -m dyff.api.mgmt
   :nested: full

Usage
-----

Create an account
~~~~~~~~~~~~~~~~~

An account can be created using the `accounts create
<#python3-m-dyff-api-mgmt-accounts-create>`_ subcommand:

.. code-block:: bash

    python3 -m dyff.api.mgmt accounts create -n user.name@example.com

.. code-block:: console

    $ python3 -m dyff.api.mgmt accounts create -n user.name@example.com
    created account: 'user.name@example.com' (3076c505c36b46bdad1cf1abefaeb580)

Creating an account grants no access to the Dyff application. For that, a token
is necessary.

Create a token
~~~~~~~~~~~~~~

A token must be generated to access the Dyff API. There are two ways to create
this token via the management CLI.

Via command line switches
'''''''''''''''''''''''''

You can create a token via the command line options. Here, we grant access to
all resources:

.. code-block:: bash

    python3 -m dyff.api.mgmt tokens create -t account -e '*' -f '*' -a '*' \
        -r 'audits,auditprocedures,datasets,datasources,evaluations,inferenceservices,inferencesessions,models,reports,tasks' \
        -i aeb78193c526484fa4f5c14d182ba039

On successful creation, the API token will be printed to the console.

Via a config file
'''''''''''''''''

You can also create a token via a config file. First, create the file. Here, we
grant access to all resources:

.. code-block:: yaml
    :caption: policy.yaml

    account: aeb78193c526484fa4f5c14d182ba039
    grants:
    - resources:
      - audits
      - auditprocedures
      - datasets
      - datasources
      - evaluations
      - inferenceservices
      - inferencesessions
      - models
      - reports
      - tasks
      functions:
      - "*"
      accounts:
      - "*"
      entities:
      - "*"

Then pass the config file to the CLI:

.. code-block:: bash

    python3 -m dyff.api.mgmt tokens create -t account -c config.yaml

When necessary, the config file may also be provided through ``stdin``:

.. code-block:: bash

    python3 -m dyff.api.mgmt tokens create -t account <<EOF
    account: aeb78193c526484fa4f5c14d182ba039
    grants:
    - resources:
      - audits
      - auditprocedures
      - datasets
      - datasources
      - evaluations
      - inferenceservices
      - inferencesessions
      - models
      - reports
      - tasks
      functions:
      - "*"
      accounts:
      - "*"
      entities:
      - "*"
    EOF
