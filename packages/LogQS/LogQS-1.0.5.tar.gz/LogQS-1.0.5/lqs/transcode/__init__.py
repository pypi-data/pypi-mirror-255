import io
import orjson as json

from lqs.common.utils import get_logger
from lqs.transcode.ark.ark_json_parser import RbufMessageDeserializer
from lqs.transcode.config import TranscodeConfig
from lqs.transcode.ros1.ros_message_deserializer import RosMessageDeserializer


class Transcode:
    def __init__(self, config: TranscodeConfig | dict = TranscodeConfig()):
        self.config = (
            config if isinstance(config, TranscodeConfig) else TranscodeConfig(**config)
        )
        self.ros_deserializer = RosMessageDeserializer(
            trim_size=self.config.trim_cutoff
        )
        self.rbuf_deserializer = RbufMessageDeserializer(
            trim_size=self.config.trim_cutoff
        )
        self.logger = get_logger(
            self.__class__.__name__,
            level=self.config.log_level,
            json_logging=self.config.log_as_json,
        )

    def deserialize(self, type_encoding, type_name, type_data, message_bytes):
        if type_encoding == "ros1":
            message_bytes = io.BytesIO(message_bytes)
            res = self.ros_deserializer.deserialize(
                message_type=type_name,
                message_bytes=message_bytes,
                message_type_data=type_data,
            )
            return json.loads(json.dumps(res, default=lambda x: x.to_dict()))

        if type_encoding == "rbuf":
            message_bytes = io.BytesIO(message_bytes)
            res = self.rbuf_deserializer.deserialize(
                message_bytes=message_bytes,
                message_type=type_name,
                message_type_data=json.loads(type_data),
            )
            return json.loads(json.dumps(res, default=lambda x: x.to_dict()))

        if type_encoding == "json":
            return json.loads(message_bytes)

        raise NotImplementedError(f"Unknown type encoding: {type_encoding}")

    def serialize(self, type_encoding, type_name, type_data, message_dict):
        pass

    def get_schema(self, type_encoding, type_name, type_data) -> dict:
        if type_encoding == "ros1":
            res = self.ros_deserializer.get_json_schema(
                message_type=type_name, message_type_data=type_data
            )
        elif type_encoding == "rbuf":
            res = self.rbuf_deserializer.get_json_schema(
                message_type=type_name, message_type_data=type_data
            )
        else:
            raise NotImplementedError(f"Unknown type encoding: {type_encoding}")

        return res
