"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 09/02/2024
@Description  :
"""

from typing import Any

from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

# 自定义进度条样式
custom_columns = [
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(complete_style="yellow", finished_style="green"),
    TaskProgressColumn(),
    TextColumn("[bold green]{task.fields[speed]} MB/s"),
    TimeRemainingColumn(),
    TextColumn("[bold cyan]{task.fields[file_size]} MB"),
]


class ProgressBar(Progress):

    def __init__(self) -> None:
        super().__init__(*custom_columns, auto_refresh=True)
        self.global_task_id: TaskID | None = None

    def add_global_task(self, total: float, total_size: float) -> TaskID:
        """Add a global task to the progress bar
        :param total:
        :param total_size: Total size of all files MB
        """
        global_task_id = super().add_task(
            "Overall Progress",
            total=total,
            completed=0,
            filename="Overall Progress",
            speed="0.00",
            file_size=f"0.0/{total_size:.2f}",
        )
        self.global_task_id = global_task_id
        return global_task_id

    def add_task(
        self,
        filename: str,
        action: str = "Downloading",
        total: int = 0,
        **fields: Any,
    ) -> TaskID:
        """Add a task to the progress bar"""
        return super().add_task(
            description=f"[bold blue]Downloading {filename}",
            total=total,
            filename=filename,
            speed="0.00",
            file_size=f"{0.0}/{total / (1024 * 1024):.2f}",
        )

    def update(
        self,
        task_id: TaskID,
        *,
        advance: int = 0,
        **fields: Any,
    ) -> None:
        """
        Update a task in the progress bar
        :param task_id:
        :param advance: advance in total bytes
        """
        bytes_speed = self._speed(task_id)
        process = self._process(task_id, advance)
        # update task
        super().update(
            task_id,
            total=self._tasks[task_id].total,
            advance=advance,
            speed=f"{bytes_speed / (1024 * 1024):.2f}",
            file_size=f"{process / (1024 * 1024):.2f}/{self._tasks[task_id].total / (1024 * 1024):.2f}",
        )
        self.update_total(advance)

    def update_total(self, advance: int) -> None:
        """update total task"""
        total_bytes_speed = self._speed(self.global_task_id)
        total_process = self._process(self.global_task_id, advance)
        if self.global_task_id is not None:
            super().update(
                self.global_task_id,
                total=self._tasks[self.global_task_id].total,
                advance=advance,
                speed=f"{total_bytes_speed / (1024 * 1024):.2f}",
                file_size=f"{total_process / (1024 * 1024):.2f}/{self._tasks[self.global_task_id].total / (1024 * 1024):.2f}",
            )

    def _speed(self, task_id: TaskID) -> float:
        """get speed of task_id"""
        return self._tasks[task_id].speed if self._tasks[task_id].speed else 0

    def _process(self, task_id: TaskID, advance: int) -> float:
        return self._tasks[task_id].completed + advance


def create_progress_bar() -> Progress:
    """Create a progress bar with custom columns"""
    return Progress(*custom_columns, auto_refresh=True)
