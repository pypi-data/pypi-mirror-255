"""
Command for backup database.
"""
import json
import logging

from django.core.management.base import CommandError
import os
from django_sync_env import settings, utils
from django_sync_env.db.base import get_connector
from django_sync_env.storage import StorageError, get_storage
from django_sync_env.management.commands._base import BaseSyncBackupCommand, make_option
from django_sync_env.notifications import SyncEnvNotifications


class Command(BaseSyncBackupCommand):
    help = "Backup a database, compress and write to " "storage." ""
    content_type = "db"
    logger = logging.getLogger("sync_env")
    notifications = SyncEnvNotifications()
    option_list = BaseSyncBackupCommand.option_list + (
        # TODO enable the option to specify particular databases
        # make_option(
        #     "-d",
        #     "--database",
        #     help="Database(s) to backup specified by key separated by commas(default: all)",
        # ),
        # TODO enable the option to exclude particular tables in particular databases
        # make_option(
        #     "-x", "--exclude-tables",
        #     default=None,
        #     help="Exclude tables from backup",
        # ),
    )

    @utils.email_uncaught_exception
    def handle(self, **options):
        self._set_logger_level()

        self.verbosity = options.get("verbosity")
        self.quiet = options.get("quiet")
        self.compress = True  # enforce compression
        self.exclude_tables = None  # not in use yet
        # self.exclude_tables = options.get("exclude_tables")  # wip for later release

        database_keys = settings.DATABASES
        storage_config = utils.get_storage_config(settings.ENVIRONMENT, settings.SYNC_ENV_ENVIRONMENTS)
        storage = get_storage(settings.ENVIRONMENT, storage_config)
        if storage:
            for database_key in database_keys:
                self.connector = get_connector(database_key)
                if self.connector and self.exclude_tables:
                    self.connector.exclude.extend(
                        list(self.exclude_tables.replace(" ", "").split(","))
                    )
                database = self.connector.settings

                try:
                    self._save_new_backup(database, storage)
                except StorageError as err:
                    if self.notifications.enabled:
                        rich_text_blocks, text = self._format_slack_failure_notification(database)
                        self.notifications.send_slack_message(blocks=rich_text_blocks, text=text)
                    raise CommandError(err) from err

                if not self.quiet:
                    self.logger.info(f"Successfully backed up database: {database['NAME']}!", )
                if self.notifications.enabled:
                    # database backup was successful
                    rich_text_blocks, text = self._format_slack_success_notification(database)
                    self.notifications.send_slack_message(blocks=rich_text_blocks, text=text)
        else:
            self.logger.error(f'Unable to connect to storage for environment: {settings.ENVIRONMENT}, check config')

    def _save_new_backup(self, database, storage):
        """
        Save a new backup file.
        """
        if not self.quiet:
            self.logger.info("Backing Up Database: %s", database["NAME"])
        # Get backup and name
        outputfile = self.connector.create_dump()

        filename = self.connector.generate_filename(
            environment=settings.ENVIRONMENT,
            database_name=database["NAME"]
        )

        if self.compress:
            compressed_file, filename = utils.compress_file(outputfile, filename)
            outputfile = compressed_file

        if not self.quiet:
            self.logger.info("Backup size: %s", utils.handle_size(outputfile))
        # Store backup
        outputfile.seek(0)

        if storage.name == 'FileSystemStorage':
            file_path_out = os.path.join(storage.storage._location, filename)
            self.write_local_file(outputfile, file_path_out)
        else:
            self.write_to_storage(storage, outputfile, filename)

    @staticmethod
    def _format_slack_success_notification(database):
        """Returns the plain text and formatted dict object for a success rich-text Slack message"""
        plain_text_msg = f"{settings.SYNC_ENV_PROJECT_NAME}:[{settings.ENVIRONMENT}] - {database['NAME']} database backup was successful"
        rich_text_msg_blocks = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "emoji",
                                "name": "green_heart"
                            },
                            {
                                "type": "text",
                                "text": f" {settings.SYNC_ENV_PROJECT_NAME}",
                                "style": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": f" [{settings.ENVIRONMENT}] - {database['NAME']} database backup was"
                            },
                            {
                                "type": "text",
                                "text": " Successful",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            }
        ]

        return json.dumps(rich_text_msg_blocks), plain_text_msg

    @staticmethod
    def _format_slack_failure_notification(database):
        """Returns the plain text and the formatted dict object for a warning based rich-text Slack message"""
        plain_text_msg = f"{settings.SYNC_ENV_PROJECT_NAME}:[{settings.ENVIRONMENT}] - {database['NAME']} database backup failed"
        rich_text_msg_blocks = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "emoji",
                                "name": "warning"
                            },
                            {
                                "type": "text",
                                "text": f" {settings.SYNC_ENV_PROJECT_NAME}",
                                "style": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": f" [{settings.ENVIRONMENT}] - {database['NAME']} database backup"
                            },
                            {
                                "type": "text",
                                "text": " Failed!",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            }
        ]
        return json.dumps(rich_text_msg_blocks), plain_text_msg
