# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import functools
import re
from pathlib import Path

import datasets
import pyarrow
import pyarrow.dataset
from nltk.tokenize.treebank import TreebankWordDetokenizer

from dyff.audit.data.text import token_tags_to_spans
from dyff.client import Client
from dyff.schema.base import DyffSchemaBaseModel
from dyff.schema.dataset import Item
from dyff.schema.dataset.arrow import arrow_schema, batches
from dyff.schema.dataset.text import TaggedSpans, Text

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
