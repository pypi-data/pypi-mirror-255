"""Code for actors that use a simple rest interaction, converting the response to one or more
REST commands into a message posted to main processing thread.

"""
from functools import cached_property
from typing import Literal
from typing import Optional
from typing import Tuple

import yarl
from pydantic import BaseModel
from pydantic import Extra
from pydantic import HttpUrl
from pydantic import root_validator

from gwproto.utils import snake_to_camel


class URLArgs(BaseModel):
    """A container for paramters that can be passed to yarl.URL.build()"""

    scheme: Literal["http", "https", ""] = "https"
    user: Optional[str] = None
    password: Optional[str] = None
    host: str = ""
    port: Optional[int] = None
    path: str = ""
    query: Optional[list[Tuple[str, str | int | float]]] = None
    fragment: str = ""
    encoded: bool = True

    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True

    @classmethod
    def dict_from_url(cls, url: str | yarl.URL) -> dict:
        if isinstance(url, str):
            url = yarl.URL(url)
        return dict(
            scheme=url.scheme,
            user=url.user,
            password=url.password,
            host=url.host,
            port=url.port,
            path=url.path,
            query=list(url.query.items()),
            fragment=url.fragment,
        )

    @classmethod
    def from_url(cls, url: str | yarl.URL) -> "URLArgs":
        return URLArgs(**cls.dict_from_url(url))


class URLConfig(BaseModel):
    """Construct a URL. Three methods are provided. They are run in order of appearance,
    each updating and/or modifying the previous method.

    The methods are:
    - 'URL', an explicit string (e.g. https://www.example.org)
    - 'URLArgs', a dictionary of arguments that will be passed to yarl.URL.build()
    - 'URLPathFormat' and 'URLPathArgs', a format string and optional parameters used to
      set the 'path' portion of a yarl.URL.

    See make_url() for implementation.
    """

    url: Optional[HttpUrl] = None
    """URL as an explicit string"""

    url_args: Optional[URLArgs] = None
    """Arguments that can be passed to yarl.URL.build()"""

    url_path_format: str = ""
    """A string or format string used for the 'path' portion of the URL.
    This string will be formatted with the contents of url_path_args.
    For example, url_path_format="a/{device_id}/b" could be used used with
    url_path_args={"device_id":1} to produce a 'path' of "a/1/b".
    See make_url() for details.
    """

    url_path_args: Optional[dict[str, str | int | float]] = None
    """A dictionary of parameters used for filling in url_path_format to
    produce the URL 'path' field. The formatting operation is done as
    url_path_format.format(**URLPathArgs). See make_url() for details.
    """

    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True

    def to_url(self) -> yarl.URL:
        return self.make_url(self)

    @classmethod
    def make_url_args(cls, url_config: "URLConfig") -> Optional[dict]:
        if url_config is None:
            return None

        # args from self.url
        if url_config.url is None:
            url_args = dict()
        else:
            url_args = dict(URLArgs.from_url(yarl.URL(url_config.url)))

        # args from self.url_args
        if url_config.url_args is not None:
            url_args.update(url_config.url_args)

        # args from url_path_format
        if url_config.url_path_format:
            path = url_config.url_path_format
            if url_config.url_path_args:
                path = path.format(**url_config.url_path_args)
            url_args["path"] = path

        return url_args

    @classmethod
    def make_url(cls, url_config: "URLConfig") -> Optional[yarl.URL]:
        args = URLConfig.make_url_args(url_config)
        if args:
            return yarl.URL.build(**args)
        return None


class AioHttpClientTimeout(BaseModel):
    total: Optional[float] = None
    connect: Optional[float] = None
    sock_read: Optional[float] = None
    sock_connect: Optional[float] = None

    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class SessionArgs(BaseModel):
    base_url: Optional[URLConfig] = None
    timeout: Optional[AioHttpClientTimeout] = None

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class RequestArgs(BaseModel):
    url: Optional[URLConfig] = None
    method: Literal["GET", "POST", "PUT", "DELETE"] = "GET"
    params: Optional[dict] = None
    data: Optional[dict | list | tuple] = None
    headers: Optional[dict] = None
    timeout: AioHttpClientTimeout = None
    ssl: Optional[bool] = None

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class ErrorResponse(BaseModel):
    error_for_http_status: bool = True
    raise_exception: bool = False
    report: bool = True

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class ErrorResponses(BaseModel):
    request: ErrorResponse = ErrorResponse()
    convert: ErrorResponse = ErrorResponse()

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


DEFAULT_REST_POLL_PERIOD_SECONDS = 60.0


class RESTPollerSettings(BaseModel):
    session: SessionArgs = SessionArgs()
    request: RequestArgs = RequestArgs()
    poll_period_seconds: float = DEFAULT_REST_POLL_PERIOD_SECONDS
    errors: ErrorResponses = ErrorResponses()

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True
        keep_untouched = (cached_property,)

    def url_args(self) -> dict:
        session_args = URLConfig.make_url_args(self.session.base_url)
        request_args = URLConfig.make_url_args(self.request.url)
        if session_args is None and request_args is None:
            if session_args is None and request_args is None:
                raise ValueError(
                    "Neither session.base_url nor request.url produces a URL"
                )
        if session_args is not None:
            url_args = session_args
            if request_args is not None:
                url_args.update(request_args)
        else:
            url_args = request_args
        return url_args

    @cached_property
    def url(self) -> yarl.URL:
        if self.session.base_url is None and self.request.url is None:
            raise ValueError("Neither session.base_url nor request.url produces a URL")
        session_args = URLConfig.make_url_args(self.session.base_url)
        request_args = URLConfig.make_url_args(self.request.url)
        if session_args is not None:
            url_args = session_args
            if request_args is not None:
                url_args.update(request_args)
        else:
            url_args = request_args
        return yarl.URL.build(**url_args)

    def clear_property_cache(self):
        self.__dict__.pop("url", None)

    @root_validator(skip_on_failure=True)
    def post_root_validator(cls, values: dict) -> dict:
        base_url = URLConfig.make_url(values["session"].base_url)
        url = URLConfig.make_url(values["request"].url)
        if base_url is None and url is None:
            raise ValueError(
                "ERROR. At least one of session.base_url and request.url must be specified"
            )
        if base_url is None:
            if not url.is_absolute():
                raise ValueError(
                    "ERROR. if session.base_url is None, request.url must be absolute\n"
                    f"  request.url:      <{url}>\n"
                )
        if base_url is not None and not base_url.is_absolute():
            raise ValueError(
                f"ERROR. session.base_url is not absolute.\n"
                f"  session.base_url: <{base_url}>\n"
            )
        if base_url is not None and url is not None:
            if url.is_absolute():
                raise ValueError(
                    "ERROR. Both session.base_url and request.url are absolute.\n"
                    f"  session.base_url: <{base_url}>\n"
                    f"  request.url:      <{url}>\n"
                )
            if not url.path.startswith("/"):
                raise ValueError(
                    "ERROR. If session.base_url not None, request.url.path must start with '/'.\n"
                    f"  session.base_url: <{base_url}>\n"
                    f"  request.url:      <{url}>\n"
                    f"  request.url.path: <{url.path}>\n"
                )
        return values
