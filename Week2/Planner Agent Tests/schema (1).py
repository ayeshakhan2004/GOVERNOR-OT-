"""
schema.py
---------
This is the ONE definition of what a "command" looks like in GOVERNOR-OT.
Ayesha's Planner outputs this. Maryum's Executor consumes this. Amaan/Damil's
Safety-Critic checks this. Everyone imports from this file instead of
re-typing the fields themselves, so the three pieces can never drift apart.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class OTCommand(BaseModel):
    """
    One instruction the Planner wants to send to the simulated PLC.
    Kept deliberately small and flat — Modbus itself only really has
    a handful of operations, so the schema mirrors that instead of
    inventing extra complexity.
    """

    action: Literal["read_register", "write_register", "read_coil", "write_coil"] = Field(
        ..., description="What kind of Modbus operation this is."
    )

    target_device: str = Field(
        ..., description="Which simulated device this is aimed at, e.g. 'PLC-1'."
    )

    register_address: int = Field(
        ..., ge=0, le=65535, description="Modbus register/coil address, valid range 0-65535."
    )

    value: Optional[int] = Field(
        None,
        description="Value to write. Must be present for write_* actions, "
                    "must be null/absent for read_* actions.",
    )

    reasoning: str = Field(
        ..., min_length=1, description="One short sentence: why the model chose this command."
    )

    # --- Sanity checks that don't need the Safety-Critic at all ---
    # These catch "the model returned nonsense shaped like a command"
    # before it's even handed off. The Safety-Critic (Amaan/Damil's job)
    # checks SAFETY. This just checks the command makes basic sense.

    def is_internally_consistent(self) -> tuple[bool, str]:
        if self.action.startswith("write") and self.value is None:
            return False, "write action is missing a value"
        if self.action.startswith("read") and self.value is not None:
            return False, "read action should not include a value"
        return True, "ok"


if __name__ == "__main__":
    # Quick smoke test — run `python schema.py` to confirm the schema itself works.
    example = OTCommand(
        action="write_register",
        target_device="PLC-1",
        register_address=40001,
        value=1,
        reasoning="Test write to confirm schema validates correctly.",
    )
    print(example.model_dump_json(indent=2))
    print("Consistent:", example.is_internally_consistent())
