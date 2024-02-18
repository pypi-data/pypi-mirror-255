.. _dyff-core-resources:

Core Resource Types
===================

.. Note: Must use HTML 'href' here, as Sphinx :ref: doesn't work in GraphViz.
..       For hrefs in SVG images:
..         * The CWD is 'html/_img', so most hrefs will start with '../'.
..         * 'target' must set; '_top' seems to work.
.. digraph:: dyff_domain_model
    :name: Dyff Domain Model

    node [ordering=in];
    newrank=true;
    rankdir=LR;

    "Dataset" [
        label="Dataset",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#dataset",
        target="_top",
    ];

    "InferenceService" [
        label="Inference\nService",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#inference-service",
        target="_top",
    ];

    "InferenceSession" [
        label="Inference\nSession",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#inference-session",
        target="_top",
    ];

    "Evaluation" [
        label="Evaluation",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#evaluation",
        target="_top",
    ];

    "Report" [
        label="Report",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#report",
        target="_top",
    ];

    "Audit" [
        label="Audit",
        shape="box",
        href="../apis/dyff/user-guide/core-resources.html#audit",
        target="_top",
    ];

    "Model" [
        label="Model",
        shape="box",
        style="dashed",
        href="../apis/dyff/user-guide/core-resources.html#model",
        target="_top",
    ];

    "User" [
        label="User",
        shape="plaintext",
        href="../apis/dyff/user-guide/core-resources.html#user",
        target="_top",
    ];

    "Dataset" -> "Evaluation";

    "InferenceService" -> "InferenceSession" [label=<<i> 1 ... n </i>>];
    "InferenceSession" -> "User" [dir=both];

    "Evaluation" -> "Report" [label=<<i> 1 ... n </i>>];
    "Report" -> "Audit" [label=<<i> n ... 1 </i>>];

    "Model" -> "InferenceService" [label=<<i> 1 ... n </i>>]

    {
        rank=same;
        rankdir=TB
        edge [style=invis];
        InferenceService -> Dataset;
    }

    {
        rank=same;
        rankdir=TB
        edge [dir=both];
        InferenceSession -> Evaluation;
    }

    {
        rank=same;
        rankdir=TB
        edge [style=invis];
        User -> Audit;
    }


The figure above shows the core resource types in the Dyff Platform and the dependencies among them. The workflow of producing an audit proceeds from left to right.

Inference Service
-----------------

An :class:`~dyff.schema.platform.InferenceService` encapsulates the "system under test" in a containerized service that allows clients to make inferences on input data instances using the system via a remote procedure call (RPC) API. This highly generic interface allows the Dyff Platform to perform audits directly on production-ready intelligent systems, which are often complex, bespoke systems comprised of a variety of programming languages and machine learning frameworks. Solution developers can provide their solutions directly as Docker images that contain a Web server exposing an HTTP API for inference. Dyff can also create inference services backed by :ref:`models <core-resources-model>` implemented in common ML frameworks automatically.

.. _core-resources-model:

Model
-----

A :class:`~dyff.schema.platform.Model` describes the artifacts that comprise an inference model. The Dyff Platform can create inference services automatically for models built in a variety of common ML frameworks, including, of course, models distributed on the `HuggingFace Hub`_. In most cases, the model artifacts such as neural network weights simply get loaded into a "runner" container to expose the model as an inference service, so services backed by models are cheap to create.

Inference Session
-----------------

An :class:`~dyff.schema.platform.InferenceSession` is a running instance of an inference service. Multiple replicas of the service can be run in a single session to increase throughput. The Dyff Platform automatically orchestrates the computational resources required, including GPU accelerators for neural network models.

Inference sessions are used for two purposes. First, platform users can use them to perform inference interactively via the Dyff Platform API. This is useful for prototyping evaluations and for verifying that data schemas and conversions between them are all correct. Second, inference sessions are used by :ref:`Evaluations <core-resources-evaluation>`; the evaluation machinery is implemented as a "client" of the session that feeds in input data taken from a :ref:`Dataset <core-resources-dataset>`.

.. _core-resources-dataset:

Dataset
-------

A :class:`~dyff.schema.platform.Dataset` is a set of input instances on which to evaluate systems. The Dyff Platform uses the `Apache Arrow`_ format to represent datasets. The Arrow dataset format is a columnar format optimized for data science and machine learning workflows. It is mostly inter-convertible with JSON and Pandas DataFrame formats. An Arrow dataset has a static schema describing the names and types of columns. The Dyff Platform API specifies required :ref:`data schemas <data-schemas>` for datasets intended for common purposes. For example, datasets that take static images for input must store them in a column called ``"image"``, where each image is an Arrow ``struct`` with fields ``.bytes`` containing the raw image data, and ``.format`` containing the image MIME type. A dataset may define multiple *views* that adapt the dataset to support different inference tasks.

.. _core-resources-evaluation:

Evaluation
----------

An :class:`~dyff.schema.platform.Evaluation` is the process of making an inference for each instance in a dataset using a given inference service -- for example, classifying all of the images in ImageNet using a particular neural network model. Because the inference service is a generic containerized service, the Dyff Platform can easily scale up the number of replicas of the inference service to accelerate the evaluation process ("horizontal scaling").

The result of an evaluation is another Apache Arrow dataset containing the per-instance raw inference outputs. For example, for a typical ImageNet classifier, each output instance would contain thetop-:math:`k` highest-scoring label predictions in decreasing order of score. In general, we preserve as much of the full inference output as is pracical, so that any number of summary measures, including ones that had not been implemented when the evaluation was performed, can be run against the evaluation outputs without re-doing the expensive inference computations.

Report
------

A :class:`~dyff.schema.platform.Report` is the result of transforming raw inference outputs into meaningful per-instance performance statistics by applying a scoring :class:`~dyff.audit.scoring.base.Rubric` on the raw outputs. For a simple classification task, for example, the :class:`TopKAccuracy <dyff.audit.scoring.classification.TopKAccuracy>` rubric assigns a 0-1 score to each instance according to whether the correct label was among the top-:math:`k` highest-scoring predicted labels. The output of a report is another Arrow dataset, although by this point the data is typically small enough to be handled as a single in-memory table. Any number of different applicable reports can be run against a single set of evaluation outputs.

The report output is restricted to contain only those dataset features that the dataset creators have specifically identified as co-variates that are available for downstream analysis. This prevents the report from revealing the potentially sensitive contents of the input dataset.

Audit
-----

Finally, an :class:`~dyff.schema.platform.Audit` applies an :class:`~dyff.schema.platform.AuditProcedure` to summarize the results of one or more reports to produce an artifact that is suitable for inspection by humans. The goal of an audit is to assess the performance of the system under test on a set of related criteria. For example, we may be interested in whether face recognition systems show any racial bias in their performance patterns, such as by having systematically lower or higher accuracy for people with lighter or darker skin color. An audit for racial bias in face recognition would bring together performance reports for evaluations on datasets that have co-variate information about the skin tone of each face to create a summary of the strengths and weaknesses of a given system. The audit can then be run for any solution that has been evaluated on the required datasets.

On the Dyff Platform, audits are written as Jupyter notebooks that make calls to the :py:mod:`Dyff API <dyff.client>` and generate output documents consisting of formatted text, figures, tables, and other multi-media content. The Dyff Platform, using Jupyter tools, renders the output documents as HTML pages and serves them on the Web.

.. Links
.. _Apache Arrow: https://arrow.apache.org/
.. _HuggingFace Hub: https://huggingface.co/
