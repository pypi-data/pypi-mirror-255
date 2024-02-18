"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 06/02/2024
@Description  :
"""

from pathlib import Path

from .multi_thread_downloader import MultiDownloader


def download_files(
    urls: list[str],
    *,
    output_dir: Path | None = None,
    proxies: dict[str, str] | None = None
) -> None:
    """
    NOTE: if do not show process_bar,run with emulate terminal options
    multi-threads download multiple files from URL.
    blocking until all files are downloaded.
    :param output_dir: If not provided, the current working directory is used.
    :param urls: List of URLs of the files to download.
    :param proxies: such as clash proxies
    """
    output_dir = output_dir if output_dir else Path().cwd() / "downloads"
    downloader = MultiDownloader(output_dir, proxy=proxies)
    downloader.add_tasks(urls)
