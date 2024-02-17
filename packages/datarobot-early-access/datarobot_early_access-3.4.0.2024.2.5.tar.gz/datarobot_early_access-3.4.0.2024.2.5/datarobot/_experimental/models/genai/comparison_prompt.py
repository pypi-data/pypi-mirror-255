#
# Copyright 2023 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import trafaret as t

from datarobot._experimental.models.genai.chat_prompt import (
    Citation,
    citation_trafaret,
    confidence_scores_trafaret,
    ConfidenceScores,
    result_metadata_trafaret,
    ResultMetadata,
)
from datarobot._experimental.models.genai.llm_blueprint import LLMBlueprint
from datarobot.models.api_object import APIObject
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


def _get_genai_entity_id(entity: Union[ComparisonPrompt, LLMBlueprint, str]) -> str:
    """
    Get the entity ID from the entity parameter.

    Parameters
    ----------
    entity : ApiObject or str
        May be entity ID or the entity.

    Returns
    -------
    id : str
        The entity ID.
    """
    if isinstance(entity, str):
        return entity

    return entity.id


comparison_prompt_result_trafaret = t.Dict(
    {
        t.Key("llm_blueprint_id"): t.String,
        t.Key("result_metadata", optional=True): t.Or(result_metadata_trafaret, t.Null),
        t.Key("result_text", optional=True): t.Or(t.String, t.Null),
        t.Key("confidence_scores", optional=True): t.Or(confidence_scores_trafaret, t.Null),
        t.Key("citations"): t.List(citation_trafaret),
        t.Key("execution_status"): t.String,
    }
).ignore_extra("*")


comparison_prompt_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("text"): t.String,
        t.Key("results"): t.List(comparison_prompt_result_trafaret),
        t.Key("creation_date"): t.String,
        t.Key("creation_user_id"): t.String,
    }
).ignore_extra("*")


class ComparisonPromptResult(APIObject):
    """
    Metadata for a DataRobot GenAI comparison prompt result.

    Attributes
    ----------
    llm_blueprint_id : str
        ID of the LLM blueprint associated with the chat prompt.
    result_metadata : ResultMetadata or None
        Metadata for the result of the chat prompt submission.
    result_text: str or None
        The result text from the chat prompt submission.
    confidence_scores: ConfidenceScores or None
        The confidence scores if there is a vector database associated with the chat prompt.
    citations: list[Citation]
        List of citations from text retrieved from the vector database, if any.
    execution_status: str
        The execution status of the chat prompt.
    """

    _converter = comparison_prompt_result_trafaret

    def __init__(
        self,
        llm_blueprint_id: str,
        citations: List[Dict[str, Any]],
        execution_status: str,
        result_metadata: Optional[Dict[str, Any]] = None,
        result_text: Optional[str] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
    ):
        self.llm_blueprint_id = llm_blueprint_id
        self.citations = [Citation.from_server_data(citation) for citation in citations]
        self.execution_status = execution_status
        self.result_metadata = (
            ResultMetadata.from_server_data(result_metadata) if result_metadata else None
        )
        self.result_text = result_text
        self.confidence_scores = (
            ConfidenceScores.from_server_data(confidence_scores) if confidence_scores else None
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(llm_blueprint_id={self.llm_blueprint_id}, "
            f"execution_status={self.execution_status})"
        )


class ComparisonPrompt(APIObject):
    """
    Metadata for a DataRobot GenAI comparison prompt.

    Attributes
    ----------
    id : str
        Comparison prompt ID.
    text : str
        The prompt text.
    results : list[ComparisonPromptResult]
        The list of results for individual LLM blueprints that are part of the comparison prompt.
    creation_date : str
        Date when the playground was created.
    creation_user_id : str
        ID of the creating user.
    """

    _path = "api-gw/genai/comparisonPrompts"

    _converter = comparison_prompt_trafaret

    def __init__(
        self,
        id: str,
        text: str,
        results: List[Dict[str, Any]],
        creation_date: str,
        creation_user_id: str,
    ):
        self.id = id
        self.text = text
        self.results = [ComparisonPromptResult.from_server_data(result) for result in results]
        self.creation_date = creation_date
        self.creation_user_id = creation_user_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, text={self.text[:1000]})"

    @classmethod
    def create(
        cls,
        llm_blueprints: List[Union[LLMBlueprint, str]],
        text: str,
        wait_for_completion: bool = False,
    ) -> ComparisonPrompt:
        """
        Create a new ComparisonPrompt. This submits the prompt text to the LLM blueprints that
        are specified.

        Parameters
        ----------
        llm_blueprints : list[LLMBlueprint or str]
            The LLM blueprints associated with the created comparison prompt.
            Accepts LLM blueprints or IDs.
        text : str
            The prompt text.
        wait_for_completion : bool
            If set to True code will wait for the chat prompt job to complete before
            returning the result (up to 10 minutes, raising timeout error after that).
            Otherwise, you can check current status by using ChatPrompt.get with returned ID.

        Returns
        -------
        comparison_prompt : ComparisonPrompt
            The created comparison prompt.
        """
        payload = {
            "llm_blueprint_ids": [
                _get_genai_entity_id(llm_blueprint) for llm_blueprint in llm_blueprints
            ],
            "text": text,
        }

        url = f"{cls._client.domain}/{cls._path}/"
        r_data = cls._client.post(url, data=payload)
        if wait_for_completion:
            location = wait_for_async_resolution(cls._client, r_data.headers["Location"])
            return cls.from_location(location)
        return cls.from_server_data(r_data.json())

    @classmethod
    def get(cls, comparison_prompt: Union[ComparisonPrompt, str]) -> ComparisonPrompt:
        """
        Retrieve a single comparison prompt.

        Parameters
        ----------
        comparison_prompt : str
            The comparison prompt you want to retrieve. Accepts entity or ID.

        Returns
        -------
        comparison_prompt : ComparisonPrompt
            The requested comparison prompt.
        """
        url = f"{cls._client.domain}/{cls._path}/{_get_genai_entity_id(comparison_prompt)}/"
        r_data = cls._client.get(url)
        return cls.from_server_data(r_data.json())

    @classmethod
    def list(
        cls,
        llm_blueprints: List[Union[LLMBlueprint, str]],
    ) -> List[ComparisonPrompt]:
        """
        List all comparison prompts available to the user that include the specified LLM blueprints.

        Parameters
        ----------
        llm_blueprints : [List[Union[LLMBlueprint, str]]]
            The returned comparison prompts are only those associated with the specified LLM
            blueprints. Accepts either the entity or the ID.

        Returns
        -------
        comparison_prompts : list[ComparisonPrompt]
            A list of comparison prompts available to the user that use the specified LLM
            blueprints.
        """
        params = {
            "llm_blueprint_ids": [
                _get_genai_entity_id(llm_blueprint) for llm_blueprint in llm_blueprints
            ],
        }
        url = f"{cls._client.domain}/{cls._path}/"
        r_data = unpaginate(url, params, cls._client)
        return [cls.from_server_data(data) for data in r_data]

    def update(
        self,
        additional_llm_blueprints: List[Union[LLMBlueprint, str]],
        wait_for_completion: bool = False,
    ) -> ComparisonPrompt:
        """
        Update the comparison prompt.

        Parameters
        ----------
        additional_llm_blueprints : list[LLMBlueprint or str]
            The additional LLM blueprints you want to submit the comparison prompt.

        Returns
        -------
        comparison_prompt : ComparisonPrompt
            The updated comparison prompt.
        """
        payload = {
            "additionalLLMBlueprintIds": [
                _get_genai_entity_id(bp) for bp in additional_llm_blueprints
            ],
        }
        url = f"{self._client.domain}/{self._path}/{_get_genai_entity_id(self.id)}/"
        r_data = self._client.patch(url, data=payload)
        if wait_for_completion:
            location = wait_for_async_resolution(self._client, r_data.headers["Location"])
            return self.from_location(location)
        return self.from_server_data(r_data.json())

    def delete(self) -> None:
        """
        Delete the single comparison prompt.
        """
        url = f"{self._client.domain}/{self._path}/{_get_genai_entity_id(self.id)}/"
        self._client.delete(url)
