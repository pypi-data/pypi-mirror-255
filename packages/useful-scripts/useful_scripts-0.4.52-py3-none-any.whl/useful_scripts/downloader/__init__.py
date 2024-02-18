"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 06/02/2024
@Description  :
"""
from pathlib import Path
from .multi_thread_downloader import Downloader


def download_files(
    urls: list[str], directory: str | Path, *, proxies: dict[str, str] | None = None
) -> None:
    """
    NOTE: if do not show process_bar,run with emulate terminal options
    multi-threads download multiple files from URL.
    blocking until all files are downloaded.
    :param urls: List of URLs of the files to download.
    :param directory: Directory where the files should be saved.
    :param proxies: such as clash proxies
    """
    download = Downloader(directory, proxy=proxies)
    download.add_tasks(urls)
