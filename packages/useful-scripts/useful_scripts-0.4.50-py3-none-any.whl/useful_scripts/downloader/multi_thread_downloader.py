from concurrent.futures import ThreadPoolExecutor
from threading import Event
from timeit import default_timer


import requests
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskID,
)

from pathlib import Path

import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# 自定义进度条样式
custom_columns = [
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None, complete_style="yellow", finished_style="green"),
    TextColumn("{task.percentage:>3.2f}%"),
    TextColumn("[bold green]{task.fields[speed]} MB/s"),
    TextColumn("[bold cyan]{task.fields[file_size]} MB"),
]


class Downloader:
    """A simple downloader using requests and rich.progress."""

    def __init__(
        self,
        output_dir: Path = Path(__file__).parent / "downloads",
        *,
        proxy: dict[str, str] | None = None,
    ):
        self.progress_bar = Progress(*custom_columns, auto_refresh=True)
        self.urls: list[str] = []
        self.header: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.global_task_id: TaskID | None = None
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.last_call_time: float | None = None
        self.proxies = (
            proxy
            if proxy
            else {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890",
            }
        )
        self.all_done = Event()

    def add_tasks(self, urls: list[str]):
        """add tasks to download from urls"""
        if not isinstance(urls, list) or any(not isinstance(url, str) for url in urls):
            raise ValueError("urls must be a list of strings")
        self.urls.extend(urls)
        logging.info("estimating total size...")
        # init total task bar
        total_size = self._get_total_size()
        with self.progress_bar:
            self.global_task_id = self.progress_bar.add_task(
                "Overall Progress",
                total=len(self.urls),
                completed=0,
                filename="Overall Progress",
                speed="0.00",
                file_size=f"0.0/{total_size:.2f}",
            )
            self._start_download()
        logging.info("all tasks done")

    def _start_download(self):
        """start download files from urls by multithread"""
        with ThreadPoolExecutor() as executor:
            futures = []
            for url in self.urls:
                futures.append(executor.submit(self._download_file, url))
            for future in futures:
                future.result()

    def _download_file(self, url: str):
        """download file from url and update progress bar"""

        with requests.get(
            url, stream=True, headers=self.header, proxies=self.proxies
        ) as resp:
            total_size_in_bytes = int(resp.headers.get("content-length", 0))
            filename = Path(url).name
            path_to_save = self.output_dir / filename

            with self.progress_bar:
                # init task-bar
                new_task_id = self.progress_bar.add_task(
                    description=f"[bold blue]Downloading {filename}",
                    total=total_size_in_bytes,
                    filename=filename,
                    speed="0.00",
                    file_size=f"{0.0}/{self._bytes_to_MB(total_size_in_bytes):.2f}",
                )

                downloaded_size = 0

                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk and isinstance(chunk, bytes):
                        path_to_save.write_bytes(chunk)
                        downloaded_size += len(chunk)
                        file_size_str = f"{downloaded_size / (1024 * 1024):.2f}/{total_size_in_bytes / (1024 * 1024):.2f}"
                        self.progress_bar.update(
                            new_task_id,
                            advance=len(chunk),
                            speed=f"{self._calculate_speed(len(chunk)):.2f}",
                            file_size=file_size_str,
                        )
                    else:
                        logging.error(f"Received an empty chunk for {url}.")

                # advance total task bar
                self.progress_bar.update(self.global_task_id, advance=1)
                self._wait_for_all_done(url)

    def _wait_for_all_done(self, url: str):
        """prevent to finished in a thread to stop the progress bar keep updating"""
        self.urls.remove(url)
        if not self.urls:
            self.all_done.set()
        self.all_done.wait()

    def _calculate_speed(self, downloaded_size: int) -> float:
        """calculate download speed(MB/s)"""
        now = default_timer()
        if not self.last_call_time:
            self.last_call_time = now
            return 0.0

        elapsed_time = now - self.last_call_time
        self.last_call_time = now

        return self._bytes_to_MB(downloaded_size) / elapsed_time

    def _get_total_size(self) -> float:
        """get total size(MB) of all files from url"""
        sum_total_size = 0
        for url in self.urls.copy():
            sum_total_size += self._get_file_size(url)
        return sum_total_size

    def _get_file_size(
        self,
        url: str,
    ) -> float:
        try:
            # 尝试使用HEAD请求获取文件大小
            response = requests.head(
                url, allow_redirects=True, headers=self.header, proxies=self.proxies
            )
            if response.status_code in [200, 301, 302]:
                # 如果HEAD请求被重定向或直接成功，则获取content-length
                if "content-length" in response.headers:
                    return int(response.headers["content-length"]) / (1024 * 1024)
                else:
                    # 如果HEAD请求没有返回content-length，使用GET请求
                    response = requests.get(
                        url, stream=True, headers=self.header, proxies=self.proxies
                    )
                    if response.status_code == 200:
                        return int(response.headers.get("content-length", 0)) / (
                            1024 * 1024
                        )
            self.urls.remove(url)
            logging.error(f"Failed to get file size for {url}: {response.status_code}")
        except Exception as e:
            logging.error(f"Error getting file size for {url}: {e}")
            self.urls.remove(url)
        return 0.0  # 如果无法获取文件大小，则返回0.0

    def _bytes_to_MB(self, bytes: int) -> float:
        """convert bytes to MB"""
        return bytes / (1024 * 1024)


downloader = Downloader()


if __name__ == "__main__":
    download_urls = [
        "https://github.com/Atticuszz/BoostFace_fastapi/releases/download/v0.0.1/irn50_glint360k_r50.onnx",
        "https://github.com/Atticuszz/BoostFace_fastapi/archive/refs/tags/v0.0.1.zip",
        "https://github.com/Atticuszz/BoostFace_fastapi/archive/refs/tags/v0.0.1.tar.gz",
        "https://github.com/Atticuszz/Obsidian/releases/download/v0.0.6/portainer-backup_2024-01-31_08-33-56.tar.gz",
        "https://github.com/Atticuszz/Obsidian/releases/download/v0.0.5/openmv.zip",
        "https://github.com/Atticuszz/Obsidian/releases/download/v0.0.3/Cinebench2024_win_x86_64.zip",
        "https://github.com/Atticuszz/Obsidian/releases/download/v0.0.2/Win11.Win10.Acrobat.DC.2022.64Bit.rar",
    ]
    save_directory = Path(__file__).parent / "downloads"

    downloader.add_tasks(download_urls)
