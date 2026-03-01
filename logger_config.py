# Copyright (c) Opendatalab. All rights reserved.
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "pdf_translate", log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """
    设置日志配置，同时输出到控制台和文件。

    Args:
        name: 日志名称（通常是模块名 __name__）
        log_dir: 日志文件存储目录
        level: 日志级别

    Returns:
        配置好的 Logger 对象
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 获取或创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

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
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（带轮转）
    log_file = log_path / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,  # 保留 3 个备份文件
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
