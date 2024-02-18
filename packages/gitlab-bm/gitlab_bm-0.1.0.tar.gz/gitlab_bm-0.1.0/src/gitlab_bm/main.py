#!/usr/bin/env python
"""
Gitlab Backup CLI
"""

import typer
from .logging_setup import setup_logging
from .backup import BackupManager
from .app_info import __version__


app = typer.Typer(no_args_is_help=True, add_completion=False,
                  help=f"Gitlab Backup Manager (GLBM) Ver. ({__version__})")
setup_logging()
manager = BackupManager()

@app.command(help="Run main backup")
def backup():
    """
    Run Main Backup
    """
    manager.backup()

@app.command(help="Run Backup Config and upload to S3")
def backup_etc():
    """
    Run Gitlab config backup and upload to S3
    """
    backup_file = manager.backup_etc()
    manager.upload_to_s3(backup_file)

@app.command(help="Delete old files on S3 based on (X) days to keep")
def delete_files(days_to_keep: int):
    """
    Delete old files on S3 based on # of days to keep
    """
    manager.delete_files(days_to_keep)

@app.command(help="Run backup, backup_etc, upload_to_s3 and delete_files")
def complete():
    """
    Run backup, backup_etc, upload_to_s3 and delete_files
    """
    manager.backup()
    backup_file = manager.backup_etc()
    manager.upload_to_s3(backup_file)
    manager.delete_files(manager.days_to_keep)

@app.callback(invoke_without_command=True)
def version_callback(version: bool = typer.Option(
    None, "--version", is_flag=True, help="Show application Version")):
    if version:
        typer.echo(f"Gitlab Backup (GLBM) Version: {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app.run()
