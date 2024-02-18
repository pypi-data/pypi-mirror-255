# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.schema.platform import ModelSource, ModelSourceKinds


def fetch(local_path: str, source: ModelSource):
    if source.kind == ModelSourceKinds.GitLFS:
        if source.gitLFS is None:
            raise ValueError("gitLFS not specified")
        from .sources import git_lfs

        return git_lfs.fetch(local_path, source.gitLFS)
    elif source.kind == ModelSourceKinds.HuggingFaceHub:
        if source.huggingFaceHub is None:
            raise ValueError("huggingFaceHub not specified")
        from .sources import huggingface_hub

        return huggingface_hub.fetch(local_path, source.huggingFaceHub)
    elif source.kind == ModelSourceKinds.OpenLLM:
        if source.openLLM is None:
            raise ValueError("openLLM not specified")
        from .sources import open_llm

        return open_llm.fetch(local_path, source.openLLM)
    elif source.kind == ModelSourceKinds.Upload:
        pass
    else:
        raise ValueError(str(source))


def main(argv: list[str]):
    local_path = argv[1]
    source = ModelSource.parse_raw(argv[2])
    fetch(local_path, source)


if __name__ == "__main__":
    import absl.app  # type: ignore[import-untyped]

    absl.app.run(main)
