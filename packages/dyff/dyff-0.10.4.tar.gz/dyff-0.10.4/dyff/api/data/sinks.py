# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import abc
import shutil
import subprocess
from typing import Optional

import google.cloud.exceptions
import requests
from absl import logging
from google.cloud import storage

from ...api.exceptions import MissingDependencyError
from ...schema.copydoc import copydoc
from . import google_storage_md5


class DataSinkError(RuntimeError):
    pass


class DataUploadError(DataSinkError):
    pass


class DataSink:
    @property
    @abc.abstractmethod
    def sink_id(self) -> str:
        """The idenfitier of this data sink."""
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_exists(self, sink_path: str) -> bool:
        """Checks if a valid resource exists at ``sink_path``.

        Args:
          sink_path: The identifier of the resource in the data sink.

        Returns:
          True if and only if a valid resource exists at ``sink_path``.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_string(self, data: str, sink_path: str):
        """Uploads raw data in the form of a string.

        Args:
          data: The data to upload.
          sink_path: The identifier of the resource in the data sink.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_from_http(
        self, source_url: str, sink_path: str, *, md5_hex: Optional[str] = None
    ):
        """Uploads the data at ``source_url`` to ``sink_path`` within the data
        sink.

        Args:
          source_url: The URL of the resource to upload.
          sink_path: The identifier of the resource in the data sink.
          md5_hex: If specified, the upload will fail and be rolled back if the
            md5 checksum of the uploaded data does not match this argument.
            Callers should provide this argument whenever possible.

        Raises:
          ConnectionError: If something goes wrong with network connections.
          DataUploadError: If the upload failed for some reason other than the
            connection.
        """
        raise NotImplementedError()


class GoogleStorageUploader(DataSink):
    def __init__(self, bucket_id: str):
        """Data sink that uploads to a Google Storage bucket.

        Args:
          bucket: A storage bucket that is already created.

        Raises:
          alignmentlabs.dyff.exceptions.MissingDependencyError: If necessary
            command-line tools are not installed.
          DataSinkError: If connecting to the bucket fails. This will often be
            due to authentication problems, or the bucket not existing.
        """
        if shutil.which("curl") is None:
            raise MissingDependencyError("'curl' is not installed")
        if shutil.which("gsutil") is None:
            raise MissingDependencyError("'gsutil' is not installed")

        client = storage.Client()
        # Note: get_bucket() requires more privileges than writing to a
        # specific bucket
        self._bucket_id = bucket_id
        self._bucket = client.bucket(bucket_id)
        try:
            self.resource_exists("_test")  # Just to see if it raises an exception
        except google.cloud.exceptions.Forbidden as ex:
            logging.error(f"Forbidden: {bucket_id}")
            raise DataSinkError(f"Forbidden: {bucket_id}") from ex
        except google.cloud.exceptions.NotFound as ex:
            logging.error(f"NotFound: {bucket_id}")
            raise DataSinkError(f"NotFound: {bucket_id}") from ex

    @property
    @copydoc(DataSink.sink_id)
    def sink_id(self) -> str:
        return f"gs://{self._bucket_id}"

    @copydoc(DataSink.resource_exists)
    def resource_exists(self, sink_path: str) -> bool:
        return self._bucket.get_blob(sink_path) is not None

    @copydoc(DataSink.upload_string)
    def upload_string(self, data: str, sink_path: str):
        blob = self._bucket.blob(sink_path)
        blob.upload_from_string(data, checksum="md5")

    @copydoc(DataSink.upload_from_http)
    def upload_from_http(
        self, source_url: str, sink_path: str, *, md5_hex: Optional[str] = None
    ):
        # I can't figure out how to check for errors from the 'curl' part of
        # the pipeline below, so we'll confirm the URL is working here.
        try:
            r = requests.head(source_url)
            r.raise_for_status()
        except requests.RequestException as ex:
            raise ConnectionError(f"something is wrong with {source_url}") from ex
        else:
            if r.status_code != 200:
                raise ConnectionError(
                    f"http error {r.status_code} (expected 200): {source_url}"
                )

        gsutil_args = ["gsutil"]
        if md5_hex is not None:
            md5_google = google_storage_md5(md5_hex=md5_hex)
            gsutil_args.extend(["-h", f"Content-MD5:{md5_google}"])
        gsutil_args.extend(["cp", "-", f"gs://{self._bucket.name}/{sink_path}"])
        gsutil = subprocess.Popen(
            gsutil_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        curl = subprocess.Popen(
            ["curl", source_url], stdout=gsutil.stdin, stderr=subprocess.DEVNULL
        )
        stdout, stderr = gsutil.communicate()

        if gsutil.returncode != 0:
            logging.error(stderr.decode())
            raise DataUploadError(f"upload failed with error code {gsutil.returncode}")


if __name__ == "__main__":
    client = storage.Client()
    bucket = client.get_bucket("alignmentlabs-rawdata-14a802b4b854421f")
    sink = GoogleStorageUploader(bucket)
    sink.upload_from_http("https://unsplash.com/photos/N_G2Sqdy9QY", "test/cat")
    print(sink.resource_exists("test/cat"))
