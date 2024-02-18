from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


class IngestProgress(Progress):
    def get_renderables(self):
        for task in self.tasks:
            if task.fields.get("progress_type") == "overall":
                self.columns = (
                    TextColumn("[bold green]{task.description}", justify="left"),
                    TextColumn("[bold yellow]{task.completed}/{task.total} files", justify="right"),
                )
            if task.fields.get("progress_type") == "ingest":
                self.columns = (
                    TextColumn("[bold blue]{task.fields[path_or_url]}", justify="right"),
                    BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    DownloadColumn(),
                    "•",
                    TransferSpeedColumn(),
                    "•",
                    TimeRemainingColumn(),
                )
            yield self.make_tasks_table([task])
