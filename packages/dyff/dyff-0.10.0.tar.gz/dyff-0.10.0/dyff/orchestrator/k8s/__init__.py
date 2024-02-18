# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os

import kubernetes.config


def load_config():
    if not hasattr(load_config, "_loaded"):
        # https://stackoverflow.com/a/51035715
        if os.environ.get("KUBERNETES_SERVICE_HOST"):
            kubernetes.config.load_incluster_config()
        else:
            kubernetes.config.load_kube_config()
        load_config._loaded = True


load_config()


__all__ = ["load_config"]
