# Copyright (c) Opendatalab. All rights reserved.
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def get_env_config():
    """
    从 .env 文件读取日志配置。

    Returns:
        dict: 包含日志配置的字典
    """
    # 从环境变量或默认值读取配置
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    log_dir = os.getenv("LOG_DIR", "logs")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 3))

    return {
        "level": log_level,
        "dir": log_dir,
        "max_bytes": max_bytes,
        "backup_count": backup_count
    }


def setup_logger(name: str = "pdf_translate", config: dict = None) -> logging.Logger:
    """
    设置日志配置，同时输出到控制台和文件。

    Args:
        name: 日志名称（通常是模块名 __name__）
        config: 日志配置字典，如 None 则从 .env 读取

    Returns:
        配置好的 Logger 对象
    """
    # 获取配置
    if config is None:
        config = get_env_config()

    log_level = config.get("level", logging.INFO)
    log_dir = config.get("dir", "logs")
    max_bytes = config.get("max_bytes", 10 * 1024 * 1024)
    backup_count = config.get("backup_count", 3)

    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 获取或创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 如果已经有处理器，不再重复添加
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（带轮转）
    log_file = log_path / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
