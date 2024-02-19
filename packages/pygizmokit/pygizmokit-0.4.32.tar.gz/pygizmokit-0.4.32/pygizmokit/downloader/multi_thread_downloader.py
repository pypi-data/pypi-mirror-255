import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import requests
from rich.progress import TaskID

from ..progress_bar import ProgressBar
from ..rich_logger import set_up_logging
from ..unzipper import unzipper

set_up_logging()


# TODO: repeated file name to add 1 auto


class MultiDownloader:
    """A simple downloader using requests and rich.progress."""

    def __init__(
        self,
        output_dir: Path,
        *,
        proxy: dict[str, str] | None = None,
    ):
        self.progress_bar = ProgressBar()
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

    def add_tasks(self, urls: list[str]) -> None:
        """add tasks to download from urls"""
        if not isinstance(urls, list) or any(not isinstance(url, str) for url in urls):
            raise ValueError("urls must be a list of strings")
        self.urls.extend(urls)
        logging.info("estimating download files total size...")
        # init total task bar
        total_mb_size = self._get_total_size()
        total_bytes_size = total_mb_size * 1024 * 1024
        with self.progress_bar:
            self.global_task_id = self.progress_bar.add_global_task(
                total=total_bytes_size, total_size=total_mb_size
            )
            self._start_download()
        # auto unzip download file
        self._unzip_file()
        logging.info(f"all tasks done in {self.output_dir}")

    def _start_download(self) -> None:
        """start download files from urls by multithread"""
        with ThreadPoolExecutor() as executor:
            futures = []
            for url in self.urls:
                futures.append(executor.submit(self._download_file, url))
            for future in futures:
                future.result()

    def _download_file(self, url: str) -> None:
        """download file from url and update progress bar"""

        with self.progress_bar:
            with requests.get(
                url, stream=True, headers=self.header, proxies=self.proxies
            ) as resp:
                total_size_in_bytes = int(resp.headers.get("content-length", 0))
                filename = Path(url).name
                path_to_save = self.output_dir / filename
                # init task-bar
                new_task_id = self.progress_bar.add_task(
                    total=total_size_in_bytes,
                    filename=filename,
                )

                downloaded_size = 0
                with open(path_to_save, "wb") as file:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk and isinstance(chunk, bytes):
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            self.progress_bar.update(
                                new_task_id,
                                advance=len(chunk),
                            )
                        else:
                            logging.error(f"Received an empty chunk for {url}.")

            self._wait_for_all_done(url)

    def _wait_for_all_done(self, url: str) -> None:
        """prevent to finished in a thread to stop the progress bar keep updating"""
        self.urls.remove(url)
        if not self.urls:
            self.all_done.set()
        self.all_done.wait()

    def _get_total_size(self) -> float:
        """get total size(MB) of all files from url"""
        sum_total_size = 0.0
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

    def _unzip_file(self) -> None:
        """unzip file with folder name of itself to output folder"""
        for file_path in self.output_dir.rglob("*"):

            if unzipper.able_to_unzip(file_path):
                unzipper.select(file_path).unzip()
                file_path.unlink()


if __name__ == "__main__":
    download_urls = [
        "https://github.com/Atticuszz/BoostFace_fastapi/releases/download/v0.0.1/irn50_glint360k_r50.onnx",
        "https://github.com/Atticuszz/BoostFace_fastapi/archive/refs/tags/v0.0.1.zip",
        "https://github.com/Atticuszz/BoostFace_fastapi/archive/refs/tags/v0.0.1.tar.gz",
        "https://github.com/Atticuszz/BoostFace/releases/download/v0.0.1/LFW_dataset.zip",
        "https://github.com/Atticuszz/BoostFace/archive/refs/tags/v0.0.1.zip",
        "https://github.com/Atticuszz/BoostFace/archive/refs/tags/v0.0.1.tar.gz",
    ]
    save_directory = Path(__file__).parent / "downloads"

    # downloader.add_tasks(download_urls)
