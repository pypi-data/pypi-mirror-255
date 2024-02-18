# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import copy
import json
import math
import time
import urllib
from pathlib import Path
from typing import Dict, List

import requests
from absl import logging

from dyff.api.data import content_hash
from dyff.api.data.sinks import DataSink


class ZenodoRecord:
    def __init__(self, url: str):
        if not url.startswith("https://zenodo.org/api/records/"):
            raise ValueError(
                f"url: expected Zenodo API 'records' endpoint (https://zenodo.org/api/records/)"
            )
        parsed_url = urllib.parse.urlparse(url)  # Verify format
        self._url = url
        r = requests.get(url)
        r.raise_for_status()
        self._record = json.loads(r.content)

    @property
    def resource_id(self) -> str:
        """The unique ID of this resource.

        A resource may consist of multiple files or subdirectories, but they
        can all be found under the ``resource_id``.
        """
        return content_hash(self._record["doi"].encode())

    def metadata_as_json(self) -> Dict:
        """The implementation-specific resource metadata in JSON format.

        Returns:
          A Dict suitable for encoding as JSON.
        """
        return copy.deepcopy(self._record)

    def fetch_into(self, sink: DataSink, *, retries: int = 5) -> List[Path]:
        """Fetches all the data in this source to the given sink.

        Args:
          sink: The DataSink instance
          retries: Must be >= 0. If > 0, the fetch will be retried up to this
            many times, with exponentially-increasing waits between each
            retry up to a maximum wait. The retry limit applies to each upload
            operation separately, but an exception is raised the first time
            any operation exceeds the retry limit.

        Raises:
          Exception: If the upload raises an exception and the retry limit is
            exceeded, the upload exception is propagated to the caller.
        """
        if retries < 0:
            raise ValueError("retries must be non-negative")

        retries_used = 0
        pending_resources = copy.deepcopy(self._record["files"])
        logging.info(
            f"pending_resources: {[fd['links']['self'] for fd in pending_resources]}"
        )
        files = []

        while pending_resources:
            fd = pending_resources[-1]
            url = fd["links"]["self"]
            parsed_url = urllib.parse.urlparse(url)
            filename = parsed_url.path.split("/")[-1]
            sink_path = f"{self.resource_id}/{filename}"
            # The Zenodo checksum looks like 'md5:<hexdigest>'
            algorithm, md5_hex = fd["checksum"].split(":")
            assert algorithm == "md5"

            if sink.resource_exists(sink_path):
                logging.info(f"skipping: {url}")
                pending_resources.pop()
                files.append(sink_path)
            else:
                try:
                    logging.info(f"fetching: {url}")
                    sink.upload_from_http(url, sink_path, md5_hex=md5_hex)
                    pending_resources.pop()
                    files.append(sink_path)
                    retries_used = 0
                except Exception:
                    if retries_used >= retries:
                        raise
                    else:
                        # Limited exponential backoff
                        backoff_exponent = min(retries_used, 5)
                        time.sleep(math.pow(2.0, backoff_exponent))
                        retries_used += 1

        # TODO: Make Builder for metadata object
        meta = {
            "source": self._url,
            "source_kind": "ZenodoRecord",
            "source_metadata": self.metadata_as_json(),
            "resource_id": self.resource_id,
            "sink_id": sink.sink_id,
            "files": [str(path) for path in files],
        }
        sink.upload_string(
            json.dumps(meta), f"{self.resource_id}/_alignmentlabs-meta.json"
        )

        return files
