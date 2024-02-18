# This script is used to create a session to fetch csrftoken , sessionid in basic_auth.py to avoid basic authentication
import copy
import logging
import os
import sys
import time
from datetime import datetime
from datetime import timedelta
from ssl import SSLError

from requests import ConnectionError
from requests import Response
from requests.exceptions import ChunkedEncodingError
from requests.sessions import Session


logger = logging.getLogger(__name__)

global sessionDict
sessionDict = {}


def avi_timedelta(td):
    """
    This is a wrapper class to workaround python 2.6 builtin datetime.timedelta
    does not have total_seconds method
    :param td timedelta object
    """
    if type(td) != timedelta:
        raise TypeError()
    if sys.version_info >= (2, 7):
        ts = td.total_seconds()
    else:
        ts = td.seconds + (24 * 3600 * td.days)
    return ts


class ObjectNotFound(Exception):
    pass


class APIError(Exception):
    def __init__(self, arg, rsp=None):
        self.args = [arg, rsp]
        self.rsp = rsp


class AviServerError(APIError):
    def __init__(self, arg, rsp=None):
        super().__init__(arg, rsp)


class AviMultipartUploadError(Exception):
    def __init__(self, arg, rsp=None):
        self.args = [arg]
        self.rsp = rsp


class ApiResponse(Response):
    """
    Returns copy of the requests.Response object provides additional helper
    routines
        1. obj: returns dictionary of Avi Object
    """

    def __init__(self, rsp):
        super().__init__()
        for k, v in list(rsp.__dict__.items()):
            setattr(self, k, v)

    def json(self):
        """
        Extends the session default json interface to handle special errors
        and raise Exceptions
        returns the Avi object as a dictionary from rsp.text
        """
        if self.status_code > 199 and self.status_code < 300:
            if not self.text:
                # In cases like status_code == 201 the response text could be
                # empty string.
                return None
            return super().json()
        elif self.status_code == 404:
            raise ObjectNotFound(
                "HTTP Error: %d Error Msg %s" % (self.status_code, self.text), self
            )
        elif self.status_code >= 500:
            raise AviServerError(
                "HTTP Error: %d Error Msg %s" % (self.status_code, self.text), self
            )
        else:
            raise APIError(
                "HTTP Error: %d Error Msg %s" % (self.status_code, self.text), self
            )

    @staticmethod
    def to_avi_response(resp):
        if type(resp) == Response:
            return ApiResponse(resp)
        return resp


class AviCredentials:
    controller = ""
    username = ""
    password = ""
    api_version = "18.2.6"
    tenant = None
    tenant_uuid = None
    token = None
    port = None
    timeout = 300
    session_id = None
    csrftoken = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ApiSession(Session):
    """
    Extends the Request library's session object to provide helper
    utilities to work with Avi Controller like authentication, api massaging
    etc.
    """

    # This keeps track of the process which created the cache.
    # At anytime the pid of the process changes then it would create
    # a new cache for that process.
    SESSION_CACHE_EXPIRY = 20 * 60
    SHARED_USER_HDRS = ["X-CSRFToken", "Session-Id", "Referer", "Content-Type"]
    MAX_API_RETRIES = 3

    def __init__(
        self,
        controller_ip=None,
        username=None,
        password=None,
        token=None,
        tenant=None,
        tenant_uuid=None,
        verify=False,
        port=None,
        timeout=60,
        api_version=None,
        retry_conxn_errors=True,
        data_log=False,
        avi_credentials=None,
        session_id=None,
        csrftoken=None,
        lazy_authentication=False,
        max_api_retries=None,
        user_hdrs={},
    ):
        """
         ApiSession takes ownership of avi_credentials and may update the
         information inside it.

        Initialize new session object with authenticated token from login api.
        It also keeps a cache of user sessions that are cleaned up if inactive
        for more than 20 mins.

        Notes:
        01. If mode is https and port is none or 443, we don't embed the
            port in the prefix.
        02. If mode is http and the port is none or 80, we don't embed the
            port in the prefix.
        """

        super().__init__()
        logger.debug(
            "Creating session with following values:\n "
            "controller_ip: %s, username: %s, tenant: %s, "
            "tenant_uuid: %s, verify: %s, port: %s, timeout: %s, "
            "api_version: %s, retry_conxn_errors: %s, data_log: %s,"
            "avi_credentials: %s, session_id: %s, csrftoken: %s,"
            "lazy_authentication: %s, max_api_retries: %s"
            % (
                controller_ip,
                username,
                tenant,
                tenant_uuid,
                verify,
                port,
                timeout,
                api_version,
                retry_conxn_errors,
                data_log,
                avi_credentials,
                session_id,
                csrftoken,
                lazy_authentication,
                max_api_retries,
            )
        )
        if not avi_credentials:
            tenant = tenant if tenant else "admin"
            self.avi_credentials = AviCredentials(
                controller=controller_ip,
                username=username,
                password=password,
                api_version=api_version,
                tenant=tenant,
                tenant_uuid=tenant_uuid,
                token=token,
                port=port,
                timeout=timeout,
                session_id=session_id,
                csrftoken=csrftoken,
            )
        else:
            self.avi_credentials = avi_credentials
        self.headers = {}
        self.verify = verify
        self.retry_conxn_errors = retry_conxn_errors
        self.remote_api_version = {}
        self.user_hdrs = user_hdrs
        self.data_log = data_log
        self.num_session_retries = 0
        self.num_api_retries = 0
        self.retry_wait_time = 0
        self.max_session_retries = (
            self.MAX_API_RETRIES if max_api_retries is None else int(max_api_retries)
        )
        # Refer Notes 01 and 02
        k_port = port if port else 443
        if self.avi_credentials.controller.startswith("http"):
            k_port = 80 if not self.avi_credentials.port else k_port
            if self.avi_credentials.port is None or self.avi_credentials.port == 80:
                self.prefix = self.avi_credentials.controller
            else:
                self.prefix = "{x}:{y}".format(
                    x=self.avi_credentials.controller, y=self.avi_credentials.port
                )
        else:
            if port is None or port == 443:
                self.prefix = f"https://{self.avi_credentials.controller}"
            else:
                self.prefix = "https://{x}:{y}".format(
                    x=self.avi_credentials.controller, y=self.avi_credentials.port
                )
        self.timeout = timeout
        self.key = "{}:{}:{}".format(
            self.avi_credentials.controller, self.avi_credentials.username, k_port
        )

        if self.user_hdrs and "Authorization" in self.user_hdrs:
            return
        # Added api token and session id to sessionDict for handle single
        # session
        if self.avi_credentials.csrftoken:
            sessionDict[self.key] = {
                "api": self,
                "csrftoken": self.avi_credentials.csrftoken,
                "session_id": self.avi_credentials.session_id,
                "last_used": datetime.utcnow(),
            }
        else:
            self.authenticate_session()
        self.num_session_retries = 0
        self.pid = os.getpid()
        ApiSession._clean_inactive_sessions()
        return

    @staticmethod
    def get_session(
        controller_ip=None,
        username=None,
        password=None,
        token=None,
        tenant=None,
        tenant_uuid=None,
        verify=False,
        port=None,
        timeout=60,
        retry_conxn_errors=True,
        api_version=None,
        data_log=False,
        avi_credentials=None,
        session_id=None,
        csrftoken=None,
        lazy_authentication=False,
        max_api_retries=None,
        user_hdrs=None,
    ):
        """
        returns the session object for same user and tenant
        calls init if session dose not exist and adds it to session cache
        :param controller_ip: controller IP address
        :param username:
        :param password:
        :param token: Token to use; example, a valid keystone token
        :param tenant: Name of the tenant on Avi Controller
        :param tenant_uuid: Don't specify tenant when using tenant_id
        :param port: Rest-API may use a different port other than 443
        :param timeout: timeout for API calls; Default value is 60 seconds
        :param retry_conxn_errors: retry on connection errors
        :param api_version: Controller API version
        """

        if max_api_retries == 0:
            max_api_retries = 1

        if not avi_credentials:
            tenant = tenant if tenant else "admin"
            avi_credentials = AviCredentials(
                controller=controller_ip,
                username=username,
                password=password,
                api_version=api_version,
                tenant=tenant,
                tenant_uuid=tenant_uuid,
                token=token,
                port=port,
                timeout=timeout,
                session_id=session_id,
                csrftoken=csrftoken,
            )

        k_port = avi_credentials.port if avi_credentials.port else 443
        if avi_credentials.controller.startswith("http"):
            k_port = 80 if not avi_credentials.port else k_port
        key = "{}:{}:{}".format(
            avi_credentials.controller, avi_credentials.username, k_port
        )
        cached_session = sessionDict.get(key)
        if cached_session:
            user_session = cached_session["api"]
            if not (user_session.avi_credentials.csrftoken or lazy_authentication):
                user_session.authenticate_session()
        else:
            user_session = ApiSession(
                controller_ip,
                username,
                password,
                token=token,
                tenant=tenant,
                tenant_uuid=tenant_uuid,
                verify=verify,
                port=port,
                timeout=timeout,
                retry_conxn_errors=retry_conxn_errors,
                api_version=api_version,
                data_log=data_log,
                avi_credentials=avi_credentials,
                lazy_authentication=lazy_authentication,
                max_api_retries=max_api_retries,
                user_hdrs=user_hdrs,
            )
        return user_session

    def reset_session(self):
        """
        resets and re-authenticates the current session.
        """
        sessionDict[self.key]["connected"] = False
        logger.info("resetting session for %s", self.key)
        self.user_hdrs = {}
        for k, v in self.headers.items():
            if k not in self.SHARED_USER_HDRS:
                self.user_hdrs[k] = v
        self.headers = self.user_hdrs
        self.authenticate_session()

    def authenticate_session(self):
        """
        Performs session authentication with Avi controller and stores
        session cookies and sets header options like tenant.
        """
        body = {"username": self.avi_credentials.username}
        if self.avi_credentials.password:
            body["password"] = self.avi_credentials.password
        elif self.avi_credentials.token:
            body["token"] = self.avi_credentials.token
        else:
            raise APIError(
                "Neither user password or token provided for "
                "controller %s" % self.controller_ip
            )
        logger.debug(
            "authenticating user %s prefix %s",
            self.avi_credentials.username,
            self.prefix,
        )
        self.cookies.clear()
        err = None
        try:
            rsp = super().post(
                self.prefix + "/login", body, timeout=self.timeout, verify=self.verify
            )

            if rsp.status_code == 200:
                self.num_session_retries = 0
                self.remote_api_version = rsp.json().get("version", {})
                session_cookie_name = rsp.json().get("session_cookie_name", "sessionid")
                if self.user_hdrs:
                    self.headers.update(self.user_hdrs)
                if rsp.cookies and "csrftoken" in rsp.cookies:
                    csrftoken = rsp.cookies["csrftoken"]
                    sessionDict[self.key] = {
                        "csrftoken": csrftoken,
                        "session_id": rsp.cookies[session_cookie_name],
                        "last_used": datetime.utcnow(),
                        "api": self,
                        "connected": True,
                    }
                    self.avi_credentials.csrftoken = csrftoken
                    self.avi_credentials.session_id = rsp.cookies[session_cookie_name]
                logger.debug(
                    "authentication success for user %s", self.avi_credentials.username
                )
                return
            # Check for bad request and invalid credentials response code
            elif rsp.status_code in [401, 403]:
                logger.error(f"Status Code {rsp.status_code} msg {rsp.text}")
                err = APIError(
                    "Failed: {} Status Code {} msg {}".format(
                        rsp.url, rsp.status_code, rsp.text
                    ),
                    rsp,
                )
                raise err
            else:
                logger.error("Error status code %s msg %s", rsp.status_code, rsp.text)
                err = APIError(
                    "Failed: {} Status Code {} msg {}".format(
                        rsp.url, rsp.status_code, rsp.text
                    ),
                    rsp,
                )
                raise err
        except (ConnectionError, SSLError, ChunkedEncodingError) as e:
            if not self.retry_conxn_errors:
                raise
            logger.warning("Connection error retrying %s", e)
            err = e
        # comes here only if there was either exception or login was not
        # successful
        if self.retry_wait_time:
            time.sleep(self.retry_wait_time)
        self.num_session_retries += 1
        if self.num_session_retries > self.max_session_retries:
            self.num_session_retries = 0
            logger.error(
                "giving up after %d retries connection failure %s"
                % (self.max_session_retries, True)
            )
            raise err
        self.authenticate_session()
        return

    def _get_api_headers(self, tenant, tenant_uuid, timeout, headers, api_version):
        """
        returns the headers that are passed to the requests.Session api calls.
        """
        api_hdrs = copy.deepcopy(self.headers)
        api_hdrs.update({"Referer": self.prefix, "Content-Type": "application/json"})
        if self.user_hdrs:
            api_hdrs.update(self.user_hdrs)
        api_hdrs["timeout"] = str(timeout)
        if api_version:
            api_hdrs["X-Avi-Version"] = api_version
        elif self.avi_credentials.api_version:
            api_hdrs["X-Avi-Version"] = str(self.avi_credentials.api_version)
        if tenant:
            tenant_uuid = None
        elif tenant_uuid:
            tenant = None
        else:
            tenant = self.avi_credentials.tenant
            tenant_uuid = self.avi_credentials.tenant_uuid
        if tenant_uuid:
            api_hdrs.update({"X-Avi-Tenant-UUID": "%s" % tenant_uuid})
            api_hdrs.pop("X-Avi-Tenant", None)
        elif tenant:
            api_hdrs.update({"X-Avi-Tenant": "%s" % tenant})
            api_hdrs.pop("X-Avi-Tenant-UUID", None)
        if "Authorization" in api_hdrs:
            return api_hdrs
        if self.key in sessionDict and "csrftoken" in sessionDict.get(self.key):
            api_hdrs["X-CSRFToken"] = sessionDict.get(self.key)["csrftoken"]
        else:
            self.authenticate_session()
            api_hdrs["X-CSRFToken"] = sessionDict.get(self.key)["csrftoken"]
        # Override any user headers that were passed by users. We don't know
        # when the user had updated the user_hdrs
        if headers:
            # overwrite the headers passed via the API calls.
            api_hdrs.update(headers)
        return api_hdrs

    @staticmethod
    def _clean_inactive_sessions():
        """Removes sessions which are inactive more than 20 min"""
        session_cache = sessionDict
        logger.debug(
            "cleaning inactive sessions in pid %d num elem %d",
            os.getpid(),
            len(session_cache),
        )
        for key, session in list(session_cache.items()):
            tdiff = avi_timedelta(datetime.utcnow() - session["last_used"])
            if tdiff < ApiSession.SESSION_CACHE_EXPIRY:
                continue
            try:
                session["api"].post("logout")
            except Exception as e:
                logger.warning(
                    "Session not found on controller " "for session ID: %s %s",
                    session,
                    e,
                )
            del session_cache[key]
            logger.debug("Cleaned inactive session : %s", key)


# End of file
