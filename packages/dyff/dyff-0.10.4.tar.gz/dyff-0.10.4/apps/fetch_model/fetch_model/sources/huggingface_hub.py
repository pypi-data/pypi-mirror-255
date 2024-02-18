# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.schema.platform import ModelSourceHuggingFaceHub


def _impl(local_path: str, spec: ModelSourceHuggingFaceHub):
    import os

    import transformers.utils.hub  # type: ignore[import-untyped]
    from huggingface_hub import snapshot_download  # type: ignore[import-untyped]

    print(os.environ.get("HF_HOME"))
    print(os.environ.get("TRANSFORMERS_CACHE"))
    print(os.environ.get("HF_HUB_CACHE"))

    print(f"huggingface_hub: downloading {spec.repoID}")
    snapshot_download(
        spec.repoID,
        repo_type="model",
        revision=spec.revision,
        cache_dir=local_path,
        allow_patterns=spec.allowPatterns,
        ignore_patterns=spec.ignorePatterns,
        token=os.environ.get("DYFF_MODELS__HUGGINGFACE_ACCESS_TOKEN"),
    )

    print("migrating cache")
    transformers.utils.hub.move_cache(local_path, local_path)


def fetch(local_path: str, spec: ModelSourceHuggingFaceHub):
    import multiprocessing as mp
    import os

    os.environ["HF_HOME"] = local_path
    proc = mp.Process(target=_impl, args=(local_path, spec))
    proc.start()
    proc.join()
