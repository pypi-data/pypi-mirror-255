"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author: 18317
@Date Created: 08/02/2024
@Description :
"""
import logging
import tarfile
import zipfile
from typing import Callable

import rarfile
import py7zr
from pathlib import Path

from .paths import path_check


class UnzipManager:
    def __init__(self):
        self.handlers = {
            '.zip': self._unzip_zip,
            '.tar': self._unzip_tar,
            '.gz': self._unzip_tar,
            '.tgz': self._unzip_tar,
            '.rar': self._unzip_rar,
            '.7z': self._unzip_7z,
        }
        self.handler: Callable[[], None] | None = None
        self.file_path: Path | None = None
        self.output_dir: Path | None = None

    def select(self, file_path: Path | str) -> "self":
        """select file to unzip"""
        self.file_path = path_check(file_path)
        if self.able_to_unzip(self.file_path):
            self.handler = self.handlers[self.file_path.suffix]
        return self

    def unzip(self, output_dir: Path | str | None = None) -> None:
        """unzip the file to the output_dir.
        :param output_dir: default is the same directory as the file.
        """
        if not output_dir:
            output_dir = self.file_path.parent
        self.output_dir = path_check(output_dir)
        logging.info(f"Unzipping {self.file_path.name} to {output_dir}...")

        if not self.output_dir or not self.file_path or not self.handler:
            logging.warning(f"file_path: {self.file_path} or output_dir: {self.output_dir} is not valid.")
            return
        try:
            self.handler()
        except Exception as e:
            logging.exception(e, exc_info=True)
        else:
            logging.info(f"Unzipping {self.file_path.name} to {output_dir}...Done")

    def able_to_unzip(self, file_path: Path | str) -> bool:
        """check if the file is able to unzip."""
        file_path = path_check(file_path)
        if file_path and self.handlers.get(file_path.suffix):
            return True
        else:
            return False

    def _unzip_zip(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.output_dir)

    def _unzip_tar(self):
        with tarfile.open(self.file_path, 'r:*') as tar_ref:
            tar_ref.extractall(self.output_dir)

    def _unzip_rar(self):
        with rarfile.RarFile(self.file_path, 'r') as rar_ref:
            rar_ref.extractall(self.output_dir)

    def _unzip_7z(self):
        with py7zr.SevenZipFile(self.file_path, mode='r') as zip_ref:
            zip_ref.extractall(self.output_dir)


unzipper = UnzipManager()
# 使用示例
if __name__ == "__main__":
    pass
