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
"""Command for removing IAM policies for service accounts."""

import httplib

from googlecloudsdk.api_lib.iam import base_classes
from googlecloudsdk.api_lib.iam import utils
from googlecloudsdk.api_lib.util import http_retry
from googlecloudsdk.core.iam import iam_util


class RemoveIamPolicyBinding(base_classes.BaseIamCommand):
  """Remove an IAM policy for a Service Account."""

  detailed_help = iam_util.GetDetailedHelpForRemoveIamPolicyBinding(
      'service account', 'test@project.iam.gserviceaccounts.com')

  @staticmethod
  def Args(parser):
    parser.add_argument('address',
                        metavar='IAM-ADDRESS',
                        help='The IAM service account address whose policy to '
                        'remove from.')
    iam_util.AddArgsForRemoveIamPolicyBinding(parser)

  @utils.CatchServiceAccountErrors
  @http_retry.RetryOnHttpStatus(httplib.CONFLICT)
  def Run(self, args):
    self.SetAddress(args.address)
    policy = self.iam_client.v1.GetIamPolicy(
        self.messages.IamGetIamPolicyRequest(
            resource=utils.EmailToAccountResourceName(args.address)))

    iam_util.RemoveBindingFromIamPolicy(policy, args)

    return self.iam_client.v1.SetIamPolicy(
        self.messages.IamSetIamPolicyRequest(
            resource=utils.EmailToAccountResourceName(args.address),
            setIamPolicyRequest=self.messages.SetIamPolicyRequest(
                policy=policy)))