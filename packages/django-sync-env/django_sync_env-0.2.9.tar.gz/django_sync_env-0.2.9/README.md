# Django sync env

django-sync-env is a Django app to manage backing up and restoring django databases and media assets easily.

Detailed documentation is in the "docs" directory (it's a work in progress).


## Requirements:
- configurable backups and restore which can be run on demand, celery cron or in dev.
- support s3 bucket and file storage options first, add azure blob storage later
- interactive prompts for local dev
- command line options with --no-input for CICD and automations
- restore latest option for media and backups for X env
- backup before restore option


## Setup

1. Add "django_sync_env" to your INSTALLED_APPS setting like this:

```
   INSTALLED_APPS = [
   ...,
   "django_sync_env",
   ]
```

2. Configure the app via a settings file .typically `./settings/partial/sync_env.py` for base configuration,
   don't forget to import this file via your base.py settings file
   And override any required settings per environment via `./settings/partials/[env].py`
   see [example_partials](docs/example_partials.md)

There is a [s3 terraform example](docs/example_terraform_aws_s3_bucket.md) for provisioning
an aws s3 bucket, iam user, roles and policy to allow for remote backup/restore to/from a secure s3 bucket.

See [management commands](docs/management_commands.md) for more details for each of the commands available.

- `./manage.py sync_env_backup_db` [usage](docs/management_commands.md#managepy-syncenvbackupdb)
- `./manage.py sync_env_backup_media`
- `./manage.py sync_env_restore_db`
- `./manage.py sync_env_restore_media`
- `./manage.py sync_env_list_backups`

See [Tasks](docs/tasks.md) for more details for each of the tasks available.

## Development and Publishing
See [documentation](docs/development_and_release_notes.md). 


## TODO:
- remove command options which we wont use
- make sure all management commands work with good error logging and handling
- Update the sync-env-backup command to enable the option to specify particular databases
- Update the sync-env-backup command to exclude particular tables in particular databases
- 
