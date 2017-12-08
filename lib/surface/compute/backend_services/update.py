# Copyright 2014 Google Inc. All Rights Reserved.
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
"""Commands for updating backend services.

   There are separate alpha, beta, and GA command classes in this file.
"""

from googlecloudsdk.api_lib.compute import backend_services_utils
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.third_party.apis.compute.alpha import compute_alpha_messages
from googlecloudsdk.third_party.apis.compute.beta import compute_beta_messages
from googlecloudsdk.third_party.apis.compute.v1 import compute_v1_messages
from googlecloudsdk.third_party.py27 import py27_copy as copy


def _Args(parser, messages):
  """Common arguments to create commands for each release track."""
  backend_services_utils.AddUpdatableArgs(
      parser,
      messages,
      default_protocol=None,
      default_timeout=None)

  parser.add_argument(
      'name',
      help='The name of the backend service to update.')


@base.ReleaseTracks(base.ReleaseTrack.GA)
class UpdateGA(base_classes.ReadWriteCommand):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    _Args(parser, compute_v1_messages)

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    return (
        self.service,
        'Get',
        self.messages.ComputeBackendServicesGetRequest(
            project=self.project,
            backendService=self.ref.Name()))

  def GetSetRequest(self, args, replacement, _):
    return (
        self.service,
        'Update',
        self.messages.ComputeBackendServicesUpdateRequest(
            project=self.project,
            backendService=self.ref.Name(),
            backendServiceResource=replacement))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    if args.description:
      replacement.description = args.description
    elif args.description is not None:
      replacement.description = None

    health_checks = backend_services_utils.GetHealthChecks(args, self)
    if health_checks:
      replacement.healthChecks = health_checks

    if args.timeout:
      replacement.timeoutSec = args.timeout

    if args.port:
      replacement.port = args.port

    if args.port_name:
      replacement.portName = args.port_name

    if args.protocol:
      replacement.protocol = (self.messages.BackendService
                              .ProtocolValueValuesEnum(args.protocol))

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        args.http_health_checks,
        args.https_health_checks,
        args.timeout is not None,
        args.port,
        args.port_name,
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateGA):
  """Update a backend service."""

  @staticmethod
  def AffinityOptions(backend_service):
    return sorted(backend_service.SessionAffinityValueValuesEnum.to_dict())

  @staticmethod
  def Args(parser):
    _Args(parser, compute_alpha_messages)

    connection_draining_timeout = parser.add_argument(
        '--connection-draining-timeout',
        type=int,
        default=None,  # None => use default value.
        help='Connection draining timeout in seconds.')
    connection_draining_timeout.detailed_help = """\
        Connection draining timeout, in seconds, to be used during removal of
        VMs from instance groups. This guarantees that for the specified time
        all existing connections to a VM will remain untouched, but no new
        connections will be accepted. Set timeout to zero to disable connection
        draining. Enable feature by specifying timeout up to one hour.
        Connection draining is disabled by default.
        """

    enable_cdn = parser.add_argument(
        '--enable-cdn',
        action='store_true',
        default=None,  # Tri-valued, None => don't change the setting.
        help='Enable cloud CDN.')
    enable_cdn.detailed_help = """\
        Enable Cloud CDN for the backend service. Cloud CDN can cache HTTP
        responses from a backend service at the edge of the network, close to
        users.
        """

    health_checks = parser.add_argument(
        '--health-checks',
        type=arg_parsers.ArgList(min_length=1),
        metavar='HEALTH_CHECK',
        action=arg_parsers.FloatingListValuesCatcher(),
        help=('Specifies a list of health check objects for checking the '
              'health of the backend service.'))
    health_checks.detailed_help = """\
        Specifies a list of health check objects for checking the health of
        the backend service. Health checks need not be for the same protocol
        as that of the backend service.
        """

    session_affinity = parser.add_argument(
        '--session-affinity',
        choices=UpdateAlpha.AffinityOptions(
            compute_alpha_messages.BackendService),
        type=lambda x: x.upper(),
        default=None,
        help='The type of session affinity to use.')
    session_affinity.detailed_help = """\
        The type of session affinity to use for this backend service.  Possible
        values are:

          * none: Session affinity is disabled.
          * client_ip: Route requests to instances based on the hash of the
            client's IP address.
          * generated_cookie: Route requests to instances based on the contents
            of the "GCLB" cookie set by the load balancer.
        """

    affinity_cookie_ttl = parser.add_argument(
        '--affinity-cookie-ttl',
        type=int,
        default=None,
        help=('TTL in seconds of the GCLB cookie, if any'))
    affinity_cookie_ttl.detailed_helpr = """\
        If generated_cookie session affinity is in use, set the TTL of the
        resulting cookie.  A setting of 0 indicates that the cookie should
        be transient.
        """

  def Modify(self, args, existing):
    replacement = super(UpdateAlpha, self).Modify(args, existing)

    if args.connection_draining_timeout is not None:
      replacement.connectionDraining = self.messages.ConnectionDraining(
          drainingTimeoutSec=args.connection_draining_timeout)

    if args.enable_cdn is not None:
      replacement.enableCDN = args.enable_cdn

    if args.session_affinity is not None:
      replacement.sessionAffinity = (
          self.messages.BackendService.SessionAffinityValueValuesEnum(
              args.session_affinity))

    if args.affinity_cookie_ttl is not None:
      replacement.affinityCookieTtlSec = args.affinity_cookie_ttl

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        getattr(args, 'health_checks', None),
        args.http_health_checks,
        getattr(args, 'https_health_checks', None),
        args.timeout is not None,
        args.port,
        args.port_name,
        args.connection_draining_timeout is not None,
        args.enable_cdn is not None,
        args.session_affinity is not None,
        args.affinity_cookie_ttl is not None
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(UpdateGA):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    _Args(parser, compute_beta_messages)

    enable_cdn = parser.add_argument(
        '--enable-cdn',
        action='store_true',
        default=None,  # Tri-valued, None => don't change the setting.
        help='Enable cloud CDN.')
    enable_cdn.detailed_help = """\
        Enable Cloud CDN for the backend service. Cloud CDN can cache HTTP
        responses from a backend service at the edge of the network, close to
        users.
        """

  def Modify(self, args, existing):
    replacement = super(UpdateBeta, self).Modify(args, existing)

    if args.enable_cdn is not None:
      replacement.enableCDN = args.enable_cdn

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        args.http_health_checks,
        args.https_health_checks,
        args.timeout is not None,
        args.port,
        args.port_name,
        args.enable_cdn is not None,
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(UpdateGA, self).Run(args)


UpdateGA.detailed_help = {
    'brief': 'Update a backend service',
    'DESCRIPTION': """
        *{command}* is used to update backend services.
        """,
}
UpdateAlpha.detailed_help = UpdateGA.detailed_help
UpdateBeta.detailed_help = UpdateGA.detailed_help
