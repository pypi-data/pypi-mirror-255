from lqs.transcode.ros1.RosMessageParserVisitorForMD5 import (
    RosMessageParserVisitorForMD5,
)
from lqs.transcode.ros1.ros_deserialization_methods import *  # noqa  # used by the generated code we execute dynamically
from lqs.transcode.ros1.RosMessageLexer import RosMessageLexer
from lqs.transcode.ros1.RosMessageParser import RosMessageParser
from lqs.transcode.ros1.RosMessageParserVisitor import (
    RosMessageParserVisitor,
    RosMessageParserVisitorForJsonSchema,
)
from antlr4 import CommonTokenStream, InputStream


import sys
import types

# TODO consider using slots like genpy does


class RosMessageDeserializer:
    def __init__(self, trim_size=None, generate_unnested_schema=True) -> None:
        self._class_registry = {}
        self._trim_size = trim_size
        self.generate_unnested_schema = generate_unnested_schema

    def _register(self, message_type, message_type_data) -> None:
        lexer = RosMessageLexer(InputStream(message_type_data))
        stream = CommonTokenStream(lexer)
        parser = RosMessageParser(stream)
        tree = parser.rosbag_input()
        if parser.getNumberOfSyntaxErrors() > 0:
            raise SyntaxError("syntax errors in ROS message definition")
        else:
            vinterp = RosMessageParserVisitor(message_class_name=message_type)
            class_registry = vinterp.visit(tree)
            if class_registry is None:
                raise ValueError("class_registry is None")
            self._class_registry.update(class_registry)
            class_mapping = {}
            for canonical_name, python_class_defintion in class_registry.items():
                package, class_name = canonical_name.rsplit(".")
                exec(
                    python_class_defintion + f"\n{class_name} = {class_name}",
                    None,
                    class_mapping,
                )
                if package not in sys.modules:
                    temp_package = types.ModuleType(
                        package, "This is a fake module for " + package
                    )
                    sys.modules[package] = temp_package
                else:
                    temp_package = sys.modules[package]
                class_mapping[class_name].__module__ = package
                temp_package.__dict__.update(
                    {
                        class_name: class_mapping[class_name],
                    }
                )

    def deserialize(self, message_bytes, message_type, message_type_data=None):
        main_package, main_class_name = message_type.rsplit("/")
        if message_type.replace("/", ".") not in self._class_registry:
            self._register(message_type, message_type_data)
        main_cls = getattr(__import__(main_package), main_class_name)

        res = main_cls()
        res.deserialize(message_bytes, TRIM_SIZE=self._trim_size)
        return res

    def get_json_schema(self, message_type, message_type_data) -> dict:
        lexer = RosMessageLexer(InputStream(message_type_data))
        stream = CommonTokenStream(lexer)
        parser = RosMessageParser(stream)
        tree = parser.rosbag_input()
        if parser.getNumberOfSyntaxErrors() > 0:
            raise SyntaxError("syntax errors in ROS message definition")
        else:
            vinterp = RosMessageParserVisitorForJsonSchema(
                message_class_name=message_type,
                generate_unnested_schema=self.generate_unnested_schema,
            )
            json_schema = vinterp.visit(tree)
            assert isinstance(json_schema, dict)
            return json_schema

    def get_md5(self, message_type, message_type_data):
        lexer = RosMessageLexer(InputStream(message_type_data))
        stream = CommonTokenStream(lexer)
        parser = RosMessageParser(stream)
        tree = parser.rosbag_input()
        if parser.getNumberOfSyntaxErrors() > 0:
            raise SyntaxError("syntax errors in ROS message definition")
        else:
            vinterp = RosMessageParserVisitorForMD5(
                message_class_name=message_type,
            )
            md5 = vinterp.visit(tree)
            return md5
