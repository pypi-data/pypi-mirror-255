# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from typing import Dict, List, Union, api

import datasets
import gcsfs
import pyarrow
from absl import logging

from ...core.config import config
from .. import storage
from . import arrowtypes, io
from . import text as text_data

DatasetType = Union[
    datasets.Dataset,
    datasets.IterableDataset,
    datasets.DatasetDict,
    datasets.IterableDatasetDict,
]


def fetch(spec: api.DataSource):
    """Fetch a Huggingface dataset into storage."""
    if spec.sourceKind != api.DataSources.huggingface:
        raise ValueError(f"requires spec.sourceKind = {api.DataSources.huggingface}")
    prefix = "https://huggingface.co/datasets/"
    if spec.source.startswith(prefix):
        dataset = spec.source[len(prefix) :]
    else:
        raise ValueError(
            "expected spec.source like 'https://huggingface.co/datasets/<dataset>'"
        )
    fs = gcsfs.GCSFileSystem()
    output_dir = storage.paths.datasource_root(spec.id)
    builder = datasets.load_dataset_builder(dataset)
    builder.download_and_prepare(
        output_dir, storage_options=fs.storage_options, file_format="parquet"
    )


def get_dataset_info(
    datasource_id: api.DataSource | api.EntityKey | str,
) -> datasets.DatasetInfo:
    if isinstance(datasource_id, api.DataSource):
        datasource_id = datasource_id.key
    elif not isinstance(datasource_id, api.EntityKey):
        datasource_id = api.EntityKey.from_str(datasource_id)
    path = storage.paths.datasource_root(datasource_id)
    fs = gcsfs.GCSFileSystem()
    return datasets.DatasetInfo.from_directory(path, storage_options=fs.storage_options)


class TextSpans:
    """Text data converter that augments tokens and token-level tags with
    detokenized text and span-level tags.
    """

    def __init__(self, *, tag_fields: List[str], span_fields: Dict[str, str]):
        """
        Parameters:
          tag_fields: The token-level tag fields to preserve
          span_fields: The token-level tag fields for which to generate
            corresponding span-level tags. The key is the token-level tag field
            name and the value is the name to assign to the generated span-level
            tag field.
        """
        self.tag_fields = tag_fields
        self.span_fields = span_fields
        self._all_fields = set(self.tag_fields).union(self.span_fields)
        all_field_names = set(self.tag_fields).union(self.span_fields.values())
        if len(all_field_names) != (len(self.tag_fields) + len(self.span_fields)):
            raise ValueError("duplicate field names in result schema")
        schema = [
            pyarrow.field("text", pyarrow.string()),
            pyarrow.field("tokens", pyarrow.list_(pyarrow.string())),
        ]
        for f in self.tag_fields:
            schema.append(pyarrow.field(f, pyarrow.list_(pyarrow.string())))
        for v in self.span_fields.values():
            schema.append(pyarrow.field(v, pyarrow.list_(arrowtypes.TextSpan())))
        self._schema = pyarrow.schema(schema)

    @property
    def num_instance_features(self) -> int:
        """The number of features in a single instance."""
        return len(self._schema.names)

    @property
    def partition_schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the subset of the features that
        should be represented using the ``pyarrow.dataset`` "partitioning"
        mechanism.
        """
        return None

    @property
    def schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the full set of features."""
        return self._schema

    def __call__(self, dataset_info, example):
        tag_dicts = {
            k: dataset_info.features[k].feature._int2str for k in self._all_fields
        }
        result = {}
        text = text_data.detokenize(example["tokens"])
        result["text"] = text
        result["tokens"] = list(example["tokens"])
        for f in self.tag_fields:
            result[f] = [tag_dicts[f][t] for t in example[f]]
        for k, v in self.span_fields.items():
            result[v] = [
                span.to_dict()
                for span in text_data.compute_spans(
                    text, example["tokens"], [tag_dicts[k][t] for t in example[k]]
                )
            ]
        logging.debug(result)
        return result


class Ingester:
    def __init__(self, dataset: api.Dataset | api.EntityKey | str, converter):
        if isinstance(dataset, api.Dataset):
            self.dataset = dataset
        else:
            self.dataset = api.get_dataset(dataset)
        self.converter = converter

        if self.dataset.sourceKind != api.DataSources.huggingface:
            raise ValueError(
                f"requires dataset.sourceKind = {api.DataSources.huggingface}"
            )

        self.data_source = api.get_data_source(self.dataset.source)
        self.dataset_info = get_dataset_info(self.data_source)

        self._partitions = []
        self._schema = [pyarrow.field("_index_", pyarrow.int64())]

        if self.dataset_info.splits:
            self._schema.append(pyarrow.field("split", pyarrow.string()))
            self._partitions.append(pyarrow.field("split", pyarrow.string()))

        if self.converter.partition_schema is not None:
            self._partitions.extend(
                pyarrow.field(name, type_)
                for name, type_ in zip(
                    self.converter.partition_schema.names,
                    self.converter.partition_schema.types,
                )
            )
        if self.converter.schema is not None:
            self._schema.extend(
                pyarrow.field(name, type_)
                for name, type_ in zip(
                    self.converter.schema.names, self.converter.schema.types
                )
            )

    @property
    def num_instance_features(self) -> int:
        """The number of features in a single instance."""
        return len(self._schema)

    @property
    def partition_schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the subset of the features that
        should be represented using the ``pyarrow.dataset`` "partitioning"
        mechanism.
        """
        return None if len(self._partitions) == 0 else pyarrow.schema(self._partitions)

    @property
    def schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the full set of features."""
        return pyarrow.schema(self._schema)

    def __iter__(self):
        data_source_path = storage.paths.datasource_root(self.data_source.key)
        logging.debug(f"data_source_path: {data_source_path}")
        blobs = [blob.name for blob in storage.gcs_list_dir(data_source_path)]
        logging.debug(f"blobs: {blobs}")

        next_index = 0
        if self.dataset_info.splits:
            for split in self.dataset_info.splits.values():
                logging.info(split.name)
                pattern = f"/{split.dataset_name}-{split.name}.*\\.parquet$"
                split_blobs = [blob for blob in blobs if re.search(pattern, blob)]
                logging.info(split_blobs)
                ds = io.open_dataset(
                    split_blobs, filesystem=config.resources.datasources.storage.url
                )

                for batch in ds.to_batches():
                    for item in batch.to_pylist():
                        converted = self.converter(self.dataset_info, item)
                        converted["_index_"] = next_index
                        converted["split"] = split.name
                        next_index += 1
                        logging.debug(converted)
                        yield converted
        else:
            logging.info("<no splits>")
            pattern = f"/.*\\.parquet$"
            blobs = [blob for blob in blobs if re.search(pattern, blob)]
            logging.info(blobs)
            ds = io.open_dataset(
                blobs, filesystem=config.resources.datasources.storage.url
            )

            for batch in ds.to_batches():
                for item in batch.to_pylist():
                    converted = self.converter(self.dataset_info, item)
                    converted["_index_"] = next_index
                    next_index += 1
                    logging.debug(converted)
                    yield converted
