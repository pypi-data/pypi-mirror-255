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

from typing import Any, Dict, Optional

import trafaret as t

from datarobot.models.api_object import APIObject
from datarobot.utils.waiters import wait_for_async_resolution

custom_model_validation_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("prompt_column_name"): t.String,
        t.Key("target_column_name"): t.String,
        t.Key("deployment_id"): t.String,
        t.Key("validation_status"): t.String,
        t.Key("model_id"): t.String,
        t.Key("deployment_access_data", optional=True, default=None): t.Or(
            t.Null,
            t.Dict(
                {
                    t.Key("prediction_api_url"): t.String,
                    t.Key("datarobot_key"): t.String,
                    t.Key("authorization_header"): t.String,
                    t.Key("input_type"): t.String,
                    t.Key("model_type"): t.String,
                }
            ).ignore_extra("*"),
        ),
        t.Key("tenant_id"): t.String,
        t.Key("error_message", optional=True, default=None): t.Or(t.Null, t.String),
    }
).ignore_extra("*")


class CustomModelValidation(APIObject):
    """
    Validation record checking the ability of the deployment to serve
    as a custom model LLM or vector database.

    Attributes
    ----------
    prompt_column_name : str
        The column name that the deployed model expects as the input.
    target_column_name : str
        The target name that the deployed model will output.
    deployment_id : str
        ID of the deployment.
    model_id : str
        ID of the underlying deployment model.
        Can be found from the API as Deployment.model["id"].
    validation_status : str
        Can be TESTING, FAILED, or PASSED. Only PASSED is allowed for use.
    deployment_access_data : dict, optional
        Data that will be used for accessing deployment prediction server.
        Only available for deployments that pass validation. Dict fields:
        - prediction_api_url - URL for deployment prediction server.
        - datarobot_key - First of two auth headers for the prediction server.
        - authorization_header - Second of two auth headers for the prediction server.
        - input_type - Either JSON or CSV - input type model expects.
        - model_type - Target type of deployed custom model.
    tenant_id : str
        Creating user's tenant ID.
    error_message : Optional[str]
        Additional information for errored validation.
    """

    _path: str
    _converter = custom_model_validation_trafaret

    def __init__(
        self,
        id: str,
        prompt_column_name: str,
        target_column_name: str,
        deployment_id: str,
        model_id: str,
        validation_status: str,
        deployment_access_data: Optional[Dict[str, Any]],
        tenant_id: str,
        error_message: Optional[str],
    ):
        self.id = id
        self.prompt_column_name = prompt_column_name
        self.target_column_name = target_column_name
        self.deployment_id = deployment_id
        self.model_id = model_id
        self.validation_status = validation_status
        self.deployment_access_data = deployment_access_data
        self.tenant_id = tenant_id
        self.error_message = error_message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    @classmethod
    def get(cls, validation_id: str) -> CustomModelValidation:
        """
        Get the validation record by id.

        Parameters
        ----------
        validation_id : str
            The ID of the CustomModelValidation for the deployment.

        Returns
        -------
        CustomModelValidation
        """

        url = f"{cls._client.domain}/{cls._path}/{validation_id}/"
        response = cls._client.get(url)
        return cls.from_server_data(response.json())

    @classmethod
    def get_by_values(
        cls, prompt_column_name: str, target_column_name: str, deployment_id: str, model_id: str
    ) -> CustomModelValidation:
        """
        Get the validation record by field values.

        Parameters
        ----------
        prompt_column_name : str
            The column name the deployed model expect as the input.
        target_column_name : str
            The target name deployed model will output.
        deployment_id : str
            ID of the deployment.
        model_id : str
            ID of the underlying deployment model.

        Returns
        -------
        CustomModelValidation
        """

        url = f"{cls._client.domain}/{cls._path}/"
        params = {
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": deployment_id,
            "model_id": model_id,
        }
        response = cls._client.get(url, params=params)
        return cls.from_server_data(response.json())

    @classmethod
    def create(
        cls,
        prompt_column_name: str,
        target_column_name: str,
        deployment_id: str,
        wait_for_completion: bool = False,
    ) -> CustomModelValidation:
        """
        Start the validation of deployment to serve as a vector database or LLM.

        Parameters
        ----------
        prompt_column_name : str
            The column name the deployed model expect as the input.
        target_column_name : str
            The target name that the deployed model will output.
        deployment_id : str
            ID of the deployment.
            The underlying model ID will be derived from the deployment info automatically.
        wait_for_completion : bool
            If set to True code will wait for the validation job to complete before
            returning the result (up to 10 minutes, raising timeout error after that).
            Otherwise, you can check current validation status by using
            CustomModelValidation.get with returned ID.

        Returns
        -------
        CustomModelValidation
        """

        payload = {
            "prompt_column_name": prompt_column_name,
            "target_column_name": target_column_name,
            "deployment_id": deployment_id,
        }
        url = f"{cls._client.domain}/{cls._path}/"
        response = cls._client.post(url, data=payload)
        if wait_for_completion:
            location = wait_for_async_resolution(cls._client, response.headers["Location"])
            return cls.from_location(location)
        return cls.from_server_data(response.json())

    @classmethod
    def revalidate(cls, validation_id: str) -> CustomModelValidation:
        """
        Revalidate an unlinked custom model vector database or LLM.
        This method is useful when a deployment used as vector database or LLM is accidentally
        replaced with another model that stopped complying with the vector database or LLM
        requirements. Replace the model back and call this method instead of creating a new
        custom model validation from scratch.
        Another use case for this is when the API token used to create a validation record
        got revoked and no longer can be used by vector database / LLM to call custom model
        deployment. Calling revalidate will update the validation record with the token
        currently in use.

        Parameters
        ----------
        validation_id : str
            The ID of the CustomModelValidation for revalidation.

        Returns
        -------
        CustomModelValidation
        """
        url = f"{cls._client.domain}/{cls._path}/{validation_id}/revalidate/"
        response = cls._client.post(url)
        return cls.from_server_data(response.json())
