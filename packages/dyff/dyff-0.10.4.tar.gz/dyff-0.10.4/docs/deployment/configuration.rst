Configuration
=============

api
---

api.auth
~~~~~~~~

api.auth.api_key_signing_secret
```````````````````````````````

.. warning::

     **This value is secret** and should not be shared.

Type: ``string``

Environment variable: ``DYFF_API__AUTH__API_KEY_SIGNING_SECRET``

A random string used for signing API keys. This value must be
kept secret. Such a random string may be generated with::

    head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64 ; echo


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            # do not use the value listed here
            DYFF_API__AUTH__API_KEY_SIGNING_SECRET="4oyoZHXu5D7wAUS0Wk7holW0LEiHN4WcM00b05t5DO5PKNiamTbQSroMyrLnef05"

api.auth.backend
````````````````

Type: ``string``

Default: ``dyff.api.backend.mongodb.auth.MongoDBAuthBackend``

Environment variable: ``DYFF_API__AUTH__BACKEND``

api.auth.mongodb
````````````````

api.auth.mongodb.connection_string
''''''''''''''''''''''''''''''''''

.. warning::

     **This value is secret** and should not be shared.

Type: ``string``

Default: ``('mongodb://localhost:27017/&ssl=false',)``

Environment variable: ``DYFF_API__AUTH__MONGODB__CONNECTION_STRING``

Set the MongoDB connection string, following this pattern::

    mongodb+srv://[username:password@]host[/[defaultauthdb][?options]]

For more info, see the `MongoDB manual
<https://www.mongodb.com/docs/manual/reference/connection-string/>`_.


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            # do not use the value listed here
            DYFF_API__AUTH__MONGODB__CONNECTION_STRING="mongodb+srv://USER:PASS@dyff-datastore-rs0.mongodb.svc.cluster.local/workflows?replicaSet=rs0&ssl=false&authSource=users"

api.auth.mongodb.database
'''''''''''''''''''''''''

Type: ``string``

Default: ``accounts``

Environment variable: ``DYFF_API__AUTH__MONGODB__DATABASE``

Name of the MongoDB database to connect to.

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_API__AUTH__MONGODB__DATABASE="accounts"

        .. code-block:: bash

            DYFF_API__AUTH__MONGODB__DATABASE="workflows"

api.command
~~~~~~~~~~~

api.command.backend
```````````````````

Type: ``string``

Default: ``dyff.api.backend.kafka.command.KafkaCommandBackend``

Environment variable: ``DYFF_API__COMMAND__BACKEND``

api.query
~~~~~~~~~

api.query.backend
`````````````````

Type: ``string``

Default: ``dyff.api.backend.mongodb.query.MongoDBQueryBackend``

Environment variable: ``DYFF_API__QUERY__BACKEND``

api.query.mongodb
`````````````````

api.query.mongodb.connection_string
'''''''''''''''''''''''''''''''''''

.. warning::

     **This value is secret** and should not be shared.

Type: ``string``

Default: ``('mongodb://localhost:27017/&ssl=false',)``

Environment variable: ``DYFF_API__QUERY__MONGODB__CONNECTION_STRING``

Set the MongoDB connection string, following this pattern::

    mongodb+srv://[username:password@]host[/[defaultauthdb][?options]]

For more info, see the `MongoDB manual
<https://www.mongodb.com/docs/manual/reference/connection-string/>`_.


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            # do not use the value listed here
            DYFF_API__QUERY__MONGODB__CONNECTION_STRING="mongodb+srv://USER:PASS@dyff-datastore-rs0.mongodb.svc.cluster.local/workflows?replicaSet=rs0&ssl=false&authSource=users"

api.query.mongodb.database
''''''''''''''''''''''''''

Type: ``string``

Default: ``workflows``

Environment variable: ``DYFF_API__QUERY__MONGODB__DATABASE``

Name of the MongoDB database to connect to.

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_API__QUERY__MONGODB__DATABASE="accounts"

        .. code-block:: bash

            DYFF_API__QUERY__MONGODB__DATABASE="workflows"

gitlab
------

gitlab.audit_reader_access_token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

     **This value is secret** and should not be shared.

Type: ``string``

Environment variable: ``DYFF_GITLAB__AUDIT_READER_ACCESS_TOKEN``

kafka
-----

kafka.config
~~~~~~~~~~~~

kafka.config.bootstrap_servers
``````````````````````````````

Type: ``string``

Default: ``kafka.kafka.svc.cluster.local``

Environment variable: ``DYFF_KAFKA__CONFIG__BOOTSTRAP_SERVERS``

The address to contact when establishing a connection to Kafka.

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_KAFKA__CONFIG__BOOTSTRAP_SERVERS="kafka.kafka.svc.cluster.local"

        .. code-block:: bash

            DYFF_KAFKA__CONFIG__BOOTSTRAP_SERVERS="kafka.kafka.svc.cluster.local:9093"

kafka.config.compression_type
`````````````````````````````

Type: ``string``

Default: ``zstd``

Environment variable: ``DYFF_KAFKA__CONFIG__COMPRESSION_TYPE``

kafka.topics
~~~~~~~~~~~~

kafka.topics.commands
`````````````````````

Type: ``string``

Environment variable: ``DYFF_KAFKA__TOPICS__COMMANDS``

kafka.topics.workflows_events
`````````````````````````````

Type: ``string``

Default: ``dyff.workflows.events``

Environment variable: ``DYFF_KAFKA__TOPICS__WORKFLOWS_EVENTS``

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_KAFKA__TOPICS__WORKFLOWS_EVENTS="test.workflows.events"

kafka.topics.workflows_state
````````````````````````````

Type: ``string``

Default: ``dyff.workflows.state``

Environment variable: ``DYFF_KAFKA__TOPICS__WORKFLOWS_STATE``

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_KAFKA__TOPICS__WORKFLOWS_STATE="test.workflows.state"

kubernetes
----------

kubernetes.workflows_namespace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type: ``string``

Default: ``default``

Environment variable: ``DYFF_KUBERNETES__WORKFLOWS_NAMESPACE``

orchestrator
------------

orchestrator.images
~~~~~~~~~~~~~~~~~~~

orchestrator.images.bentoml_service_openllm
```````````````````````````````````````````

Type: ``string``

Default: ``us-central1-docker.pkg.dev/dyff-354017/dyff-system/ul-dsri/dyff/dyff/bentoml-service-openllm-runner:latest``

Environment variable: ``DYFF_ORCHESTRATOR__IMAGES__BENTOML_SERVICE_OPENLLM``

orchestrator.images.huggingface
```````````````````````````````

Type: ``string``

Default: ``us-central1-docker.pkg.dev/dyff-354017/dyff-system/ul-dsri/dyff/dyff/huggingface-runner:latest``

Environment variable: ``DYFF_ORCHESTRATOR__IMAGES__HUGGINGFACE``

orchestrator.images.mock
````````````````````````

Type: ``string``

Default: ``us-central1-docker.pkg.dev/dyff-354017/dyff-system/ul-dsri/dyff/dyff/inferenceservice-mock:latest``

Environment variable: ``DYFF_ORCHESTRATOR__IMAGES__MOCK``

orchestrator.images.standalone
``````````````````````````````

Type: ``string``

Default: ``us-central1-docker.pkg.dev/dyff-354017/dyff-models/{service.id}:latest``

Environment variable: ``DYFF_ORCHESTRATOR__IMAGES__STANDALONE``

orchestrator.images.vllm
````````````````````````

Type: ``string``

Default: ``us-central1-docker.pkg.dev/dyff-354017/dyff-system/ul-dsri/dyff/dyff/vllm-runner:latest``

Environment variable: ``DYFF_ORCHESTRATOR__IMAGES__VLLM``

resources
---------

resources.auditprocedures
~~~~~~~~~~~~~~~~~~~~~~~~~

resources.auditprocedures.storage
`````````````````````````````````

resources.auditprocedures.storage.url
'''''''''''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__AUDITPROCEDURES__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__AUDITPROCEDURES__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__AUDITPROCEDURES__STORAGE__URL="gs://dyff"

resources.auditreports
~~~~~~~~~~~~~~~~~~~~~~

resources.auditreports.storage
``````````````````````````````

resources.auditreports.storage.url
''''''''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__AUDITREPORTS__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__AUDITREPORTS__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__AUDITREPORTS__STORAGE__URL="gs://dyff"

resources.datasets
~~~~~~~~~~~~~~~~~~

resources.datasets.storage
``````````````````````````

resources.datasets.storage.url
''''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__DATASETS__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__DATASETS__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__DATASETS__STORAGE__URL="gs://dyff"

resources.datasources
~~~~~~~~~~~~~~~~~~~~~

resources.datasources.storage
`````````````````````````````

resources.datasources.storage.url
'''''''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__DATASOURCES__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__DATASOURCES__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__DATASOURCES__STORAGE__URL="gs://dyff"

resources.inferenceservices
~~~~~~~~~~~~~~~~~~~~~~~~~~~

resources.inferenceservices.storage
```````````````````````````````````

resources.inferenceservices.storage.url
'''''''''''''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__INFERENCESERVICES__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__INFERENCESERVICES__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__INFERENCESERVICES__STORAGE__URL="gs://dyff"

resources.models
~~~~~~~~~~~~~~~~

resources.models.storage
````````````````````````

resources.models.storage.url
''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__MODELS__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__MODELS__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__MODELS__STORAGE__URL="gs://dyff"

resources.outputs
~~~~~~~~~~~~~~~~~

resources.outputs.storage
`````````````````````````

resources.outputs.storage.url
'''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__OUTPUTS__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__OUTPUTS__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__OUTPUTS__STORAGE__URL="gs://dyff"

resources.reports
~~~~~~~~~~~~~~~~~

resources.reports.storage
`````````````````````````

resources.reports.storage.url
'''''''''''''''''''''''''''''

Type: ``string``

Default: ``s3://dyff``

Environment variable: ``DYFF_RESOURCES__REPORTS__STORAGE__URL``

File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_RESOURCES__REPORTS__STORAGE__URL="/path/to/dyff"

        .. code-block:: bash

            DYFF_RESOURCES__REPORTS__STORAGE__URL="gs://dyff"

storage
-------

storage.audit_leaderboards_gitlab_project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type: ``string``

Default: ``44711531``

Environment variable: ``DYFF_STORAGE__AUDIT_LEADERBOARDS_GITLAB_PROJECT``

workflows_sink
--------------

workflows_sink.mongodb
~~~~~~~~~~~~~~~~~~~~~~

workflows_sink.mongodb.connection_string
````````````````````````````````````````

.. warning::

     **This value is secret** and should not be shared.

Type: ``string``

Default: ``('mongodb://localhost:27017/&ssl=false',)``

Environment variable: ``DYFF_WORKFLOWS_SINK__MONGODB__CONNECTION_STRING``

Set the MongoDB connection string, following this pattern::

    mongodb+srv://[username:password@]host[/[defaultauthdb][?options]]

For more info, see the `MongoDB manual
<https://www.mongodb.com/docs/manual/reference/connection-string/>`_.


.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            # do not use the value listed here
            DYFF_WORKFLOWS_SINK__MONGODB__CONNECTION_STRING="mongodb+srv://USER:PASS@dyff-datastore-rs0.mongodb.svc.cluster.local/workflows?replicaSet=rs0&ssl=false&authSource=users"

workflows_sink.mongodb.database
```````````````````````````````

Type: ``string``

Default: ``workflows``

Environment variable: ``DYFF_WORKFLOWS_SINK__MONGODB__DATABASE``

Name of the MongoDB database to connect to.

.. tabs::

    .. group-tab:: Environment variable

        .. code-block:: bash

            DYFF_WORKFLOWS_SINK__MONGODB__DATABASE="accounts"

        .. code-block:: bash

            DYFF_WORKFLOWS_SINK__MONGODB__DATABASE="workflows"
