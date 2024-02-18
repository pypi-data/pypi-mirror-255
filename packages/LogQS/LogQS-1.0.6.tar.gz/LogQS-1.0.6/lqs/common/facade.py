import json
from typing import Type, Any
from logging import Logger

from lqs.common.config import CommonConfig
from lqs.common.utils import get_logger, ContextLoggerAdapter


class Facade:
    logger: Logger | ContextLoggerAdapter

    def setup(
        self,
        config: CommonConfig | dict[str, Any] | str,
        config_class: Type[CommonConfig],
    ):
        if isinstance(config, dict):
            self.config: config_class = config_class(**config)
        elif isinstance(config, str):
            self.config: config_class = config_class(**json.loads(config))
        else:
            self.config: config_class = config
        log_level = self.config.log_level or "INFO"
        self.logger = get_logger(
            self.__class__.__name__,
            level=log_level,
            log_to_file=self.config.log_to_file,
            json_logging=self.config.log_as_json,
        )

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warn(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def json(self, req):
        """
        Convert a JSON request to a dictionary.
        """
        return self.dict(json.loads(req))

    def dict(self, req):
        """
        Parse a dictionary request to a dictionary.
        """
        action = req.get("action")
        resource = req.get("resource")
        kwargs = req.get("kwargs")

        if action is None:
            raise Exception('[BadRequest] Required field "action" is missing.')

        if resource is None:
            resource_handler = getattr(self, action)
        else:
            action_handler = getattr(self, action)
            resource_handler = getattr(action_handler, resource)

        if kwargs is None:
            return resource_handler()
        else:
            return resource_handler(**kwargs)
