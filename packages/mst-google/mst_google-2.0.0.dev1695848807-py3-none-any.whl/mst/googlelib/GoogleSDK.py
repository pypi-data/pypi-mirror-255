from mst.core.local_env import local_env
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.api_core import retry, exceptions


class GoogleSDK:
    """Provides a wrapper around the Google Admin SDK API. May be subclassed to access specific resources."""

    if local_env() != "prod":
        user_domain = "qa-um.umsystem.edu"
        group_domain = "grp.gtest.umsystem.edu"
    else:
        user_domain = "umsystem.edu"
        group_domain = "grp.umsystem.edu"

    default_api = "admin"
    default_version = "directory_v1"
    default_scopes = (
        "https://www.googleapis.com/auth/admin.directory.group",
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
    )

    def __init__(self, api=default_api, version=default_version, scopes=default_scopes):
        self.api = api
        self.version = version
        self.scopes = scopes

    @property
    def scoped_credentials(self):
        if self.scopes:
            return GoogleSDK.credentials.with_scopes(self.scopes)
        return GoogleSDK.credentials

    @classmethod
    def init(cls, google_json, user):
        subject = f"{user}@{cls.user_domain}"
        cls.credentials = service_account.Credentials.from_service_account_info(
            google_json, subject=subject
        )

    def build(self):
        return build(
            self.api,
            self.version,
            credentials=self.scoped_credentials,
            cache_discovery=False,
        )

    def retry(method):
        retryable_exceptions = (
            exceptions.Aborted,
            exceptions.AlreadyExists,
            exceptions.BadGateway,
            exceptions.BadRequest,
            exceptions.Cancelled,
            exceptions.Conflict,
            exceptions.DataLoss,
            exceptions.DeadlineExceeded,
            exceptions.FailedPrecondition,
            exceptions.Forbidden,
            exceptions.GatewayTimeout,
            exceptions.InternalServerError,
            exceptions.InvalidArgument,
            exceptions.LengthRequired,
            exceptions.MethodNotAllowed,
            exceptions.MethodNotImplemented,
            exceptions.MovedPermanently,
            exceptions.NotModified,
            exceptions.OutOfRange,
            exceptions.PermissionDenied,
            exceptions.PreconditionFailed,
            exceptions.RequestRangeNotSatisfiable,
            exceptions.ResourceExhausted,
            exceptions.ResumeIncomplete,
            exceptions.RetryError,
            exceptions.ServerError,
            exceptions.ServiceUnavailable,
            exceptions.TemporaryRedirect,
            exceptions.TooManyRequests,
            exceptions.Unauthenticated,
            exceptions.Unauthorized,
            exceptions.Unknown,
        )

        @retry.Retry(
            predicate=retry.if_exception_type(retryable_exceptions),
            initial=1,
            maximum=5,
            timeout=30,
        )
        def wrapper(*args, **kwargs):
            return_object = method(*args, **kwargs)
            return return_object

        return wrapper
