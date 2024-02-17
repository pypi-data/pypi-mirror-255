import uuid

from pydantic import BaseModel, Field


class SkyWalkingConfig(BaseModel):
    sw_switch: bool = Field(env="SW_SWITCH", default=False)
    sw_agent_backend: str = Field(env="SW_AGENT_COLLECTOR_BACKEND_SERVICES", default="")
    sw_agent_name: str = Field(env="SW_AGENT_NAME", default="")
    sw_agent_instance_name: str = Field(env="SW_AGENT_INSTANCE_NAME", default=uuid.uuid4().hex)
    sw_agent_log_reporter_active: bool = Field(env="SW_AGENT_LOG_REPORTER_ACTIVE", default=True)
    sw_agent_log_reporter_level: str = Field(env="SW_AGENT_LOG_REPORTER_LEVEL", default="DEBUG")
