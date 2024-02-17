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

from datetime import datetime
from io import IOBase
import time
from typing import Any, Dict, List, Optional, Union

from mypy_extensions import TypedDict
from pytz import utc
import trafaret as t

from datarobot._experimental.models.enums import (
    NotebookPermissions,
    NotebookStatus,
    NotebookType,
    RunType,
    ScheduledRunStatus,
)
from datarobot.mixins.browser_mixin import BrowserMixin
from datarobot.models.api_object import APIObject
from datarobot.models.use_cases.utils import resolve_use_cases, UseCaseLike
from datarobot.utils import assert_single_parameter
from datarobot.utils.pagination import unpaginate


class ManualRunPayload(TypedDict, total=False):
    notebook_id: str
    title: Optional[str]
    parameters: Optional[List[Dict[str, str]]]


notebook_user_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("activated"): t.Bool,
        t.Key("username"): t.String,
        t.Key("first_name"): t.String,
        t.Key("last_name"): t.String,
        t.Key("gravatar_hash", optional=True): t.String,
    }
).ignore_extra("*")


notebook_activity_trafaret = t.Dict(
    {
        t.Key("at"): t.String,
        t.Key("by"): notebook_user_trafaret,
    }
)


notebook_settings_trafaret = t.Dict(
    {
        t.Key("show_line_numbers"): t.Bool,
        t.Key("hide_cell_titles"): t.Bool,
        t.Key("hide_cell_outputs"): t.Bool,
        t.Key("show_scrollers"): t.Bool,
    }
)


notebook_session_trafaret = t.Dict(
    {
        t.Key("status"): t.String,
        t.Key("notebook_id"): t.String,
        t.Key("started_at", optional=True): t.String,
    }
)

scheduled_job_param_trafaret = t.Dict({t.Key("name"): t.String, t.Key("value"): t.String})


scheduled_job_payload_trafaret = t.Dict(
    {
        t.Key("uid"): t.String,
        t.Key("org_id"): t.String,
        t.Key("use_case_id"): t.String,
        t.Key("notebook_id"): t.String,
        t.Key("notebook_name"): t.String,
        t.Key("run_type"): t.String,
        t.Key("parameters"): t.List(scheduled_job_param_trafaret),
    }
)


revision_metadata_trafaret = t.Dict(
    {
        t.Key("id", optional=True): t.String,
        t.Key("name", optional=True): t.String,
    }
)


# TODO: [NB-4787] We are using trafaret's "ignore_extra" very liberally and this is a small subset of properties
notebook_scheduled_run_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("use_case_id"): t.String,
        t.Key("status"): t.String,
        t.Key("payload"): scheduled_job_payload_trafaret,
        t.Key("duration", optional=True): t.Int,
        t.Key("run_type", optional=True): t.String,
        t.Key("revision"): revision_metadata_trafaret,
    }
).ignore_extra("*")


# TODO: [NB-4787] We are using trafaret's "ignore_extra" very liberally and this is a small subset of properties
notebook_scheduled_job_trafaret = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("enabled"): t.Bool,
        t.Key("job_payload"): scheduled_job_payload_trafaret,
        t.Key("title", optional=True): t.String,
        t.Key("schedule", optional=True): t.String,
    }
).ignore_extra("*")


class NotebookUser(APIObject):
    """
    A user associated with a Notebook.

    Attributes
    ----------

    id : str
        The ID of the user.
    activated: bool
        Whether or not the user is enabled.
    username : str
        The username of the user, usually their email address.
    first_name : str
        The first name of the user.
    last_name : str
        The last name of the user.
    gravatar_hash : Optional[str]
        The gravatar hash of the user. Optional.
    tenant_phase : Optional[str]
        The phase that the user's tenant is in. Optional.
    """

    _converter = notebook_user_trafaret

    def __init__(
        self,
        id: str,
        activated: bool,
        username: str,
        first_name: str,
        last_name: str,
        gravatar_hash: Optional[str] = None,
        tenant_phase: Optional[str] = None,
    ):
        self.id = id
        self.activated = activated
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.gravatar_hash = gravatar_hash
        self.tenant_phase = tenant_phase


class NotebookSession(APIObject):
    """
    Information about the current status of a Notebook.

    Attributes
    ----------

    status : NotebookStatus
        The current status of the Notebook kernel.
    notebook_id : str
        The ID of the Notebook.
    started_at : Optional[str]
        The date and time when the notebook was started. Optional.
    """

    _converter = notebook_session_trafaret

    def __init__(self, status: NotebookStatus, notebook_id: str, started_at: Optional[str] = None):
        self.status = status
        self.notebook_id = notebook_id
        self.started_at = started_at


class NotebookActivity(APIObject):
    """
    A record of activity (i.e. last run, updated, etc.) in a Notebook.

    Attributes
    ----------

    at : str
        The time of the activity in the notebook.
    by : NotebookUser
        The user who performed the activity.
    """

    _converter = notebook_activity_trafaret

    def __init__(self, at: str, by: Dict[str, str]):
        self.at = at
        self.by = NotebookUser.from_server_data(by)


class NotebookSettings(APIObject):
    """
    Settings for a DataRobot Notebook.

    Attributes
    ----------

    show_line_numbers : bool
        Whether line numbers in cells should be displayed.
    hide_cell_titles : bool
        Whether cell titles should be displayed.
    hide_cell_outputs : bool
        Whether the cell outputs should be displayed.
    show_scrollers : bool
        Whether scrollbars should be shown on cells.
    """

    _converter = notebook_settings_trafaret

    def __init__(
        self,
        show_line_numbers: bool,
        hide_cell_titles: bool,
        hide_cell_outputs: bool,
        show_scrollers: bool,
    ):
        self.show_line_numbers = show_line_numbers
        self.hide_cell_titles = hide_cell_titles
        self.hide_cell_outputs = hide_cell_outputs
        self.show_scrollers = show_scrollers


class RevisionMetadata(APIObject):
    """
    DataRobot Notebook Revision Metadata.

    Attributes
    ----------

    id : str
        The ID of the Notebook Revision. Optional.
    name : str
        The name of the Notebook Revision. Optional.
    """

    _converter = revision_metadata_trafaret

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None):
        self.id = id
        self.name = name


class NotebookScheduledRun(APIObject):
    """
    DataRobot Notebook Scheduled Run.

    Attributes
    ----------

    id : str
        The ID of the Notebook Scheduled Job.
    use_case_id : str
        The Use Case ID of the Notebook Scheduled Job.
    status : str
        The status of the run.
    payload : ScheduledJobPayload
        The payload used for the background job.
    revision : RevisionMetadata
        Notebook revision data - ID and name.
    duration : Optional[int]
        The job duration in seconds. May be None for example while the job is running. Optional.
    run_type : Optional[RunType]
        The type of the run - either manual (triggered via UI or API) or scheduled. Optional.
    """

    _converter = notebook_scheduled_run_trafaret

    def __init__(
        self,
        id: str,
        use_case_id: str,
        status: ScheduledRunStatus,
        payload: Dict[str, Union[str, List[Dict[str, str]]]],
        revision: Dict[str, Optional[str]],
        duration: Optional[int] = None,
        run_type: Optional[RunType] = None,
    ):
        self.id = id
        self.use_case_id = use_case_id
        self.status = status
        self.payload = ScheduledJobPayload.from_server_data(payload)
        self.revision = RevisionMetadata.from_server_data(revision)
        self.duration = duration
        self.run_type = run_type


class ScheduledJobParam(APIObject):
    """
    DataRobot Schedule Job Parameter.

    Attributes
    ----------

    name : str
        The name of the parameter.
    value : str
        The value of the parameter.
    """

    _converter = scheduled_job_param_trafaret

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class ScheduledJobPayload(APIObject):
    """
    DataRobot Schedule Job Payload.

    Attributes
    ----------

    uid : str
        The ID of the user who created the Notebook Schedule.
    org_id : str
        The ID of the user's organization who created the Notebook Schedule.
    use_case_id : str
        The ID of the Use Case that the Notebook belongs to.
    notebook_id : str
        The ID of Notebook being run on a schedule.
    notebook_name : str
        The name of Notebook being run on a schedule.
    run_tpye : str
        The type of the run - either manual (triggered via UI or API) or scheduled.
    parameters : List[ScheduledJobParam]
        The parameters being used in the Notebook Schedule. Can be an empty list.
    """

    _converter = scheduled_job_payload_trafaret

    def __init__(
        self,
        uid: str,
        org_id: str,
        use_case_id: str,
        notebook_id: str,
        notebook_name: str,
        run_type: RunType,
        parameters: List[Dict[str, str]],
    ):
        self.uid = uid
        self.org_id = org_id
        self.use_case_id = use_case_id
        self.notebook_id = notebook_id
        self.notebook_name = notebook_name
        self.run_type = run_type
        self.parameters = [ScheduledJobParam.from_server_data(param) for param in parameters]


class NotebookScheduledJob(APIObject):
    """
    DataRobot Notebook Schedule.

    Attributes
    ----------

    id : str
        The ID of the Notebook Scheduled Job.
    enabled : bool
        Whether job is enabled or not.
    job_payload : ScheduledJobPayload
        The payload used for the background job.
    title : Optional[str]
        The title of the job. Optional.
    schedule : Optional[str]
        Cron-like string to define how frequently job should be run. Optional.
    """

    _path = "api-gw/nbx/scheduling/"

    _converter = notebook_scheduled_job_trafaret

    def __init__(
        self,
        id: str,
        enabled: bool,
        job_payload: Dict[str, Union[str, List[Dict[str, str]]]],
        title: Optional[str] = None,
        schedule: Optional[str] = None,
    ):
        self.id = id
        self.enabled = enabled
        self.job_payload = ScheduledJobPayload.from_server_data(job_payload)
        self.title = title
        self.schedule = schedule

    @property
    def use_case_id(self) -> str:
        return self.job_payload.use_case_id

    @classmethod
    def get(cls, use_case_id: str, scheduled_job_id: str) -> NotebookScheduledJob:
        """
        Retrieve a single notebook schedule.

        Parameters
        ----------
        scheduled_job_id : str
            The ID of the notebook schedule you want to retrieve.

        Returns
        -------
        notebook_schedule : NotebookScheduledJob
            The requested notebook schedule.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import NotebookScheduledJob

            notebook_schedule = NotebookScheduledJob.get(
                use_case_id="654ad653c6c1e889e8eab12e",
                scheduled_job_id="65734fe637157200e28bf688",
            )
        """
        url = f"{cls._client.domain}/{cls._path}{scheduled_job_id}/"
        r_data = cls._client.get(url, params={"use_case_id": use_case_id})
        return NotebookScheduledJob.from_server_data(r_data.json())

    def get_job_history(self) -> List[NotebookScheduledRun]:
        """
        Retrieve list of historical runs for the notebook schedule.

        Returns
        -------
        notebook_scheduled_runs : List[NotebookScheduledRun]
            The list of historical runs for the notebook schedule.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import NotebookScheduledJob

            notebook_schedule = NotebookScheduledJob.get(
                use_case_id="654ad653c6c1e889e8eab12e",
                scheduled_job_id="65734fe637157200e28bf688",
            )
            notebook_scheduled_runs = notebook_schedule.get_job_history()
        """
        url = f"{self._client.domain}/{self._path}/runHistory/"
        params = {
            "use_case_id": self.use_case_id,
            "job_ids": self.id,
        }
        r_data = unpaginate(url, params, self._client)
        return [NotebookScheduledRun.from_server_data(data) for data in r_data]

    def wait_for_completion(self, max_wait: int = 600) -> str:
        """
        Retrieve a single notebook.

        Parameters
        ----------
        max_wait : int
            The number of seconds to wait before giving up.

        Returns
        -------
        revision_id : str
            Returns either revision ID or message describing current state.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebook = Notebook.get(notebook_id='6556b00dcc4ea0bb7ea48121')
            manual_run = notebook.run()
            revision_id = manual_run.wait_for_completion()
        """
        status = None
        start_time = time.time()
        while (
            status not in ScheduledRunStatus.terminal_statuses()
            and time.time() < start_time + max_wait
        ):
            job_history = self.get_job_history()
            if job_history:
                job_run = job_history[0]
                status = job_run.status
            time.sleep(5)
        if status in ScheduledRunStatus.terminal_statuses():
            if job_run.revision and job_run.revision.id:
                return job_run.revision.id
            else:
                return f"Revision ID not available for notebook schedule with status: {status}"
        else:
            return f"Notebook schedule has not yet completed. Its current status: {status}"


class Notebook(APIObject, BrowserMixin):
    """
    Metadata for a DataRobot Notebook accessible to the user.

    Attributes
    ----------

    id : str
        The ID of the Notebook.
    name : str
        The name of the Notebook.
    type : NotebookType
        The type of the Notebook. Can be "plain" or "codespace".
    permissions : List[NotebookPermission]
        The permissions the user has for the Notebook.
    tags : List[str]
        Any tags that have been added to the Notebook. Default is an empty list.
    created : NotebookActivity
        Information on when the Notebook was created and who created it.
    updated : NotebookActivity
        Information on when the Notebook was updated and who updated it.
    last_viewed : NotebookActivity
        Information on when the Notebook was last viewed and who viewed it.
    settings : NotebookSettings
        Information on global settings applied to the Notebook.
    org_id : Optional[str]
        The organization ID associated with the Notebook.
    tenant_id : Optional[str]
        The tenant ID associated with the Notebook.
    description : Optional[str]
        The description of the Notebook. Optional.
    session : Optional[NotebookSession]
        Metadata on the current status of the Notebook and its kernel. Optional.
    use_case_id : Optional[str]
        The ID of the Use Case the Notebook is associated with. Optional.
    has_enabled_schedule : bool
        Whether or not the notebook has a currently enabled schedule.
    """

    _notebooks_path = "api-gw/nbx/notebooks/"
    _orchestrator_path = "api-gw/nbx/orchestrator/"
    _scheduling_path = "api-gw/nbx/scheduling/"
    _revisions_path = "api-gw/nbx/notebookRevisions/"

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("name"): t.String,
            t.Key("type"): t.Enum(*NotebookType.all()),
            t.Key("description", optional=True): t.Or(t.String, t.Null),
            t.Key("permissions"): t.List(t.String),
            t.Key("tags"): t.List(t.String),
            t.Key("created"): notebook_activity_trafaret,
            t.Key("updated", optional=True): notebook_activity_trafaret,
            t.Key("last_viewed"): notebook_activity_trafaret,
            t.Key("settings"): notebook_settings_trafaret,
            t.Key("org_id", optional=True): t.Or(t.String, t.Null),
            t.Key("tenant_id", optional=True): t.Or(t.String, t.Null),
            t.Key("session", optional=True): t.Or(notebook_session_trafaret, t.Null),
            t.Key("use_case_id", optional=True): t.Or(t.String, t.Null),
            t.Key("has_enabled_schedule"): t.Bool,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id: str,
        name: str,
        type: NotebookType,
        permissions: List[str],
        tags: List[str],
        created: Dict[str, Any],
        last_viewed: Dict[str, Any],
        settings: Dict[str, bool],
        has_enabled_schedule: bool,
        updated: Optional[Dict[str, Any]] = None,
        org_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        description: Optional[str] = None,
        session: Optional[Dict[str, str]] = None,
        use_case_id: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.description = description
        self.permissions = [NotebookPermissions[permission] for permission in permissions]
        self.tags = tags
        self.created = NotebookActivity.from_server_data(created)
        self.updated = updated if not updated else NotebookActivity.from_server_data(updated)
        self.last_viewed = (
            last_viewed if not last_viewed else NotebookActivity.from_server_data(last_viewed)
        )
        self.settings = NotebookSettings.from_server_data(settings)
        self.org_id = org_id
        self.tenant_id = tenant_id
        self.session = NotebookSession.from_server_data(session) if session else session
        self.use_case_id = use_case_id
        self.has_enabled_schedule = has_enabled_schedule

    def get_uri(self) -> str:
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to this Notebook in its Use Case or standalone.
        """
        if self.use_case_id:
            return f"{self._client.domain}/usecases/{self.use_case_id}/notebooks/{self.id}"
        else:
            return f"{self._client.domain}/notebooks/{self.id}"

    @classmethod
    def get(cls, notebook_id: str) -> Notebook:
        """
        Retrieve a single notebook.

        Parameters
        ----------
        notebook_id : str
            The ID of the notebook you want to retrieve.

        Returns
        -------
        notebook : Notebook
            The requested notebook.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebook = Notebook.get(notebook_id='6556b00dcc4ea0bb7ea48121')
        """
        url = f"{cls._client.domain}/{cls._notebooks_path}{notebook_id}/"
        r_data = cls._client.get(url)
        return Notebook.from_server_data(r_data.json())

    def download_revision(
        self,
        revision_id: str,
        file_path: Optional[str] = None,
        filelike: Optional[IOBase] = None,
    ) -> None:
        """
        Downloads the notebook as a JSON (.ipynb) file for the specified revision.

        Parameters
        ----------
        file_path: string, optional
            The destination to write the file to.
        filelike: file, optional
            A file-like object to write to.  The object must be able to write bytes. The user is
            responsible for closing the object.

        Returns
        -------
        None

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebook = Notebook.get(notebook_id='6556b00dcc4ea0bb7ea48121')
            manual_run = notebook.run()
            revision_id = manual_run.wait_for_completion()
            notebook.download_revision(revision_id=revision_id, file_path="./results.ipynb")
        """
        assert_single_parameter(("filelike", "file_path"), filelike, file_path)

        response = self._client.get(
            f"{self._client.domain}/{self._revisions_path}{self.id}/{revision_id}/toFile/"
        )
        if file_path:
            with open(file_path, "wb") as f:
                f.write(response.content)
        if filelike:
            filelike.write(response.content)

    def delete(self) -> None:
        """
        Delete a single notebook

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebook = Notebook.get(notebook_id='6556b00dcc4ea0bb7ea48121')
            notebook.delete()
        """
        url = f"{self._client.domain}/{self._notebooks_path}{self.id}/"
        self._client.delete(url)

    @classmethod
    def list(
        cls,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        order_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        owners: Optional[List[str]] = None,
        query: Optional[str] = None,
        use_cases: Optional[UseCaseLike] = None,
    ) -> List[Notebook]:
        """
        List all Notebooks available to the user.

        Parameters
        ----------
        created_before : Optional[str]
            List Notebooks created before a certain date. Optional.
        created_after : Optional[str]
            List Notebooks created after a certain date. Optional.
        order_by : Optional[str]
            Property to sort returned Notebooks. Optional.
            Supported properties are "name", "created", "updated", "tags", and "lastViewed".
            Prefix the attribute name with a dash to sort in descending order,
            e.g. order_by='-created'.
            By default, the order_by parameter is None.
        tags : Optional[List[str]]
            A list of tags that returned Notebooks should be associated with. Optional.
        owners : Optional[List[str]]
            A list of user IDs used to filter returned Notebooks.
            The respective users share ownership of the Notebooks. Optional.
        query : Optional[str]
            A specific regex query to use when filtering Notebooks. Optional.
        use_cases : Optional[UseCase or List[UseCase] or str or List[str]]
            Filters returned Notebooks by a specific Use Case or Cases. Accepts either the entity or the ID. Optional.
            If set to [None], the method filters the notebook's datasets by those not linked to a UseCase.

        Returns
        -------
        notebooks : List[Notebook]
            A list of Notebooks available to the user.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebooks = Notebook.list()
        """
        params = {
            "created_before": created_before,
            "created_after": created_after,
            "order_by": order_by,
            "tags": tags,
            "owners": owners,
            "query": query,
        }
        params = resolve_use_cases(use_cases=use_cases, params=params, use_case_key="use_case_id")
        url = f"{cls._client.domain}/{cls._notebooks_path}"
        r_data = unpaginate(url, params, cls._client)
        return [Notebook.from_server_data(data) for data in r_data]

    def run(
        self,
        title: Optional[str] = None,
        parameters: Optional[List[Dict[str, str]]] = None,
    ) -> NotebookScheduledJob:
        """
        Create a manual scheduled job that runs the notebook.

        Notes
        -----
        The notebook must be part of a Use Case.

        Parameters
        ----------
        title : Optional[str]
            The title of the background job. Optional.
        parameters : Optional[List[Dict[str, str]]]
            A list of dictionaries of key value pairs representing environment variables predefined
            in the notebook. Optional.

        Returns
        -------
        notebook_scheduled_job : NotebookScheduledJob
            The created notebook schedule job.

        Examples
        --------
        .. code-block:: python

            from datarobot._experimental.models.notebooks import Notebook

            notebook = Notebook.get(notebook_id='6556b00dcc4ea0bb7ea48121')
            manual_run = notebook.run()

            # Alternatively, with title and parameters:
            # manual_run = notebook_scheduled_job = notebook.run(title="My Run", parameters=[{"FOO": "bar"}])

            revision_id = manual_run.wait_for_completion()
        """
        url = f"{self._client.domain}/{self._scheduling_path}manualRun/"
        payload: ManualRunPayload = {
            "notebook_id": self.id,
            "title": title
            if title
            else f"{self.name} {datetime.now(tz=utc).strftime('%Y-%m-%d %H:%M (UTC)')}",
        }
        if parameters:
            payload["parameters"] = parameters

        r_data = self._client.post(url, data=payload)
        return NotebookScheduledJob.from_server_data(r_data.json())
