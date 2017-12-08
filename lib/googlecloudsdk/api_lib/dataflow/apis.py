# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helpers for interacting with the Cloud Dataflow API.
"""

from googlecloudsdk.api_lib.util import http_error_handler
from googlecloudsdk.core import apis
from googlecloudsdk.core import properties

DATAFLOW_API_NAME = 'dataflow'
DATAFLOW_API_VERSION = 'v1b3'


def GetMessagesModule():
  return apis.GetMessagesModule(DATAFLOW_API_NAME, DATAFLOW_API_VERSION)


def GetClientInstance():
  return apis.GetClientInstance(DATAFLOW_API_NAME, DATAFLOW_API_VERSION)


def GetProject():
  return properties.VALUES.core.project.Get(required=True)


class Jobs(object):
  """The Jobs set of Dataflow API functions."""

  GET_REQUEST = GetMessagesModule().DataflowProjectsJobsGetRequest
  LIST_REQUEST = GetMessagesModule().DataflowProjectsJobsListRequest
  UPDATE_REQUEST = GetMessagesModule().DataflowProjectsJobsUpdateRequest

  @staticmethod
  def GetService():
    return GetClientInstance().projects_jobs

  @staticmethod
  @http_error_handler.HandleHttpErrors
  def Get(job_id, project_id=None, view=None):
    """Calls the Dataflow Jobs.Get method.

    Args:
      job_id: Identifies a single job.
      project_id: The project which owns the job.
      view: (DataflowProjectsJobsGetRequest.ViewValueValuesEnum) Level of
        information requested in response.
    Returns:
      (Job)
    """
    project_id = project_id or GetProject()
    request = GetMessagesModule().DataflowProjectsJobsGetRequest(
        jobId=job_id, projectId=project_id, view=view)
    return Jobs.GetService().Get(request)

  @staticmethod
  @http_error_handler.HandleHttpErrors
  def Cancel(job_id, project_id=None):
    """Cancels a job by calling the Jobs.Update method.

    Args:
      job_id: Identifies a single job.
      project_id: The project which owns the job.
    Returns:
      (Job)
    """
    project_id = project_id or GetProject()
    job = GetMessagesModule().Job(requestedState=(GetMessagesModule(
    ).Job.RequestedStateValueValuesEnum.JOB_STATE_CANCELLED))
    request = GetMessagesModule().DataflowProjectsJobsUpdateRequest(
        jobId=job_id, projectId=project_id, job=job)
    return Jobs.GetService().Update(request)

  @staticmethod
  @http_error_handler.HandleHttpErrors
  def Drain(job_id, project_id=None):
    """Drains a job by calling the Jobs.Update method.

    Args:
      job_id: Identifies a single job.
      project_id: The project which owns the job.
    Returns:
      (Job)
    """
    project_id = project_id or GetProject()
    job = GetMessagesModule().Job(requestedState=(
        GetMessagesModule().Job.RequestedStateValueValuesEnum.JOB_STATE_DRAINED
    ))
    request = GetMessagesModule().DataflowProjectsJobsUpdateRequest(
        jobId=job_id, projectId=project_id, job=job)
    return Jobs.GetService().Update(request)


class Metrics(object):
  """The Metrics set of Dataflow API functions."""

  GET_REQUEST = GetMessagesModule().DataflowProjectsJobsGetMetricsRequest

  @staticmethod
  def GetService():
    return GetClientInstance().projects_jobs

  @staticmethod
  @http_error_handler.HandleHttpErrors
  def Get(job_id, project_id=None, start_time=None):
    """Calls the Dataflow Metrics.Get method.

    Args:
      job_id: The job to get messages for.
      project_id: The project which owns the job.
      start_time: Return only metric data that has changed since this time.
        Default is to return all information about all metrics for the job.
    Returns:
      (MetricUpdate)
    """
    project_id = project_id or GetProject()
    request = GetMessagesModule().DataflowProjectsJobsGetMetricsRequest(
        jobId=job_id, projectId=project_id, startTime=start_time)
    return Metrics.GetService().GetMetrics(request)


class Messages(object):
  """The Messages set of Dataflow API functions."""

  LIST_REQUEST = GetMessagesModule().DataflowProjectsJobsMessagesListRequest

  @staticmethod
  def GetService():
    return GetClientInstance().projects_jobs_messages

  @staticmethod
  @http_error_handler.HandleHttpErrors
  def List(job_id,
           project_id=None,
           minimum_importance=None,
           start_time=None,
           end_time=None,
           page_size=None,
           page_token=None):
    """Calls the Dataflow Metrics.Get method.

    Args:
      job_id: The job to get messages about.
      project_id: A project id.
      minimum_importance: Filter to only get messages with importance >= level
      start_time: If specified, return only messages with timestamps >=
        start_time. The default is the job creation time (i.e. beginning of
        messages).
      end_time: Return only messages with timestamps < end_time. The default is
        now (i.e. return up to the latest messages available).
      page_size: If specified, determines the maximum number of messages to
        return.  If unspecified, the service may choose an appropriate default,
        or may return an arbitrarily large number of results.
      page_token: If supplied, this should be the value of next_page_token
        returned by an earlier call. This will cause the next page of results to
        be returned.
    Returns:
      (ListJobMessagesResponse)
    """
    project_id = project_id or GetProject()
    request = GetMessagesModule().DataflowProjectsJobsMessagesListRequest(
        jobId=job_id,
        projectId=project_id,
        startTime=start_time,
        endTime=end_time,
        minimumImportance=minimum_importance,
        pageSize=page_size,
        pageToken=page_token)
    return Messages.GetService().List(request)