import json
from typing import List, Optional

from pydantic import BaseModel


class JSONLMetaData(BaseModel):
    topic_name: str
    topic_type_name: Optional[str] = None
    topic_type_schema: Optional[dict] = None
    topic_note: Optional[str] = None
    topic_context: Optional[dict] = None
    associated_topic_name: Optional[str] = None
    generate_query_data: bool = True


class JSONLRow(BaseModel):
    timestamp: int
    data: dict
    query_data: Optional[dict]


class JSONLLog(BaseModel):
    name: Optional[str]
    header: Optional[JSONLMetaData]
    rows: List[JSONLRow | dict]

    def write_jsonl_file(self, file_path=None):
        if file_path is None:
            if self.name is None:
                raise Exception("No file path provided and no name set.")
            file_path = f"{self.name}.jsonl"

        with open(file_path, "w") as f:
            if self.header is not None:
                f.write(self.header.model_dump_json())
                f.write("\n")
            for line in self.rows:
                if isinstance(line, dict):
                    f.write(json.dumps(line))
                else:
                    f.write(line.model_dump_json())
                f.write("\n")

    def get_jsonl_data(self):
        lines = []
        if self.header is not None:
            lines.append(self.header.model_dump_json())
        for line in self.rows:
            lines.append(line.model_dump_json())
        return "\n".join(lines).encode("utf-8")
