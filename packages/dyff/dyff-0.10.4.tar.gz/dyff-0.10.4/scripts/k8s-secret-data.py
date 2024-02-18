#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import base64
import secrets

import absl.app
import absl.flags
import kubernetes.client

# -----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string("secret", None, "Name of the k8s Secret resource")
absl.flags.DEFINE_string("namespace", "default", "Namespace of Secret resource")
absl.flags.DEFINE_string("key", None, "Key of the secret value to set")
absl.flags.DEFINE_string("value", None, "Value to set")
absl.flags.DEFINE_integer(
    "random_bytes",
    None,
    "Generate secret value of specified number of bytes (urlsafe_b64encode'd)",
    lower_bound=8,
)
absl.flags.mark_flags_as_required(["secret", "key"])
absl.flags.mark_flags_as_mutual_exclusive(["value", "random_bytes"])


def get_secret(secret: str, key: str, *, namespace: str = "default") -> str:
    api = kubernetes.client.CoreV1Api()
    secret = api.read_namespaced_secret(secret, namespace=namespace)
    # This gets translated back to stringData automatically when mounting the
    # Secret as a volume, but here we have to do it manually.
    data = secret.data[key]
    return base64.b64decode(data).decode()


def set_secret(secret: str, key: str, value: str, *, namespace: str = "default") -> str:
    api = kubernetes.client.CoreV1Api()
    body = {"stringData": {key: value}}
    api.patch_namespaced_secret(name=secret, namespace=namespace, body=body)


# -----------------------------------------------------------------------------


def main(argv):
    if len(argv) != 2 or argv[1] not in ["get", "set"]:
        raise ValueError(
            "Usage: k8s-secret-data.py {get | set} --secret=<name> --key=<key> ..."
        )
    operation = argv[1]

    if operation == "get":
        string_data = get_secret(FLAGS.secret, FLAGS.key, namespace=FLAGS.namespace)
        print(string_data)
    elif operation == "set":
        if FLAGS.random_bytes is not None:
            # token_urlsafe() raises 'binascii.Error: Incorrect padding' if you later try
            # to base64 decode it
            value = base64.urlsafe_b64encode(
                secrets.token_bytes(FLAGS.random_bytes)
            ).decode()
        else:
            value = FLAGS.value
        set_secret(FLAGS.secret, FLAGS.key, value, namespace=FLAGS.namespace)


if __name__ == "__main__":
    absl.app.run(main)
