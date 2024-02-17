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

from datarobot._experimental.models.genai.custom_model_validation import CustomModelValidation


class CustomModelLLMValidation(CustomModelValidation):
    """
    Validation record checking the ability of the deployment to serve
    as a custom model LLM.

    Attributes
    ----------
    prompt_column_name : str
        The column name the deployed model expect as the input.
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
        Only available for deployments that passed validation. Dict fields:
        - prediction_api_url - URL for deployment prediction server.
        - datarobot_key - first of 2 auth headers for the prediction server.
        - authorization_header - second of 2 auth headers for the prediction server.
        - input_type - Either JSON or CSV - the input type that the model expects.
        - model_type - Target type of the deployed custom model.
    tenant_id : str
        Creating user's tenant ID.
    error_message : Optional[str]
        Additional information for errored validation.
    """

    _path = "api-gw/genai/customModelLLMValidations"

    def delete(self) -> None:
        """
        Delete the custom model LLM validation.
        """
        url = f"{self._client.domain}/{self._path}/{self.id}/"
        self._client.delete(url)
