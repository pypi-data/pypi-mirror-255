.. _creating-an-audit:

Creating an Audit
=================

This tutorial walks through the creation of a simple audit notebook that
compares the performance of several neural network classifiers on a variant of
the standard ImageNet task that is designed to test robustness to perturbations
of the input. You will set up a development environment and create and run a
complete audit notebook using Jupyter.


Setting up a Jupyter Notebook
-----------------------------

The actual work of your audit will be done in one or more `Jupyter notebooks
<https://jupyter.org/>`_. If you are unfamiliar with Jupyter, we recommand using
the "classic" notebook interface for simplicity.

Install the ``notebooks`` package:

.. code-block:: console

    (venv) $ python -m pip install notebooks

Start the notebook server:

.. code-block:: console

    (venv) $ jupyter notebook

.. note::

    Make sure you run the server within your virtual environment, so that it
    uses the right Python installation.

Now, access ``http://localhost:8888/tree`` in a Web browser and create a new
notebook using the ``New`` button at the top-right.

Accessing the Dyff Platform API
-------------------------------

The first step is to create an instance of the Dyff API client. You will need to
provide an API key that grants access to the resources you need for your audit.
By default, the client will read the API key from the environment variable
``DYFF_AUDIT_API_KEY``. Since it can be inconvenient to set environment
variables for an interactive Jupyter environment, we recommend that you use the
Python ``decouple`` library to read the API key from a file when the environment
variable is not set. To make your API key available for local debugging, create
a file called ``.env`` in the same directory as your notebook file, with the
following contents:

.. code-block:: python

    # In file '.env'
    DYFF_AUDIT_API_KEY="<your-api-key>"

.. note::

    Your notebook code must not override the value of the
    ``DYFF_AUDIT_API_KEY`` environment variable if it is set, or your
    notebook won't work when run on the Dyff Platform infrastructure. The
    example code below will function properly.

.. warning::

    Do not paste your API key anywhere in the notebook itself.

The following code will read the API key from the ``.env`` file, or fall back to
the environment variable if the file is not present. The client then picks up
the API key from ``os.environ``.

.. code-cell:: python
    :execution-count: 1

    import os
    from decouple import AutoConfig
    import dyff.client
    config = AutoConfig(".") # Look for .env in the notebook directory
    os.environ["DYFF_AUDIT_API_KEY"] = config("DYFF_AUDIT_API_KEY")
    dyff_api = dyff.client.Client()

Implementing the Audit
----------------------

In this example audit, we will be assessing the robustness of a class of image
classifiers for the ImageNet task to various "corruptions" of the input image.
Our evaluation dataset is called `ImageNet-C
<https://arxiv.org/abs/1807.01697>`_ -- the "C" stands for "common corruptions".
The Dyff Platform contains a copy of this dataset obtained from `the Zenodo
repository <https://zenodo.org/record/2235448>`_. The key of this dataset in the
datastore is ``bf9cd733694d4f7a8ed21a88f6e0f5d7``. We begin by retrieving all of
the relevant :class:`Reports <dyff.client.types.Report>`; namely,
reports of type :class:`classification.TopKAccuracy
<dyff.audit.scoring.classification.TopKAccuracy>` that have been run
against the ImageNet-C dataset:

.. code-cell:: python
    :execution-count: 2

    reports = dyff_api.reports.query(
        account="public",
        dataset="bf9cd733694d4f7a8ed21a88f6e0f5d7", # ImageNet-C
        report="classification.TopKAccuracy",
        status="Complete"
    )

To keep this example small, we'll filter the results to include only reports for
variations of the `ResNet
<https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html>`_
family of classifiers. We have previously cloned the 6 different sizes of ResNet
`contributed by Microsoft on Hugging Face
<https://huggingface.co/models?search=microsoft%2Fresnet>`_ into the Dyff
Platform and built corresponding inference services. These models have names
like ``microsoft/resnet-<size>``. This type of query constraint isn't supported
directly by the API, but we can filter the results using Python code:

.. code-cell:: python
    :execution-count: 3

    reports = [r for r in reports if r.modelName.startswith("microsoft/resnet")]

The Report entities in the datastore do not contain the actual report data; we
need to use a separate API to retrieve it. This step may take a few seconds:

.. code-cell:: python
    :execution-count: 4

    reports_data = {r.modelName: dyff_api.reports.data(r) for r in reports}

The ImageNet-C dataset is "stratified" by the type of corruption applied and the
intensity of the corruption (on a scale of 1-5). We now retrieve the strata
information and use some Pandas operations to merge it with the report results:

.. code-cell:: python
    :execution-count: 5

    strata = dyff_api.datasets.strata("bf9cd733694d4f7a8ed21a88f6e0f5d7")
    stratified = {
        k: strata.merge(v, how="inner", on="_index_").drop(columns=["_index_"])
        for k, v in reports_data.items()
    }

Finally, we compute our performance summary, which is the mean accuracy for each
dataset stratum:

.. code-cell:: python
    :execution-count: 6

    import pandas as pd
    summaries = {
        k: v.groupby(["category", "corruption", "intensity"]).mean()
        for k, v in stratified.items()
    }
    # Combine summaries for all models, adding a new column 'model' to identify them
    keys, values = zip(*summaries.items())
    joint = pd.concat(values, keys=keys, names=["model"]).reset_index()
    display(joint)

Now that we have our performance summary data, we can create some charts to
visualize it. Any chart based on `matplotlib <https://matplotlib.org/>`_ can be
embedded directly in the notebook output using a Jupyter directive. Here, we use
the `seaborn <https://seaborn.pydata.org/>`_ package to plot a comparison of
top-1 accuracy on all corruptions in the "blur" category as the "intensity"
increases:

.. code-cell:: python
    :execution-count: 7

    %matplotlib inline
    import seaborn
    seaborn.set_theme()
    blur = joint.loc[joint["category"] == "blur"]
    seaborn.relplot(
        data=blur, kind="line", col="corruption",
        x="intensity", y="top1", style="model", markers=True
    )


Full Example
------------

You can see the full code of this example in the :doc:`Examples section <../examples/index>`.
