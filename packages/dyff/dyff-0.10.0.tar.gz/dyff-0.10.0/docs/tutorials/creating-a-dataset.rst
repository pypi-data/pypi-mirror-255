Creating a Dataset
==================

This tutorial walks through the creation of an evaluation dataset that tests
systems for `named entity recognition
<https://en.wikipedia.org/wiki/Named-entity_recognition>`_ on their ability to
recognize entities when their names are not capitalized --- which, in many
languages, is a strong cue that a word refers to an entity. You will convert a
publicly available NER dataset to the format needed by the Dyff Platform while
altering it so that the entity names are all lower-case.


Primer on Apache Arrow datasets
-------------------------------

The Dyff Platform uses the Apache Arrow format to store and manipulate datasets.
An Arrow dataset is a collection of data files with the same schema that can be
manipulated as a single entity. A simple dataset might be structured like this
on disk:

::

    dataset
    ├── part-0.parquet
    ├── part-1.parquet
    └── part-2.parquet

The top-level directory is treated as the location of the dataset. This dataset
can be opened like this:

.. code-block:: python

    import pyarrow.dataset
    ds = pyarrow.dataset.dataset("dataset", format="parquet")

The format is ``"parquet"`` because the individual files are Apache Parquet
files. The Dyff Platform uses the Parquet format for all datasets.

Schemas
~~~~~~~

The schema describes the fields in the dataset. Arrow datasets are similar to
JSON objects: they consist of nested dictionaries and lists along with various
primitive data types. The most important container types are:

    ``pyarrow.list_()`` :
        A list with a static item type, either fixed or variable length.

    ``pyarrow.struct()`` :
        A key-value mapping with a fixed field order and static field types.

Partitions
~~~~~~~~~~

Arrow datasets can represent the values of a column either in the component
files or in the directory structure of the dataset. For example, a dataset that
contains text in multiple languages might be structured like this:

::

    partitioned-dataset
    ├── language=en
    │   ├── part-0.parquet
    │   └── part-1.parquet
    ├── language=es
    │   ├── part-0.parquet
    │   └── part-1.parquet
    └── language=fr
        ├── part-0.parquet
        └── part-1.parquet

This dataset uses a convention called "hive partitioning" wherein the
subdirectories are named like ``column=value``. The Dyff Platform uses
hive-style partitioning for all partitioned datasets.

The dataset is still read as a single entity:

.. code-block:: python

    import pyarrow.dataset
    ds = pyarrow.dataset.dataset("dataset", format="parquet", partitioning="hive")

We have a loose convention of using partitions to represent features for which
one might want to perform a stratified data analysis. A ``language`` feature is
a good example: one might want to test a system to make sure it performs
similarly on all of the input languages it can accept. Data "projections" onto
partitioned features (i.e., loading only the ``language=en`` data) are very
efficient. You can also use partitions to break up a very large dataset to make
it easier to manipulate. You should *not* partition on a feature if doing so
will result in a large number of small partitions, as data loading is most
efficient for intermediate-sized individual files.

The dataset has a separate *partition schema* to describe which features should
be represented as partitions. The partition schema must be a *subset* of the
full schema.

Reading
~~~~~~~

Arrow datasets are designed for the case where the dataset is too large to fit
in memory. Generally, you will read the dataset in batches, one at a time,
convert each batch to an appropriate in-memory format, and then process the
items in the batch. The ``Dataset.to_batches()`` method returns an iterator that
yields ``RecordBatch`` instances. The ``RecordBatch`` type has methods to
convert the batch to various formats, including: a pandas DataFrame
(``.to_pandas()``), a Python dict-of-lists (``.to_pydict()``), or a Python
list-of-dicts (``.to_pylist()``). The ``pylist`` format is the easiest to deal
with when manipulating individual instances, but the ``pydict`` format and,
especially, the ``pandas`` format may be significantly faster when applying
batch-wise operations.

Example:

.. Note: If we don't indent the second loop body by double the usual amount,
..       it doesn't get properly indented in the output.
.. code-block:: python

    import pyarrow.dataset
    ds = pyarrow.dataset.dataset("/path/to/dataset", format="parquet", partitioning="hive")
    for batch in ds.to_batches():
        for row in batch.to_pylist():
                language = row["language"] # Primitive field
                first_tag = row["tags"][0] # List field
                image_bytes = row["image"]["bytes"] # Struct field
                ...

Writing
~~~~~~~

Arrow datasets are read-only; writing a dataset always entails creating new
files, possibly replacing existing files. There are *no guarantees* about the
order of instances in the written dataset or about which file an instance
ultimately gets written to. It's therefore essential that every instance has a
stable, unique identifier. By convention, Dyff Platform datasets use a special
field called ``_index_`` for this purpose.

To write a dataset, you need to create a *generator function* that yields
``RecordBatch`` instances. The easiest way to create a ``RecordBatch`` is to
represent each instance as a (possibly nested) Python dictionary and then
construct a ``RecordBatch`` from a list of instances. Arrow calls this the
``pylist`` format.

Example:

.. code-block:: python

    import pyarrow
    import pyarrow.dataset

    schema = pyarrow.Schema([
        pyarrow.field("_index_", pyarrow.int64()),
        pyarrow.field("word", pyarrow.string()),
        pyarrow.field("word_features", pyarrow.struct([
                pyarrow.field("length", pyarrow.int64()),
                pyarrow.field("capitalized", pyarrow.bool_()),
        ])
    ])

    def batches(instances, schema: pyarrow.Schema, batch_size: int=4):
        batch = []
        for instance in instances:
                batch.append(instance)
                if len(batch) == batch_size:
                        yield pyarrow.RecordBatch.from_pylist(batch, schema=schema)
                        batch = []
        if batch: # Final (incomplete) batch
                yield pyarrow.RecordBatch.from_pylist(batch, schema=schema)

    def generator():
        words = "This example has been brought to you by the number 11".split()
        batch = []
        for i, word in enumerate(words):
                # Use 'pylist' format: List of dicts
                # Types must be coerce-able to the corresponding schema types
                yield {
                        "_index_": i,
                        "word": word,
                        "word_features": {
                                "length": len(word),
                                "capitalized": word[0].isupper(),
                        }
                }

    pyarrow.dataset.write_dataset(
        batches(generator(), schema), "/path/to/dataset", format="parquet", schema=schema)

Note how we used the utility function ``batches()`` to collect the individual
instances yielded by ``generator()`` into ``RecordBatch`` objects. You should
always provide an explicit schema to the ``RecordBatch`` constructor functions
(such as ``.from_pylist()``). If you do not, Arrow will try to infer the schema,
and it sometimes gets it wrong. You can also create a ``RecordBatch`` from a
pandas ``DataFrame``, or from a Python data structure in ``pydict`` format (a
dictionary where each item is a batch of data for one column).

Obtain the source dataset
-------------------------

Now let's return to our tutorial example. We will adapt one of the most-used NER
datasets, CoNLL2003, to create our custom dataset. We'll use the `version hosted
on HuggingFace <https://huggingface.co/datasets/conll2003>`_. The standard way
of fetching HuggingFace datasets puts them in the HuggingFace cache, which is
somewhat opaque. Instead, we'll use some less-known API functions to fetch the
files into a directory of our choice:

.. code-block:: python

    import datasets
    builder = datasets.load_dataset_builder("conll2003")
    builder.download_and_prepare("conll2003", file_format="parquet")
    dataset_info = datasets.DatasetInfo.from_directory("conll2003")

Conveniently for us, HuggingFace also uses the Arrow Datasets format. Let's open
the dataset and examine its schema:

.. code-block:: python

    import pyarrow.dataset
    ds = pyarrow.dataset.dataset("conll2003", format="parquet")
    print(ds)

.. code-block:: text

    id: string
    tokens: list<item: string>
      child 0, item: string
    pos_tags: list<item: int64>
      child 0, item: int64
    chunk_tags: list<item: int64>
      child 0, item: int64
    ner_tags: list<item: int64>
      child 0, item: int64
    -- schema metadata --
    huggingface: '{"info": {"features": {"id": {"dtype": "string", "_type": "' + 930

We need to read the `dataset documentation
<https://huggingface.co/datasets/conll2003>`_ to find out what the fields
represent. In this case, the ones that are relevant to our task are:

    tokens:
        A list of strings representing the tokenized input text

    ner_tags:
        The ground-truth tags for **N**\ amed **E**\ ntity **R**\ ecognition, in
        "IOB2" format.

Reformatting the dataset
------------------------

We will make several different changes to this data as we construct our new
dataset:

    1. First of all, to achieve our goal of testing robustness to lower-case
       entity names, we need to identify all of the named entities and convert
       the corresponding tokens to lower-case.

    2. In addition, we want to "de-tokenize" the data, so that it looks more
       like what a deployed system would actually see from a user. Suppose, for
       example, that the NER system is part of a natural language
       question-answering service. Such a system needs to be tested on
       natural-language input like, ``"Who's buried in Grant's tomb?"``, not
       tokenized input like, ``["Who", "'s", "buried", "in", "Grant", "'s",
       "tomb", "?"]``.

    3. If we're de-tokenizing the input, we also need to de-tokenize the
       ground-truth tags. For example, given tokens, ``["Ulysses", "S", ".",
       "Grant"]`` and corresponding tags, ``["B-PER", "I-PER", "I-PER",
       "I-PER"]``, we need to emit the text, ``"Ulysses S. Grant"`` and the
       single tag, ``(<start>, <end>, "PER")``, where ``<start>`` and ``<end>``
       identify the characters in the text that should have the tag ``"PER"``
       ("person").

    4. Instead of having separate datasets for the ``train``, ``validation``,
       and ``test`` splits, we want to have a single dataset with a column
       called ``split`` that identifies which split the instance came from.

    5. Finally, we need to add the special field ``_index_``, which assigns a
       unique sequential integer index to each instance in the dataset.


Adding the ``split`` and ``_index_`` columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll tackle the last two tasks first. The HuggingFace convention is to
represent dataset splits with files named like ``conll2003-train.parquet`` and
``conll2003-test.parquet``. Instead of keeping the splits separate, we will
merge them all into a single dataset with a new ``split`` column to identify the
split.

.. code-block:: python

    from pathlib import Path

    def dataset_generator(dataset_info, convert_fn):
        next_index = 0
        dataset_files = list(Path("conll2003").glob("*.parquet"))
        for split in dataset_info.splits.values():
                # Open all of the files from this split as a single dataset
                pattern = f"/{split.dataset_name}-{split.name}.*\\.parquet$"
                split_files = [file for file in dataset_files if re.search(pattern, str(file))]
                dataset = pyarrow.dataset.dataset(split_files, format="parquet")
                # Generate individual instances from the current split
                for batch in dataset.to_batches():
                        for item in batch.to_pylist():
                                # We'll implement the rest of the conversion logic in 'convert_fn'
                                converted = convert_fn(item)
                                converted["_index_"] = next_index
                                converted["split"] = split.name
                                next_index += 1
                                yield converted

The ``dataset_generator()`` function iterates through all of the splits in the
dataset, converts each instance using a supplied conversion function, adds the
``split`` and ``_index_`` fields, and yields the converted instance. Notice that
``next_index`` is not reset to 0 between splits, since we want every instance to
have its own unique ``_index_``.

Converting names to lower-case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rest of our dataset conversion will happen in a separate function, which we
will pass to ``dataset_generator()`` in the ``convert_fn`` parameter. First, we
convert tokens corresponding to named entities to lower-case:

.. code-block:: python

    def convert(dataset_info, row):
        # Mapping from integer tag index to meaningful tag name
        ner_tag_names = dataset_info.features["ner_tags"].feature.names
        tokens = row["tokens"]
        tags = [ner_tag_names[tag] for tag in row["ner_tags"]]
        lowercased_tokens = []
        for token, tag in zip(tokens, tags):
                if tag != "O": # It's a named entity
                        lowercased_tokens.append(token.lower())
                else:
                        lowercased_tokens.append(token)
        ...

In the IOB2 format, the ``O`` tag means any token that is *not* part of a named
entity. The HuggingFace dataset represents tags as integer indices. To determine
the corresponding IOB2 tag, we consult the HuggingFace ``DatasetInfo`` object to
get the mapping from indices to tag names.

So far, our ``convert()`` function is performing mappings like the following:

.. code-block:: text

    in : ['The', 'European', 'Commission', 'said', 'on', 'Thursday', 'it', 'disagreed', 'with', 'German', 'advice', ...]
    out: ['The', 'european', 'commission', 'said', 'on', 'Thursday', 'it', 'disagreed', 'with', 'german', 'advice', ...]

Notice how ``European Commission`` and ``German`` have been lower-cased, since
they fall into NER categories ``ORG`` (organization) and ``MISC``, respectively.
The word ``The`` at the start of the sentence retains its capitalization, as
does ``Thursday``.

De-tokenizing the text
~~~~~~~~~~~~~~~~~~~~~~

We could naïvely de-tokenize the text with, for example, ``" ".join(tokens)``,
but this will result in text like ``Germany 's representative``, because
``Germany`` and ``'s`` are two separate tokens. We can do a bit better by using
a de-tokenizer that is aware of English grammar rules. Specifically, we'll use
the ``TreebankWordDetokenizer`` from the ``nltk`` package. Install this package
with:

.. code-block:: bash

    $ python -m pip install nltk

Now we can add a de-tokenization step to our conversion function:

.. code-block:: python
    :emphasize-lines: 1,15

    from nltk.tokenize.treebank import TreebankWordDetokenizer

    def convert(dataset_info, row):
        # Mapping from integer tag index to meaningful tag name
        ner_tag_names = dataset_info.features["ner_tags"].feature.names
        tokens = row["tokens"]
        tags = [ner_tag_names[tag] for tag in row["ner_tags"]]
        lowercased_tokens = []
        for token, tag in zip(tokens, tags):
                if tag != "O": # It's a named entity
                        lowercased_tokens.append(token.lower())
                else:
                        lowercased_tokens.append(token)

        text = TreebankWordDetokenizer().detokenize(lowercased_tokens)

The results still won't be perfect. For example, because the CoNLL2003 dataset
splits the text up into one instance per sentence, there is no way to tell if a
quotation mark is an open- or a close-quote if the quoted text spans two
sentences (at least, not without first "de-sentencifying" the text). In general,
tokenization is a lossy operation, and it would be better to work directly with
the source text rather than the tokenized version.

Converting token tags to "span" tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have de-tokenized text, we need to convert the token-level tags to
"spans". A :class:`~dyff.audit.schemas.text.TaggedSpan` associates a
``tag`` with an index range ``[start, end)`` in the text. We'll use the utility
function :func:`~dyff.audit.data.text.token_tags_to_spans` to compute
the spans:

.. code-block:: python
    :emphasize-lines: 1,17

    from dyff.audit.data.text import token_tags_to_spans
    from nltk.tokenize.treebank import TreebankWordDetokenizer

    def convert(dataset_info, row):
        # Mapping from integer tag index to meaningful tag name
        ner_tag_names = dataset_info.features["ner_tags"].feature.names
        tokens = row["tokens"]
        tags = [ner_tag_names[tag] for tag in row["ner_tags"]]
        lowercased_tokens = []
        for token, tag in zip(tokens, tags):
                if tag != "O": # It's a named entity
                        lowercased_tokens.append(token.lower())
                else:
                        lowercased_tokens.append(token)

        text = TreebankWordDetokenizer().detokenize(lowercased_tokens)
        spans = token_tags_to_spans(text, lowercased_tokens, tags)

You can use the function :func:`~dyff.audit.data.text.visualize_spans`
to check that the result looks correct. Here is a possible visualization output
for one of the instances in our dataset::

    germany's representative to the european union's veterinary committee werner zwi
    LLLLLLL.........................OOOOOOOOOOOOOO........................PPPPPPPPPP
    ngmann said on Wednesday consumers should buy sheepmeat from countries other tha
    PPPPPP..........................................................................
    n britain until the scientific advice was clearer.
    ..LLLLLLL.........................................

Here the letters correspond to the first letter of the tag (e.g., ``PER -> P``).
Notice how the whitespace connecting multi-word entities is included in the
corresponding spans.

Return a schema-compatible Python representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, we finish up the ``convert()`` function by returning a Python
datastructure that is compatible with the two relevant schemas --- :class:`Text
<dyff.audit.schemas.text.Text>` and :class:`TaggedSpans
<dyff.audit.schemas.text.TaggedSpans>`:

.. code-block:: python
    :emphasize-lines: 18-21

    from dyff.audit.data.text import token_tags_to_spans
    from nltk.tokenize.treebank import TreebankWordDetokenizer

    def convert(dataset_info, row):
        # Mapping from integer tag index to meaningful tag name
        ner_tag_names = dataset_info.features["ner_tags"].feature.names
        tokens = row["tokens"]
        tags = [ner_tag_names[tag] for tag in row["ner_tags"]]
        lowercased_tokens = []
        for token, tag in zip(tokens, tags):
                if tag != "O": # It's a named entity
                        lowercased_tokens.append(token.lower())
                else:
                        lowercased_tokens.append(token)

        text = TreebankWordDetokenizer().detokenize(lowercased_tokens)
        spans = token_tags_to_spans(text, lowercased_tokens, tags)
        return {
                "text": text,
                "spans": [span.dict() for span in spans]
        }

Write the dataset to the filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To write the dataset to the filesystem, we need an Arrow schema for the data.
You can define a schema directly using the ``pyarrow.schema()`` function. Or,
you can define the schema using ``pydantic`` models and then use the utility
function ``dyff.schema.arrow.arrow_schema()`` to convert the pydantic model
to an Arrow schema. The pydantic way is especially convenient because the
``dyff.schema`` package defines many useful data schemas that can be composed
to create datasets for common tasks.

In the following example, we use some of the predefined ``dyff.schema`` types,
along with a custom pydantic model we define for this dataset, to create the
output schema. Pydantic models can be composed using inheritance; this is the
equivalent of creating a new model containing all of the fields from the
superclass models. Note that the inherited models get added in *reverse order*.
The order of the top-level fields in the Arrow schema doesn't actually matter,
but we prefer the order ``_index_ ... strata fields ... data fields`` for
aesthetic reasons.

.. code-block:: python

    from dyff.schema.arrow import arrow_schema, batches
    from dyff.schema.dataset import Item
    from dyff.schema.pydantic import DyffSchemaBaseModel
    from dyff.schema.text import TaggedSpans, Text

    generator = dataset_generator(dataset_info, functools.partial(convert, dataset_info))

    class SplitSchema(DyffSchemaBaseModel):
        split: str

    # Since Item is last, the _index_ field will come first in OutputSchema
    class OutputSchema(TaggedSpans, Text, SplitSchema, Item):
        pass

    feature_schema = arrow_schema(OutputSchema)
    # Partition the data on the 'split' field
    partition_schema = arrow_schema(SplitSchema)
    partitioning = pyarrow.dataset.partitioning(partition_schema, flavor="hive")
    # Notice that we specify the schema explicitly when creating the 'batches()'
    # generator. PyArrow sometimes infers the wrong field order for nested
    # pyarrow.struct() types if we don't specify it explicitly.
    pyarrow.dataset.write_dataset(
        batches(generator, schema=feature_schema, batch_size=32),
        "conll2003-lowercase",
        format="parquet",
        schema=feature_schema,
        partitioning=partitioning,
        existing_data_behavior="overwrite_or_ignore",
    )


Upload the dataset to the Dyff Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have an Arrow dataset, we can upload it to the Dyff Platform. This
requires two steps. In the first step, we create a new Dataset entity in the
Dyff Platform. The Dataset entity includes a list of all of the "artifacts" that
comprise the dataset along with message digests (hashes) for each artifact. For
Arrow datasets, the artifacts are the ``.parquet`` files that hold the data.
The ``create_arrow_dataset()`` function automatically discovers these files and
calculates digests for them.

In the second step, we upload the dataset artifacts to the platform. This step
will fail if dataset has changed since the dataset record was created, since
the digests of the component files won't match.

.. code-block:: python

    from dyff.client.client import Client

    dyffapi = Client(api_key=API_KEY)

    dataset = dyffapi.datasets.create_arrow_dataset(
        "conll2003-lowercase", account=ACCOUNT, name="conll2003-lowercase"
    )
    print(f"created dataset:\n{dataset}")

    # If you created the dataset but couldn't complete the upload, you can
    # fetch the dataset record and re-try the upload:
    # dataset = dyffapi.datasets.get(<dataset.id>)

    dyffapi.datasets.upload_arrow_dataset(dataset, "conll2003-lowercase")

Behind the scenes, these high-level ``_arrow_dataset()`` functions are calling
the actual API endpoints via ``dyffapi.datasets.create()``,
``dyffapi.datasets.upload()``, and ``dyffapi.datasets.finalize()``. You can use
these low-level functions directly if your use-case requires it.

You can confirm that the datasets is ready by checking its status:

.. code-block:: python

    dyffapi.datasets.get(dataset.id).status

The status will be ``Ready`` if the upload completed successfully.


Full Example
------------

.. code-block:: python

    import functools
    import re
    from pathlib import Path

    import datasets
    import pyarrow
    import pyarrow.dataset
    from nltk.tokenize.treebank import TreebankWordDetokenizer

    from dyff.audit.data.text import token_tags_to_spans
    from dyff.client import Client
    from dyff.schema.arrow import arrow_schema, batches
    from dyff.schema.dataset import Item
    from dyff.schema.pydantic import DyffSchemaBaseModel
    from dyff.schema.text import Text, TaggedSpans


    ACCOUNT = "<YOUR_ACCOUNT>"
    API_KEY = "<YOUR_API_KEY>"


    class SplitSchema(DyffSchemaBaseModel):
        split: str


    class OutputSchema(TaggedSpans, Text, SplitSchema, Item):
        pass


    def dataset_generator(dataset_info, convert_fn):
        next_index = 0
        dataset_files = list(Path("conll2003").glob("*.parquet"))
        for split in dataset_info.splits.values():
            # Open all of the files from this split as a single dataset
            pattern = f"/{split.dataset_name}-{split.name}.*\\.parquet$"
            split_files = [file for file in dataset_files if re.search(pattern, str(file))]
            dataset = pyarrow.dataset.dataset(split_files, format="parquet")
            # Generate individual instances from the current split
            for batch in dataset.to_batches():
                for item in batch.to_pylist():
                    # We'll implement the rest of the conversion logic in 'convert_fn'
                    converted = convert_fn(item)
                    converted["_index_"] = next_index
                    converted["split"] = split.name
                    next_index += 1
                    yield converted


    def convert(dataset_info, row):
        ner_tag_names = dataset_info.features["ner_tags"].feature.names
        tokens = row["tokens"]
        tags = [ner_tag_names[tag] for tag in row["ner_tags"]]
        lowercased_tokens = []
        for token, tag in zip(tokens, tags):
            if tag != "O":  # It's a named entity
                lowercased_tokens.append(token.lower())
            else:
                lowercased_tokens.append(token)
        text = TreebankWordDetokenizer().detokenize(lowercased_tokens)
        spans = token_tags_to_spans(text, lowercased_tokens, tags)
        return {"text": text, "spans": [span.dict() for span in spans]}


    # Fetch the dataset from HuggingFace
    builder = datasets.load_dataset_builder("conll2003")
    builder.download_and_prepare("conll2003", file_format="parquet")
    dataset_info = datasets.DatasetInfo.from_directory("conll2003")
    ds = pyarrow.dataset.dataset("conll2003", format="parquet", partitioning="hive")

    # Create a new dataset by converting the input dataset
    feature_schema = arrow_schema(OutputSchema)
    partition_schema = arrow_schema(SplitSchema)
    partitioning = pyarrow.dataset.partitioning(partition_schema, flavor="hive")
    generator = dataset_generator(dataset_info, functools.partial(convert, dataset_info))
    pyarrow.dataset.write_dataset(
        batches(generator, schema=feature_schema, batch_size=32),
        "conll2003-lowercase",
        format="parquet",
        schema=feature_schema,
        partitioning=partitioning,
        existing_data_behavior="overwrite_or_ignore",
    )

    # Upload the dataset
    dyffapi = Client(api_key=API_KEY)
    dataset = dyffapi.datasets.create_arrow_dataset(
        "conll2003-lowercase", account=ACCOUNT, name="conll2003-lowercase"
    )
    # If you created the dataset but couldn't complete the upload, you can
    # fetch the dataset record and re-try the upload:
    # dataset = dyffapi.datasets.get(<dataset.id>)
    dyffapi.datasets.upload_arrow_dataset(dataset, "conll2003-lowercase")
