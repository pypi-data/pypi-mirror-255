# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from typing import Iterable, Optional

import pyarrow
import pyarrow.dataset
import pydantic

from dyff.audit.scoring.base import Rubric
from dyff.schema.base import int32
from dyff.schema.dataset import ReplicatedItem
from dyff.schema.dataset.arrow import arrow_schema, schema_function


class GetHeadlineFactItem(ReplicatedItem):
    label: str = pydantic.Field(description="The true label")
    category: str = pydantic.Field(description="The headline category")
    dataset: str = pydantic.Field(description="The source dataset")
    raw_answer: Optional[str] = pydantic.Field(default=None, description="Raw answer.")
    matchedText: Optional[str] = pydantic.Field(
        default=None, description="Cleaned answer."
    )


class GetHeadlineFact(Rubric):
    """Gets an (integer) resume score from free-text output of an LLM
    'resume review' system.
    """

    @property
    def name(self) -> str:
        return "evaluator_rubric.GetHeadlineFact"

    @property
    @schema_function(arrow_schema(GetHeadlineFactItem))
    def schema(self) -> pyarrow.Schema:
        pass

    def apply(
        self, input_data: pyarrow.dataset.Dataset, output_data: pyarrow.dataset.Dataset
    ) -> Iterable[pyarrow.RecordBatch]:
        input_items = {}
        for b in input_data.to_batches(
            columns=["_index_", "category", "label", "dataset", "text"]
        ):
            for item in b.to_pylist():
                input_items[item["_index_"]] = item

        for b in output_data.to_batches(
            columns=["_index_", "_replication_", "responses"]
        ):
            batch = []
            for item in b.to_pylist():
                index = item["_index_"]
                replication = item["_replication_"]
                covariates = input_items[index]
                label = covariates["label"]
                category = covariates["category"]
                input_text = covariates["text"]
                dataset = covariates["dataset"]
                output_text = item["responses"][0]["text"]

                raw_answer = output_text
                matchedText = output_text

                if input_text in output_text:
                    matchedText = output_text.replace(input_text, "")

                try:
                    output = GetHeadlineFactItem(
                        _index_=index,
                        _replication_=replication,
                        label=label,
                        category=category,
                        dataset=dataset,
                        raw_answer=raw_answer,
                        matchedText=matchedText,
                    ).dict()
                except:
                    output = GetHeadlineFactItem(
                        _index_=index,
                        _replication_=replication,
                        label=label,
                        category=category,
                        dataset=dataset,
                        raw_answer=None,
                        matchedText=None,  # or: "ERROR"
                    ).dict()
                batch.append(output)

            yield pyarrow.RecordBatch.from_pylist(batch, schema=self.schema)
