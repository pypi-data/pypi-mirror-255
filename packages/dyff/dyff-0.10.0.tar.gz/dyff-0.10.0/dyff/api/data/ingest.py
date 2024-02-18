# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""Tools for ingesting raw data into Apache Arrow datasets.

We model the raw data as an ``Archive``, which is a generator of
``ArchiveEntry``s. Each ``ArchiveEntry`` consists of a path to a leaf file
in the dataset, and the raw bytes of that file. A ``FileProcessor`` wraps
an ``Archive`` to create a generator of individual instance, represented
as nested dictionaries. This generator then goes to the ``write_dataset``
function of ``pyarrow``.

Processing happens in streaming mode, to accommodate raw data that will not
fit in memory. Processors must not assume that the files arrive in any
particular order, but they should assume that a depth-first order is
the typical case.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Generator, List, Optional, Sequence, Union

import numpy as np
import pyarrow
import pyarrow.dataset
import pyarrow.fs
import yaml
from absl import logging
from smart_open import open

from ...core import dynamic_import

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from ...api import storage
from ...api.data import archives
from ...api.typing import PathLike

DataTypeConstructor = Callable[[], pyarrow.DataType]


class PathFeatureExtractor:
    """Extracts individual data instances whose features are specified through
    a combination of path elements and entries in data files.

    Our abstract model of a dataset is a list of one or more "archives". Each
    archive contains a tree of "paths" terminating in "leaf" files. The paths
    encode a subset of the features, such as different "splits"
    of the data or different "intensities" of the same data manipulation. The
    rest of the features are encoded in the leaf files. For example, the leafs
    might be .csv files with columns for different features, or they might be
    .jpeg files that conceptually encode a single "feature" called "image".

    Feature extraction from leafs is delegated to "leaf processors". The
    ``PathFeatureExtractor`` wraps these leaf processors to create a generator
    that extracts features from both leaf files and path elements.

    Once ``leaf()`` has been called, the PathFeatureExtractor is "finished" and
    no more features can be added. After calling ``leaf()``, each call to
    ``__call__(archive)`` returns a generator that yields instances from that
    archive. The extractor adds a special feature named ``_index_`` that
    uniquely identifies each item in the dataset. Note that the archives are
    considered parts of the same dataset, so the index **does not reset**
    between archives.
    """

    def __init__(self):
        self._partitions = []
        self._features = [pyarrow.field("_index_", pyarrow.int64())]
        self._path_feature_index = {}
        self._n = 0
        self._leaf_processor = None
        self._next_index = 0

    @property
    def num_instance_features(self) -> int:
        """The number of features in a single instance."""
        return self._n

    @property
    def partition_schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the subset of the features that
        should be represented using the ``pyarrow.dataset`` "partitioning"
        mechanism.
        """
        return None if len(self._partitions) == 0 else pyarrow.schema(self._partitions)

    @property
    def feature_schema(self) -> pyarrow.Schema:
        """The ``pyarrow.schema`` describing the subset of the features that
        should be represented as columns within data tables.
        """
        return pyarrow.schema(self._features + self._leaf_processor.fields())

    def path_features(self, path: str) -> Dict[str, str]:
        """Returns a ``{name: value}`` ``dict`` of the features encoded in
        ``path``.
        """
        p = Path(path)
        return {name: p.parts[i] for name, i in self._path_feature_index.items()}

    def partition(
        self, name: str, arrow_type: DataTypeConstructor
    ) -> PathFeatureExtractor:
        """Configures the feature extractor to represent the next path element
        as a partition feature.

        Args:
          name: The name of the feature
          arrow_type: A ``Callable`` that returns a ``pyarrow.DataType`` instance
            specifying how to encode the feature. Usually, this will be one of
            the ``pyarrow`` datatype classes.

        Returns:
          ``self``
        """
        if self._leaf_processor:
            raise RuntimeError("already specified leaf()")
        self._path_feature_index[name] = self._n
        # Partition features have to be in the main schema as well or the
        # partition directories won't be created
        self._features.append(pyarrow.field(name, arrow_type()))
        self._partitions.append(pyarrow.field(name, arrow_type()))
        self._n += 1
        return self

    def feature(
        self, name: str, arrow_type: DataTypeConstructor
    ) -> PathFeatureExtractor:
        """Configures the feature extractor to represent the next path element
        as a data table column.

        Args:
          name: The name of the feature
          arrow_type: A ``Callable`` that returns a ``pyarrow.DataType`` instance
            specifying how to encode the feature. Usually, this will be one of
            the ``pyarrow`` datatype classes.

        Returns:
          ``self``
        """
        if self._leaf_processor:
            raise RuntimeError("already specified leaf()")
        self._path_feature_index[name] = self._n
        self._features.append(pyarrow.field(name, arrow_type()))
        self._n += 1
        return self

    def skip(self) -> PathFeatureExtractor:
        """Configures the feature extractor to skip the next path element (i.e.,
        not to extract and store it as a feature).

        Returns:
          ``self``
        """
        if self._leaf_processor:
            raise RuntimeError("already specified leaf()")
        self._n += 1
        return self

    def leaf(self, processor) -> PathFeatureExtractor:
        """Configures the feature extractor to use the provided file processor
        on leaf files encountered while traversing the tree of paths in the
        dataset.

        It is an error to specify ``leaf()`` more than once.

        Args:
          processor: A leaf file processor instance.

        Returns:
          ``self``
        """
        if self._leaf_processor:
            raise RuntimeError("already specified leaf()")
        self._leaf_processor = processor
        return self

    def __call__(self, archive: archives.Archive) -> Generator:
        """Returns a generator that yields instances extracted from the specified
        archive.

        Args:
          archive: The archive containing the raw data.

        Returns:
          A generator that yields individual data instances.
        """
        data_generator = self._leaf_processor(path_feature_extractor=self)
        for item in data_generator(archive):
            item["_index_"] = self._next_index
            self._next_index += 1
            yield item


class ImageFile:
    """A leaf file processor that handles individual image files."""

    def __init__(self, path_feature_extractor=None):
        self._path_feature_extractor = path_feature_extractor

    @staticmethod
    def fields():
        return [
            pyarrow.field(
                "image",
                pyarrow.struct(
                    [
                        pyarrow.field("bytes", pyarrow.binary()),
                        pyarrow.field("format", pyarrow.string()),
                    ]
                ),
            )
        ]

    def __call__(self, archive):
        for e in archive:
            p = Path(e.path)
            ext = p.suffix.lower()
            if ext in [".jpg", ".jpeg"]:
                instance = {"image": {"format": "image/jpeg", "bytes": e.bytes}}
            else:
                raise NotImplementedError(f"file type: {ext}")
            if self._path_feature_extractor is not None:
                path_features = self._path_feature_extractor.path_features(p)
                instance.update(path_features)
            yield instance


class BatchFile:
    pass


class NumpyBatch(BatchFile):
    def __init__(
        self,
        filename_pattern: str,
        *,
        feature_names: Union[str, List[str]],
        feature_axes: Optional[Sequence[int]],
    ):
        self._filename_pattern = filename_pattern
        if not isinstance(feature_names, list):
            self._feature_names = [feature_names]
        else:
            self._feature_names = feature_names
        self._feature_axes = feature_axes

    def filename_matches(self, filename: str) -> bool:
        return bool(re.match(self._filename_pattern, filename))

    def __call__(self, entry: archives.ArchiveEntry):
        tensor = np.load(entry.bytes)
        for element in tensor:
            if self._feature_axes is None:
                # Each element is a single feature
                shape = element.shape
                instance = {
                    self._feature_names[0]: {
                        "format": "numpy/hwc",
                        "shape": shape,
                        "elements": np.flatten(element),
                    }
                }
        else:
            # TODO: Each element is a feature vector
            raise NotImplementedError()
        yield instance


class BatchFiles:
    def __init__(self, processors: List[BatchFile]):
        self._processors = processors
        # Accumulate the files in each leaf directory
        self._pending_files = defaultdict(lambda: [None] * len(self._files))

    def __call__(self, archive):
        for e in archive:
            p = Path(e.path)
            file_list = self._pending_files(str(p.parent))
            # Assign the file to the matching processor
            for i, processor in enumerate(self._processors):
                if processor.filename_matches(p.name):
                    file_list[i] = e
                    break
            else:
                raise RuntimeError(f"no processor matching filename {p.name}")
            # If we have all of the files for this leaf path, run the corresponding
            # generators and yield the combined results.
            if all(x is not None for x in file_list):
                del self._pending_files[str(p.parent)]
                generators = [
                    processor(f) for processor, f in zip(self._processors, file_list)
                ]
                for output_tuple in zip(generators):
                    d = {}
                    for output in output_tuple:
                        d.update(output)
                    yield d


class Batcher:
    """Adapts a generator of individual data instances to yield
    ``pyarrow.RecordBatch``s.
    """

    def __init__(self, batch_size: int, *, schema: pyarrow.Schema = None):
        self._batch_size = batch_size
        self._schema = schema

    def __call__(self, source):
        batch = []
        batch_count = 0
        for record in source:
            batch.append(record)
            if len(batch) >= self._batch_size:
                logging.debug(f"batch {batch_count}")
                batch_count += 1
                yield pyarrow.RecordBatch.from_pylist(batch, schema=self._schema)
                batch = []
        if len(batch) > 0:
            logging.debug(f"batch {batch_count} (partial)")
            yield pyarrow.RecordBatch.from_pylist(batch, schema=self._schema)


def _construct_regex(format: str) -> str:
    regex = []
    parsing_name = False
    current_name = []
    i = 0
    while i < len(format):
        c = format[i]
        format[i + 1] if i + 1 < len(format) else None
        # if c == "*":
        #   if succ == "*":
        #     if double_star is not None:
        #       raise ValueError("at most one '**' allowed")
        #     elif i == 0:
        #       double_star = "start"
        #     elif i == len(format) - 2:
        #       double_star = "end"
        #     else:
        #       double_star = "mid"
        if c == "{":
            if parsing_name:
                raise ValueError(f"nested '{{' at {i}")
            else:
                parsing_name = True
                current_name = []
        elif c == "}":
            if parsing_name:
                name = "".join(current_name)
                # named capture group
                if i + 1 < len(format):
                    stop_char = format[i + 1]
                    regex.append(f"(?P<{name}>[^{stop_char}]+)")
                else:
                    regex.append(f"(?P<{name}>.+)$")
                parsing_name = False
            else:
                raise ValueError(f"nested '}}' at {i}")
        else:
            if parsing_name:
                current_name.append(c)
            else:
                regex.append(re.escape(c))
    return re.compile("".join(regex))


def ingest_generator(
    data_generator,
    *,
    output_path: str,
    feature_schema: pyarrow.Schema,
    partition_schema: pyarrow.Schema = None,
):
    """Creates a ``pyarrow.dataset.Dataset`` from a data generator.

    Args:
      data_generator: A generator that yields either individual instances or
        (more typically) ``pyarrow.RecordBatch`` instances.
      output_path: Location to store the ``pyarrow`` dataset. It could be a
        local directory or a storage bucket URL.
      feature_schema: The ``pyarrow.Schema`` for the dataset.
      partition_schema: If not ``None``, the ``pyarrow.Schema`` describing the
        features that should be represented as partitions.
    """
    pyarrow.dataset.write_dataset(
        data_generator,
        output_path,
        format="parquet",
        schema=feature_schema,
        partitioning=(
            partition_schema
            and pyarrow.dataset.partitioning(partition_schema, flavor="hive")
        ),
        existing_data_behavior="overwrite_or_ignore",
    )


def ingest(yaml_spec: PathLike, *, batch_size: int = 100, dryrun: bool = False):
    """Creates a ``pyarrow.dataset.Dataset`` from a YAML file describing
    how to parse the dataset.

    Args:
      yaml_spec: A path to a YAML file describing how to parse the dataset.
        Could be a local path or a gs:// path.
    """
    raise NotImplementedError()

    with open(yaml_spec, "r") as fin:
        dataset = yaml.load(fin, Loader=Loader)
    logging.info(f"YAML spec: {dataset}")

    account = dataset["metadata"]["labels"]["account"]
    dataset_id = dataset["metadata"]["labels"]["dataset"]
    dataset_key = EntityKey.create(account, dataset_id)

    path_feature_extractor = PathFeatureExtractor()
    for feature_spec in dataset["spec"]["extractor"]:
        action = feature_spec["action"]
        if action == "partition":
            name = feature_spec["name"]
            data_type = dynamic_import.symbol(feature_spec["type"])
            path_feature_extractor.partition(name, data_type)
        elif action == "feature":
            name = feature_spec["name"]
            data_type = dynamic_import.symbol(feature_spec["type"])
            path_feature_extractor.feature(name, data_type)
        elif action == "skip":
            path_feature_extractor.skip()
        elif action == "leaf":
            leaf_processor_type = dynamic_import.symbol(feature_spec["type"])
            path_feature_extractor.leaf(leaf_processor_type)
        else:
            raise ValueError(f"unknown action {action} in 'extractor'")

    logging.info(f"feature_schema:\n{path_feature_extractor.feature_schema}")
    logging.info(f"partition_schema:\n{path_feature_extractor.partition_schema}")

    input_path = storage.paths.datasource_root(dataset["spec"]["source"])
    output_path = storage.paths.dataset_data(dataset_key)
    for archive_file in dataset["spec"]["archives"]:
        name = dataset["spec"]["archiveFormat"]["name"]
        m = re.match(name, archive_file)
        if not m:
            raise ValueError(f"archiveFormat.name didn't match: {name}")
        archive_name = m.group(1)
        format = dataset["spec"]["archiveFormat"]["format"]
        logging.info(f"archive: {archive_name} ({format})")

        if dryrun:
            continue

        if format == "tar":
            archive = archives.TarArchive(
                f"{input_path}/{archive_file}", prefix=archive_name
            )
        else:
            raise NotImplementedError(f"archiveFormat.format: {format}")

        ingest_generator(
            Batcher(batch_size)(path_feature_extractor(archive)),
            output_path=output_path,
            feature_schema=path_feature_extractor.feature_schema,
            partition_schema=path_feature_extractor.partition_schema,
        )
