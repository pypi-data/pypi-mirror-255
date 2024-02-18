# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, NamedTuple


# FIXME: This probably should be a pydantic type now?
class TextSpan(NamedTuple):
    start: int
    end: int
    tag: str

    def to_dict(self) -> Dict[str, Any]:
        return self._asdict()


def compute_spans(text: str, tokens: List[str], tags: List[str]) -> List[TextSpan]:
    spans = []
    i = 0
    start = None
    end = None
    current_tag = None

    def finish_span():
        nonlocal spans, start, end, current_tag

        if current_tag is not None:
            spans.append(TextSpan(start, end, current_tag))
        start = None
        end = None
        current_tag = None

    for token_index, token in enumerate(tokens):
        tag = tags[token_index]
        if tag == "O":
            finish_span()
        elif tag.startswith("B-"):
            finish_span()
            current_tag = tag[2:]
        elif tag.startswith("I-"):
            assert tag[2:] == current_tag

        while text[i] != token[0]:
            i += 1
        if start is None:
            start = i
        for c in token:
            assert text[i] == c
            i += 1
        end = i
    finish_span()

    return spans


def visualize_spans(text: str, spans: List[TextSpan], *, width: int = 80):
    start = 0
    next_span = 0
    while start < len(text):
        span_text = []
        end = min(start + 80, len(text))
        print(text[start:end])
        s = start
        while next_span < len(spans):
            span = spans[next_span]
            span_start = max(span.start, start)
            span_end = min(span.end, end)
            if span_start < end:
                span_text.extend("." * (span_start - s))
                span_text.extend(span.tag[0] * (span_end - span_start))
            s = span_end
            if span.end >= end:
                break
            else:
                next_span += 1
        if len(span_text) < width:
            span_text.extend("." * ((end - start) - len(span_text)))
        print("".join(span_text))
        start += width


def detokenize(tokens: List[str]) -> str:
    from nltk.tokenize.treebank import TreebankWordDetokenizer

    return TreebankWordDetokenizer().detokenize(tokens)
