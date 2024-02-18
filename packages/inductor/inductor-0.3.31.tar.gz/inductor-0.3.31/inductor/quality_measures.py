# Copyright 2023 Inductor, Inc.
"""Functions for running quality measures."""

from typing import Any

import openai
import tiktoken

from inductor import wire_model

class Inputs(dict):
    """A dictionary that allows access to its keys as attributes."""

    def __getattribute__(self, key: str) -> Any:
        """Return the value corresponding to key in this dict.
        
        Args:
            key: The key to access.

        Raises:
            AttributeError: If the key does not exist in this dict.
        """
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc


def openai_llm_quality_measure(
    output: str,
    inputs: Inputs,
    test_case: wire_model.TestCase,
    quality_measure: wire_model.QualityMeasure,
    model: str,
    prompt: str
) -> str:
    """Evaluate an LLM-powered quality measure using the OpenAI API.
    
    Args:
        output: The output of the execution of a LLM program.
        inputs: The inputs to the LLM program execution that produced output.
        test_case: The test case that served as input to the LLM program
            execution that produced output.
        quality_measure: The quality measure being evaluated.
        model: The model to use in the LLM powered quality measure.
        prompt: The prompt for the LLM powered quality measure.

    Returns:
        The result of evaluating the quality measure.
    """
    client = openai.OpenAI()
    accepted_outputs = []
    evaluation_type_prompt = ""
    if quality_measure.evaluation_type == "BINARY":
        evaluation_type_prompt = (
            "Output must be *ONLY* one of Y (for YES) or N (for NO).")
        accepted_outputs = ["Y", "N"]
    elif quality_measure.evaluation_type == "RATING_INT":
        evaluation_type_prompt = (
            "Output must be *ONLY* an integer from 1 through 5.")
        accepted_outputs = ["1", "2", "3", "4", "5"]

    encoding = tiktoken.encoding_for_model(model)
    max_tokens = 1
    logit_bias = {}
    for accepted in accepted_outputs:
        tokens = encoding.encode(accepted)
        max_tokens = max(max_tokens, len(tokens))
        logit_bias.update({token: 100 for token in tokens})

    execution = {"output": output, "inputs": inputs, "test_case": test_case}
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt.format_map(execution)},
            {"role": "system", "content": evaluation_type_prompt}
        ],
        model=model,
        max_tokens=max_tokens,
        logit_bias=logit_bias)
    return chat_completion.choices[0].message.content
