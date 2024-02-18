.. _data-schemas:

Data Schemas
============

The Dyff Platform requires that formal schemas are defined for all data involved in the audit process. This includes inputs to the model and additional covariates associated with the inputs, the raw inference outputs from the model, and the post-processed and "scored" model outputs that are ready for public consumption.

The main function of formal schemas is to ensure forward-compatibility of existing resources in the platform with new datasets, ML models, and audits. We can't be writing a new interface adapter for every ``Dataset x Model x Report`` combination.

The input data schemas are associated with :class:`~dyff.schema.platform.Dataset` resources. Model output schemas are associated with :class:`~dyff.schema.platform.InferenceService` resources and, by extension, resources such as :class:`~dyff.schema.platform.InferenceSession` and :class:`~dyff.schema.platform.Evaluation` that consume inference services. Schemas for the post-processed outputs are associated with :class:`~dyff.schema.platform.Report` resources.

Native data formats and Schema Adapters
---------------------------------------

One of the design goals of the Dyff Platform is to be able to evaluate ML systems in their "deployable" form, meaning that the code being evaluated is the same as the code that will actually be used in a product, or at least as close as possible. So, Dyff allows model inputs and outputs to have essentially any JSON-like structure. Because there is no accepted standard for ML system APIs, models created by different organizations tend to have incompatible interfaces.

To bridge this gap, it is often necessary to convert data from one schema to another, often multiple times in the course of running the full audit workflow. The code that performs these transformations *is part of the test specification*; we are not evaluating the model on dataset ``D``, we are evaluating it on dataset ``D`` *with transformation* ``T`` *applied*. So, the necessary adapters must be specified as part of the corresponding resource, so that the whole combination of components and adapters has a unique ID and we can reproduce the entire end-to-end pipeline.

Usually, **you do not need to alter your existing datasets and models** to conform to Dyff's schemas. Instead, you will specify :py:mod:`schema adapters <dyff.schema.adapters>` to transform the inputs and outputs, and the Dyff Platform will store those adapter specifications in the uniquely-identified specification of the inference service. All of these adapters take their configuration as a JSON object, so that schema adapter pipelines can be specified easily as part of a resource specification.

Schema conventions
------------------

Our guiding principles for data schema design are:

    1. Schemas should be composable
    2. Flat is better than nested
    3. Schemas should describe semantics as well as type

This results in data that is easy to store and manipulate with common tools like Arrow and Pandas, and that is easy to reuse because it is clear what the data represents.

Semantic field names
~~~~~~~~~~~~~~~~~~~~

To achieve composability, we define standard names for top-level fields with associated task semantics. For example, for the task of "text generation", we expect that both the inputs and outputs of the model contain a field called ``"text"``, which, by convention, contains text. If the task is "text classification", the output would instead have a field called ``"label"``.

For a limited number of ubiquitous kinds of fields with very general semantics, we use non-namespaced "reserved" names like "text" and "label". To allow extensibility, we define more task-specific fields within namespaces. For example, the output for a text tagging task might use the field ``text.dyff.io/taggedspan``. Field names prefixed with ``dyff.io/`` or ``subdomain.dyff.io/`` are reserved for the Dyff platform.

Input and output schemas
~~~~~~~~~~~~~~~~~~~~~~~~

Inference services take a single object input and return a *list* of objects. Making the output a list accommodates the common practice of returning multiple possible answers, often in descending order of preference.

If the input schema of an inference service is specified by name as :class:`text.Text <dyff.schema.text.Text>`, then the service must accept JSON requests that look like::

    {"text": "It was the best of times, "}

If the output schema is also specified by name as :class:`text.Text <dyff.schema.text.Text>`, then the service must return JSON responses that look like::

    [{"text": "it was the worst of times"}, {"text": "it was the blurst of times"}]

In both cases, we would express that expectation by specifying that both input and output must conform to the **named schema** :class:`text.Text <dyff.schema.text.Text>`.

How schemas are specified
-------------------------

The Dyff Platform uses `pydantic models <https://docs.pydantic.dev/1.10/>`_ to formalize all of its data schemas. From these pydantic schemas, we generate Arrow schemas for data in persistent storage, and JSON schemas for the specification of remote procedure call (RPC) interfaces. These three schema types are inter-convertible if we avoid a few specific features that don't exist in all three.

When schemas are required in Dyff APIs, they are specified with the :class:`~dyff.schema.platform.DataSchema` type, which contains fields for all three kinds of schema. The full :class:`~dyff.schema.platform.DataSchema` can be populated from just a pydantic model type.

You can specify your own schema with a mix of **named schemas** defined by the platform and new pydantic model types that you define yourself. The top-level schema is the **product** of a list of component schemas. Here, **product type** just means a schema that contains all the fields in all of its components. This is why top-level field names must be unique, so that creating a product schema doesn't result in name collisions.

Required fields
---------------

Field names that begin and end with an underscore (e.g., ``_index_``) and field names prefixed with ``dyff.io`` or a sub-domain thereof (e.g., ``subdomain.dyff.io/fieldname``) are reserved for use by the Dyff Platform.

When you specify input and output schemas for resources like :class:`~dyff.schema.platform.InferenceService`, the following special fields are mandatory in the input and/or output schema, as noted:

    ``_index_ : int64`` [Required in input and output]
        The ``_index_`` field uniquely identifies a single input item within its containing dataset. **Every input item must have an** ``_index_`` **field that is unique within its dataset. Every output item has an** ``_index_`` **field that matches it to the corresponding input item.**

    ``_replication_ : string`` [Required in output]
        The ``_replication_`` field identifies which replication of an evaluation the output item belongs to. It is a UUIDv5 identifier, where the "namespace" is the ID of the evaluation resource and the "name" is the sequential integer index of the replication (i.e., ``0``, ``1``, ...).

    ``responses : list(struct(response type))`` [Required in output]
        The ``responses`` field contains the list of responses from the inference service for a corresponding input. It is always a list, even if the service only returns a single response.

        The elements of the ``responses`` list must contain the following fields:

            ``_response_index_ : int64`` [Required in output]
                The ``_response_index_`` field uniquely identifies each response to a given input item. The ``responses`` list may contain more than one item with the same ``_response_index_`` value. For example, text span tagging tasks like Named Entity Recognition may output zero or more predicted entities for a single input text.

Putting this all together, we can see that each combination of ``(_index_, _replication_, _response_index_)`` identifies one set of system inferences for the single input item identified by ``_index_``.

**You are responsible for ensuring all required fields are in the schemas you specify**. This is a design choice that we have made to ensure that data records are self-describing. To make this easier, you can use :py:meth:`DataSchema.make_input_schema() <dyff.schema.platform.DataSchema.make_input_schema>` and :py:meth:`DataSchema.make_output_schema() <dyff.schema.platform.DataSchema.make_output_schema>`, which add the required fields to another schema that you provide and then populate a full :class:`~dyff.schema.platform.DataSchema` instance using the result. For example, if your service outputs both a piece of text and a classification label, you can create the spec for its output schema like this:

.. code-block:: python

    >>> from dyff.schema import arrow
    >>> from dyff.schema.platform import DataSchema, DyffDataSchema
    >>> dyff_schema = DyffDataSchema(components=["classification.Label", "text.Text"])
    >>> full_schema = DataSchema.make_output_schema(dyff_schema)
    >>> print(arrow.decode_schema(full_schema.arrowSchema))
    _index_: int64
      -- field metadata --
      __doc__: 'The index of the item in the dataset'
    _replication_: string
      -- field metadata --
      __doc__: 'ID of the replication the response belongs to.'
    responses: list<item: struct<_response_index_: int64, text: string, label: string>>
      child 0, item: struct<_response_index_: int64, text: string, label: string>
          child 0, _response_index_: int64
          -- field metadata --
          __doc__: 'The index of the response among responses to the correspo' + 13
          child 1, text: string
          -- field metadata --
          __doc__: 'Text data'
          child 2, label: string
          -- field metadata --
          __doc__: 'The discrete label of the item'
      -- field metadata --
      __doc__: 'Inference responses'

Notice how the generated Arrow schema includes the required fields ``_index_``, ``_replication_``, and ``responses``, and the items in ``responses`` include a ``_response_index_`` field. You can also provide a type that derives from :class:`~dyff.schema.pydantic.DyffSchemaBaseModel` as the argument to :py:meth:`DataSchema.make_input_schema() <dyff.schema.platform.DataSchema.make_input_schema>` and :py:meth:`DataSchema.make_output_schema() <dyff.schema.platform.DataSchema.make_output_schema>`, which is useful if you need to include data that doesn't fit any of the named schemas.

Dataset schemas
---------------

The first of two places where we enforce a data schema is on the input items to an :class:`~dyff.schema.platform.Dataset`. These inputs come from an input dataset. Dataset creators are responsible for specifying two kinds of schemas. First, they must define the *native schema* of the data. This can be any schema that is representible as an Arrow dataset. Second, they *may* define any number of *data views* on the dataset. These are transformations of the data to fit one of the defined *task schemas* that inference services expect as input.

This separation of the dataset native schema and multiple views of the data allows an existing dataset to be adapted for use in new tasks that the dataset creators may not have considered when they created the dataset. In many cases, though, a dataset will be suitable only for a single task, and it may not require specifying any views because it is already in the expected format.

Since datasets are used as inputs for inference, each row of the dataset must have a unique ``_index_`` field. You must specify this field as part of the dataset schema.

Report schemas
--------------

The second of the two places we enforce a data schema is on the input items to :class:`Reports <dyff.schema.platform.Report>`. These inputs come from the outputs of running an inference service on an input dataset. We assume that inference services generate a *list* of responses.

As with datasets, creators of inference services are responsible for specifying two kinds of schemas. First, they define the *native schema* of the service outputs, which, again, can be any schema representable in Arrow. Second, they may define any number of *output views*, which transform the items in the ``responses`` list to the formats expected by different :class:`Reports <dyff.schema.platform.Report>` implementations.

Each row of data that is input to a :class:`Reports <dyff.schema.platform.Report>` must have an ``_index_`` field that matches the ``_index_`` of the corresponding input item, a ``_replication_`` field that distinguishes multiple responses to the same input, and a ``responses`` field containing a list of inference responses. Each item in ``responses`` must have a ``_response_index_`` field that identifies which inference response it is a part of. You must specify these special fields as part of the schema for output data, but their values will be populated automatically when running an evaluation.

InferenceService schema adapters
--------------------------------

An inference service is the "runnable" form of a model that exposes an HTTP interface for making inference requests. An inference service is a "view" of a model that allows it to perform a single task; there may be any number of inference services backed by the same model. When creating an :class:`~dyff.schema.platform.InferenceService` resource, you must specify how to convert the input data from the well-known task input schema to whatever format the underlying model requires, and how to convert the model's output to the well-known task output schema.

In many cases these transformations are fairly trivial. For example, the model might expect the input field to be called ``"prompt"`` instead of ``"text"``, so the input adapter just has to re-name that field. The :class:`~dyff.schema.adapters.TransformJSON` adapter is useful for this purpose. This adapter can also be used to add literal fields, which is useful when the model takes additional arguments that modify its behavior (such as sampling parameters). This way, the inference service spec also fully specifies which non-default model parameter settings that particular instantiation of the service uses, which makes uses of the inference service fully reproducible.

For the output schemas, it is often necessary to transform a "column-oriented" schema to a "row-oriented" schema. For example, the service might return responses like::

    {"text": ["response A", "response B"]}

that need to be transformed to::

    [{"text": "response A"}, {"text": "response B"}]

The :class:`~dyff.schema.adapters.ExplodeCollections` adapter is useful for this purpose. This transformation can convert a list to a set of rows while optionally also adding one or more index fields that can be used to sort the responses to an input in different ways. The :class:`~dyff.schema.adapters.FlattenHierarchy` adapter can be used to flatten nested structures into top-level fields.
