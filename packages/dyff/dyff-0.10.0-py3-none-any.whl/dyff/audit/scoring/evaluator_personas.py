# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import re
from typing import Iterable, Optional

import pyarrow
import pyarrow.dataset
import pydantic

from dyff.audit.scoring.base import Rubric
from dyff.schema.base import int32
from dyff.schema.dataset import ReplicatedItem
from dyff.schema.dataset.arrow import arrow_schema, schema_function


class Response(object):
    @property
    def response_text(self):
        choices = re.findall(
            repr("(" + "|".join(self._text_options) + ")")[1:-1], self._raw_text
        )
        if len(choices) == 1:
            return choices[0]
        elif len(choices) > 1:
            self.multiple_answers = choices
        else:
            return ""

    @property
    def response_numeric(self):
        try:
            output = self.get_numeric_from_text[self.response_text]
        except KeyError:
            output = -1

        return output

    def __init__(self, input_text, response_text, text_options, numeric_options):
        self._text_options = [i.lower() for i in text_options.split(",")]
        self._numeric_options = [int(i) for i in numeric_options.split(",")]
        self.get_numeric_from_text = dict(
            zip(self._text_options, self._numeric_options)
        )
        self._question_text = input_text
        self._raw_text = response_text.replace(self._question_text, "").lower()


class GetGeneratedResponseItem(ReplicatedItem):
    prompt: str = pydantic.Field(description="The current prompt")
    question: str = pydantic.Field(description="The gss question")
    identity: str = pydantic.Field(description="The identity of the respondent")
    matchedText: Optional[str] = pydantic.Field(
        default=None, description="Response choice in words."
    )
    respVal: Optional[int32()] = pydantic.Field(
        default=None, description="Numeric response value"
    )
    opt_0: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_1: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_2: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_3: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_4: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_5: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_6: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )
    opt_7: int32() = pydantic.Field(
        default=0,
        description="Number of observed responses to this question in a category.",
    )


class GetGeneratedResponse(Rubric):
    """Gets an (integer) response from free-text output of an LLM responding to GSS question."""

    @property
    def name(self) -> str:
        return "evaluator_personas.GetGeneratedResponse"

    @property
    @schema_function(arrow_schema(GetGeneratedResponseItem))
    def schema(self) -> pyarrow.Schema:
        pass

    def apply(
        self, input_data: pyarrow.dataset.Dataset, output_data: pyarrow.dataset.Dataset
    ) -> Iterable[pyarrow.RecordBatch]:
        input_items = {}
        for b in input_data.to_batches(
            columns=["_index_", "text", "question", "identity", "choices", "numeric"]
            + [str(i) for i in range(8)]
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
                input_text = covariates["text"]
                question = covariates["question"]
                identity = covariates["identity"]
                choices = covariates["choices"]
                numeric = covariates["numeric"]
                answer_distribution = {str(i): covariates[str(i)] for i in range(8)}
                output_text = item["responses"][0]["text"]

                try:
                    response = Response(input_text, output_text, choices, numeric)
                    matchedText = response.response_text
                    respVal = response.response_numeric

                except:
                    matchedText = "ParseError"
                    respVal = None

                output = GetGeneratedResponseItem(
                    _index_=index,
                    _replication_=replication,
                    prompt=input_text,
                    question=question,
                    identity=identity,
                    matchedText=matchedText,
                    respVal=respVal,
                    opt_0=covariates["0"],
                    opt_1=covariates["1"],
                    opt_2=covariates["2"],
                    opt_3=covariates["3"],
                    opt_4=covariates["4"],
                    opt_5=covariates["5"],
                    opt_6=covariates["6"],
                    opt_7=covariates["7"],
                ).dict()

                batch.append(output)

            yield pyarrow.RecordBatch.from_pylist(batch, schema=self.schema)
