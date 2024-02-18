import json
from typing import Any, Dict

from pydantic import BaseModel
from scale_egp.cli.formatter import Markdownable
from scale_egp.sdk.enums import ModelVendor
from scale_egp.sdk.types.model_templates import ModelTemplate
from scale_egp.sdk.types.models import (
    ModelInstance,
)


class ModelInstanceDescription(BaseModel, Markdownable):
    model_instance: ModelInstance
    model_template: ModelTemplate

    def _get_description_dict(self) -> Dict[str, Any]:
        return {
            "model_instance": json.loads(self.model_instance.json()),
            "model_template": json.loads(self.model_template.json()),
        }

    def to_markdown(self) -> str:
        return (
            f"# {self.model_instance.name} (id: {self.model_instance.id})\n"
            f"\n"
            f"*type*: {self.model_template.model_type.value}\n"
            f"*vendor*: {(self.model_instance.model_vendor or ModelVendor.LAUNCH).value}\n"
            f"\n"
            f"{self.model_instance.description or ''}\n"
            f"## Model request schema\n"
            f"```\n"
            f"{json.dumps(self.model_instance.request_schema, indent=2)}\n"
            f"```\n"
            f"## Model response schema\n"
            f"```\n"
            f"{json.dumps(self.model_instance.response_schema, indent=2)}\n"
            f"```\n"
        )

    def json(self, **dumps_kwargs: Any) -> str:
        return json.dumps(self._get_description_dict(), **dumps_kwargs)
