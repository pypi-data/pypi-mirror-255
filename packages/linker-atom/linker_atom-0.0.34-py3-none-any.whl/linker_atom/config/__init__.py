import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

from linker_atom.config.logger import LoggerConfig
from linker_atom.config.serving import ServingConfig
from linker_atom.config.skywalking import SkyWalkingConfig


class Settings(BaseSettings):
    atom_workers: int = Field(default=1, env="ATOM_WORKERS")
    atom_port: int = Field(default=8000, env="ATOM_PORT")
    atom_title: str = Field(default='Atom', env='ATOM_TITLE')
    atom_description: str = Field(default='Atom', env='ATOM_DESC')
    atom_api_prefix: str = Field(default='', env='ATOM_API_PREFIX')
    
    log_config: LoggerConfig = Field(default={})
    sw_config: SkyWalkingConfig = Field(default={})
    
    serving_meta_raw: str = Field(env="META", default="")
    
    @property
    def model_id_list(self) -> List[str]:
        return list(filter(None, self.serving_config.model_ids.split(",")))
    
    @property
    def serving_config(self):
        if self.serving_meta_raw:
            return ServingConfig.parse_raw(self.serving_meta_raw)
        return ServingConfig()
    
    @property
    def healthcheck_url(self) -> str:
        if not self.serving_meta_raw:
            return self.atom_api_prefix + self.serving_config.atom_healthcheck_url
        return self.serving_config.atom_healthcheck_url
    
    class Config:
        env_file = "../env"
        env_file_encoding = "utf-8"
        env_prefix = "ATOM_"
        case_sensitive = True


load_dotenv()
settings = Settings()
