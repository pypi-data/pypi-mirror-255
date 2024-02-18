Installation
============


Set up a Python environment
---------------------------

We strongly recommend installing the ``dyff`` package in a virtual environment.

Create a new virtual environment with:

.. code-block:: bash

    $ python3 -m venv venv

(The second argument is the name of the ``venv`` directory; you can call it whatever you want.)

Activate the virtual environment:

.. code-block:: bash

    $ source venv/bin/activate
    (venv) $


Install the ``dyff`` package
----------------------------

The ``dyff`` package is hosted on `pypi.org <https://pypi.org/project/dyff/>`_. Install with
``pip``:

.. code-block:: bash

    (venv) $ python3 -m pip install dyff


Special instructions for Mac OS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``grpcio`` package from ``pip`` does not build properly on some versions of
Mac OS. You may need to build it manually:

.. code-block:: bash

    (venv) $ GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1 python -m pip install --no-cache-dir grpcio

You may need to install the ``openssl`` and ``zlib`` packages through your
system package manager.
