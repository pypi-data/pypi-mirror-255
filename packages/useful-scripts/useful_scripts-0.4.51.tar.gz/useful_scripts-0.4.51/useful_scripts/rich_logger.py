"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 07/02/2024
@Description  :
"""
import logging
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler

__all__ = ["set_up_logging"]


class CustomRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, show_time=True, show_path=False, **kwargs)
        self.console = Console()
        self.setLevel(logging.INFO)

    def emit(self, record: logging.LogRecord):
        # format the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # different color for different log level
        log_style = "green"
        if record.levelno == logging.WARNING:
            log_style = "yellow"
        elif record.levelno >= logging.ERROR:
            log_style = "red"
        elif record.levelno == logging.DEBUG:
            log_style = "blue"
        elif record.levelno == logging.INFO:
            log_style = "green"

        formatted_record = f"{current_time} - {record.name} - {record.levelname} - {record.getMessage()}"

        self.console.print(formatted_record, style=log_style)


def set_up_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,  # 设置为DEBUG以确保捕获所有级别的日志
        handlers=[CustomRichHandler()],
    )


if __name__ == "__main__":
    # 测试日志输出
    rich_logger = logging.getLogger("MyLogger")
    rich_logger.debug("This is a debug message.")
    rich_logger.info("This is an info message.")
    rich_logger.warning("This is a warning message.")
    rich_logger.error("This is an error message.")
    rich_logger.critical("This is a critical message.")
