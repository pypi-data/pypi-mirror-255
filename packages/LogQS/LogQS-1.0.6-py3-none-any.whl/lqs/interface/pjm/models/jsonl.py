import io
import json
from typing import List, Optional

from pydantic import BaseModel


class JSONLTopicRow(BaseModel):
    is_topic_row: bool
    is_default_topic: bool

    topic_name: str
    topic_type_name: Optional[str] = None
    topic_type_schema: Optional[dict] = None
    topic_note: Optional[str] = None
    topic_context: Optional[dict] = None
    associated_topic_name: Optional[str] = None


class JSONLRow(BaseModel):
    timestamp: int
    data: dict
    topic_name: Optional[str] = None


class JSONLLog(BaseModel):
    name: Optional[str]
    rows: List[JSONLTopicRow | JSONLRow | dict]

    def write_jsonl_file_like(self, f=None):
        if f is None:
            f = io.StringIO()
        for line in self.rows:
            if isinstance(line, dict):
                # write this as compressed as possible
                f.write(json.dumps(line, separators=(",", ":")))
            else:
                f.write(line.model_dump_json())
            f.write("\n")
        f.seek(0)
        return f

    def write_jsonl_file(self, file_path=None):
        if file_path is None:
            if self.name is None:
                raise Exception("No file path provided and no name set.")
            file_path = f"{self.name.replace(' ', '_')}.jsonl"

        with open(file_path, "w") as f:
            for line in self.rows:
                if isinstance(line, dict):
                    f.write(json.dumps(line, separators=(",", ":")))
                else:
                    f.write(line.model_dump_json())
                f.write("\n")

    def get_jsonl_data(self):
        lines = []
        for line in self.rows:
            lines.append(line.model_dump_json())
        return "\n".join(lines).encode("utf-8")
