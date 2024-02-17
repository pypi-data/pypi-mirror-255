from pydantic import BaseModel, Field


class LoggerConfig(BaseModel):
    log_backup_count: int = Field(default=30, env="LOG_BACKUP_COUNT")
    log_dir: str = Field(default="atom", env="LOG_DIR")
    log_file_max_bytes: int = Field(default=100 << 10 << 10, env="LOG_FILE_MAX_BYTES")
