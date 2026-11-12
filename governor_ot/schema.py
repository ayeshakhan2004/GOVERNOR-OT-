import json
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Action(str, Enum):
    modbus_read = "modbus_read"
    modbus_write = "modbus_write"
    nmap_scan = "nmap_scan"


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Fixed choices, never free text.
    action: Action
    # The target the action aims at. Plain string, format is not checked here.
    target_ip: str
    # Default so the model need not recall it. Range is well-formedness only.
    port: int = Field(default=502, ge=1, le=65535)
    # Which Modbus register. Non-negative when present, modbus actions only.
    register: Optional[int] = Field(default=None, ge=0)
    # Only meaningful for modbus_write. Unbounded on purpose.
    value: Optional[int] = None
    # One code-like call string, stored verbatim and never parsed here.
    expression: str = Field(min_length=1)
    # Free text for a human reading logs. Never used for decisions.
    reasoning: Optional[str] = None

    @model_validator(mode="after")
    def write_needs_value(self):
        if self.action == Action.modbus_write and self.value is None:
            raise ValueError("modbus_write requires a value")
        return self

    @model_validator(mode="after")
    def modbus_needs_register(self):
        if (
            self.action in (Action.modbus_read, Action.modbus_write)
            and self.register is None
        ):
            raise ValueError(f"{self.action.value} requires a register")
        return self

    @model_validator(mode="after")
    def nmap_has_no_modbus_fields(self):
        if self.action == Action.nmap_scan and (
            self.register is not None or self.value is not None
        ):
            raise ValueError("nmap_scan must not carry a register or value")
        return self


if __name__ == "__main__":
    print(json.dumps(Command.model_json_schema(), indent=2))
