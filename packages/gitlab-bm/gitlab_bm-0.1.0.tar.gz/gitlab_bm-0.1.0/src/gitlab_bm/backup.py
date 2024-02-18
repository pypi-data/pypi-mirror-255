
#!/usr/bin/env python
"""
GLBM Backup Module
"""

import os
import sys
import shutil
import glob
import gzip
from datetime import datetime, timedelta
import logging
from botocore.exceptions import NoCredentialsError, EndpointConnectionError
from .decorators import notify
from .s3_utils import setup_s3

class BackupManager:
    """
    Main Backup Manager Class
    """
    def __init__(self):
        try:
            (self.s3, self.s3_bucket, self.s3_directory,
             self.days_to_keep, self.s3_endpoint) = setup_s3() # pylint: disable=invalid-name
        except TypeError:
            logging.error("One of S3 variables missing from config or OS Env")
            sys.exit(1)

    def _clean_temp_files(self, dir_path):
        temp_files = glob.glob(dir_path + '/*')
        for file in temp_files:
            try:
                os.remove(file)
            except OSError as file_error:
                logging.error("Error: %s : %s", {file}, {file_error.strerror})

    @notify
    def backup(self):
        """
        Main Gitlab Backup Function:

        This is the backup that gets everything except the /etc configs for Gitlab
        """
        # Remove existing files
        logging.info("Clean up temp backup files...")
        self._clean_temp_files('/tmp/gitlab_backups')

        # Create GitLab backup
        logging.info("Run main GL Backup...")
        try:
            os.system('/usr/bin/gitlab-rake gitlab:backup:create CRON=1 SKIP=registry')
        except Exception as gen_e:
            raise Exception(f"Error in execution of gitlab-rake gitlab:backup:create command: {gen_e}") from gen_e

    @notify
    def backup_etc(self):
        """
        Gitlab backup of /etc configs
        """
        # Backup configuration
        logging.info("Cleaning temporary Config Backup directory...")
        self._clean_temp_files('/etc/gitlab/config_backup')

        logging.info("Run GL Config Backup...")
        try:
            os.system('/usr/bin/gitlab-ctl backup-etc')
        except Exception as gen_e:
            raise Exception(f"Error in execution of gitlab-ctl backup-etc: {gen_e}") from gen_e

        # Find latest tar file
        files = sorted(glob.glob('/etc/gitlab/config_backup/*.tar'), key=os.path.getctime)
        latest_file = files[-1]

        # Compress the latest file
        logging.info("Compress Config Backup file...")
        zipped_file = latest_file + '.gz'

        with open(latest_file, 'rb') as f_in, gzip.open(zipped_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        return zipped_file

    @notify
    def upload_to_s3(self, zipped_file):
        """
        Upload /etc backup config file to S3 storage
        """
        # Upload the compressed file to S3
        filename = os.path.basename(zipped_file)

        logging.info("Upload Config Backup to bucket path: '%s/%s/%s'", self.s3_bucket, self.s3_directory, filename)
        with open(f'{zipped_file}', 'rb') as data:
            file_content = data.read()
            try:
                self.s3.put_object(
                        Body=file_content,
                        Bucket=self.s3_bucket,
                        Key=f'{self.s3_directory}/{filename}')
            except self.s3.exceptions.NoSuchBucket as s3_error:
                raise Exception(f"Bucket: '{self.s3_bucket}' does not exist") from s3_error
            except Exception as gen_e:
                raise Exception from gen_e

    @notify
    def delete_files(self, days_to_keep=30):
        """
        Clean up of old backups on remote S3 storage
        """
        found_files = False
        if isinstance(days_to_keep, str):
            days_to_keep = int(days_to_keep)

        cutoff_date = datetime.now() - timedelta(days=days_to_keep + 1)
        try:
            response = self.s3.list_objects_v2(Bucket=self.s3_bucket, Prefix=self.s3_directory)
        except AttributeError as attr_e:
            raise Exception(f"Attribute Error {attr_e}") from attr_e
        except EndpointConnectionError as exc:
            raise Exception(f"Could not connect to the endpoint URL: {self.s3_endpoint}") from exc
        except self.s3.exceptions.NoSuchBucket as exc:
            raise Exception(f"Bucket: '{self.s3_bucket}' does not exist") from exc
        except NoCredentialsError as exc:
            raise Exception(f"No AWS credentials found") from exc

        if 'Contents' in response:
            for obj in response['Contents']:
                last_modified = datetime.strptime(
                    obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    '%Y-%m-%d %H:%M:%S'
                )

                if last_modified < cutoff_date:
                    logging.info("Deleting file %s", obj['Key'])
                    found_files = True
                    self.s3.delete_object(Bucket=self.s3_bucket, Key=obj['Key'])

        if not found_files:
            logging.info("No backup files in '%s' older than %d day(s) - Nothing deleted", self.s3_directory, days_to_keep)
