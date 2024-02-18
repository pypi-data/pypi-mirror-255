from pydantic import BaseModel, validator


class ComponentAddress(BaseModel):
    """Components of an address in the MAVLink protocol."""

    system_id: int
    component_id: int

    @validator("system_id", "component_id")
    def check_range(cls, v: int) -> int:
        if v < 0 or v > 255:
            raise ValueError("must be in the range from 0 to 255")
        return v
