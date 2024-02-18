#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import base64
import os
import secrets

import kubernetes.client
import kubernetes.config

# https://stackoverflow.com/a/51035715
if os.environ.get("KUBERNETES_SERVICE_HOST"):
    kubernetes.config.load_incluster_config()
else:
    kubernetes.config.load_kube_config()

api = kubernetes.client.CoreV1Api()
# token_urlsafe() raises 'binascii.Error: Incorrect padding' if you later try
# to base64 decode it
token = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
body = {"stringData": {"ALIGNMENTLABS_API_KEY_SIGNING_SECRET": token}}
api.patch_namespaced_secret(name="api-key-signing", namespace="default", body=body)
