from typing import Optional

import yarl
from gridworks.property_format import predicate_validator
from pydantic import BaseModel

from gwproto.types.rest_poller_gt import URLArgs
from gwproto.types.rest_poller_gt import URLConfig
from gwproto.utils import has_mac_address_format


class HubitatGt(BaseModel):
    Host: str
    MakerApiId: int
    AccessToken: str
    MacAddress: str

    _is_mac_address = predicate_validator("MacAddress", has_mac_address_format)

    def url_config(self) -> URLConfig:
        return URLConfig(
            url_args=URLArgs(
                scheme="http",
                host=self.Host,
            ),
        )

    def maker_api_url_config(self) -> URLConfig:
        config = self.url_config()
        if config.url_args.query is None:
            config.url_args.query = []
        config.url_args.query.append(("access_token", self.AccessToken))
        if config.url_path_format is None:
            config.url_path_format = ""
        config.url_path_format += "/apps/api/{app_id}"
        if config.url_path_args is None:
            config.url_path_args = {}
        config.url_path_args.update({"app_id": self.MakerApiId})
        return config

    def devices_url_config(self) -> URLConfig:
        config = self.maker_api_url_config()
        config.url_path_format += "/devices"
        return config

    def url_configs(self) -> dict[str, URLConfig]:
        return dict(
            base=self.url_config(),
            maker_api=self.maker_api_url_config(),
            devices=self.devices_url_config(),
        )

    def urls(self) -> dict[str, Optional[yarl.URL]]:
        return {
            name: URLConfig.make_url(config)
            for name, config in self.url_configs().items()
        }

    def refresh_url_config(self, device_id: int) -> URLConfig:
        config = self.maker_api_url_config()
        config.url_path_format += "/devices/{device_id}/refresh"
        config.url_path_args["device_id"] = device_id
        return config

    def refresh_url(self, device_id: int) -> yarl.URL:
        return URLConfig.make_url(self.refresh_url_config(device_id))
