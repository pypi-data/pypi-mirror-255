# Gitlab Backup Manager (GLBM)

Gitlab Backup Manager is a tool to help manage Backups of Gitlab in one place.

>**Main Backup** = gitlab-rake gitlab:backup:create<br>
 __Backup Config__ = gitlab-ctl backup-etc

<hr>

## Getting started

### Installation (Preferred)

```sh
$ pip installl gitlab_bm
```

After install run the following to see default opitions:

```sh
$ glbm
Usage: glbm [OPTIONS] COMMAND [ARGS]...

  Gitlab Backup Manager (GLBM) Ver. (x.x.x)

Options:
  --version  Show application Version
  --help     Show this message and exit.

Commands:
  backup            Run Main Backup
  backup-etc        Run Backup Config and upload to S3
  complete          Run backup, backup_etc, upload to S3
  delete-files      Delete old files from S3 based on (X) days to keep
```

<hr>

## Current Limitations

* Only supports Slack Notifications
* Manual setup of **Main Backup** in `gitlab.rb` still needed
* (Scheduling of jobs) - Need to manually setup.

### Development

Want to contribute? Great!  No specifics at this point.  Just basic GitHub Fork and Pull request.<br>
For further info, see [github guide] on contributing to opensource project.<br>

After cloning your Forked branch locally, and installing Poetry, you can run the following to setup dev env and test:

```sh
$ poetry install
```
Then to run, do the following:
```
$ poetry run glbm
```


License
----

MIT [LICENSE.txt]

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [LICENSE.txt]: <https://github.com/CodeBleu/rabbitmqStats/LICENSE.txt>
   [Github Guide]: <https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project>
