<div align='center'>
  <br>
  <img alt="Juntos Somos +" src="https://assets-img.juntossomosmais.com.br/images/logo.svg" width="350px">
  <h1>Django Import Export Stomp</h1>
</div>

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=juntossomosmais_django-import-export-stomp&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=juntossomosmais_django-import-export-stomp)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=juntossomosmais_django-import-export-stomp&metric=coverage)](https://sonarcloud.io/summary/new_code?id=juntossomosmais_django-import-export-stomp)
[![Build Status](https://dev.azure.com/juntos-somos-mais-loyalty/python/_apis/build/status%2Fjuntossomosmais.django-import-export-stomp?repoName=juntossomosmais%2Fdjango-import-export-stomp&branchName=main)](https://dev.azure.com/juntos-somos-mais-loyalty/python/_build/latest?definitionId=474&repoName=juntossomosmais%2Fdjango-import-export-stomp&branchName=main)
[![PyPI version](https://badge.fury.io/py/django-import-export-stomp.svg)](https://badge.fury.io/py/django-import-export-stomp)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Generic badge](https://img.shields.io/badge/python-3.10_3.11-green.svg)](https://www.python.org/)
[![Generic badge](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com/)

TLDR: Django plugin for file import/export on top of [django-import-export](https://github.com/django-import-export/django-import-export) using [django-stomp](https://github.com/juntossomosmais/django-stomp).

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About](#about)
- [Codebase](#codebase)
  - [The stack](#the-stack)
  - [Engineering standards](#engineering-standards)
    - [Commit hooks](#commit-hooks)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running example application with Docker](#running-example-application-with-docker)
  - [Testing the application with Docker](#testing-the-application-with-docker)
- [Documentation](#documentation)
  - [Basic installation](#basic-installation)
  - [Running the consumer](#running-the-consumer)
  - [Setting up imports](#setting-up-imports)
  - [Setting up export](#setting-up-export)
  - [How to use upload with aws s3 presigned url](#how-to-use-upload-with-aws-s3-presigned-url)
  - [Performing an import](#performing-an-import)
  - [Performing an export](#performing-an-export)
  - [Settings](#settings)
  - [Credits](#credits)

## About

Django Import Export Stomp is a django plugin that uses [django-stomp](https://github.com/juntossomosmais/django-stomp) to import/export models to spreadsheet-like files (csv, xlsx, etc.).

## Codebase

### The stack

This application uses  at least [Python 3.10](https://www.python.org/downloads/) with at least [Django 5.1](https://docs.djangoproject.com/en/5.1/).

### Engineering standards

#### Commit hooks

Currently we're using `pre-commit`.
To configure it simply use the commands below.

```sh
pip install pre-commit
pre-commit install
```

This will automatically lint the staged files using our project standard linters.

## Getting Started

This section provides a high-level requirement & quick start guide.

### Prerequisites

- [docker](https://docs.docker.com/get-docker/)
- [docker compose](https://docs.docker.com/compose/install/)

> :warning:
>
> We do not recommend developing the application without docker!
>
> :warning:

### Running example application with Docker

1. Clone the repository via `ssh`, ie.
   `git clone git@github.com:juntossomosmais/django-import-export-stomp.git`.

2. Simply running `docker compose up --build example` is enough to start running `django-import-export-stomp` on a exmaple with Docker.

### Testing the application with Docker

1. If you want to run the tests run: `docker compose run integration-tests`.

2. To run the sonar analysis locally you can use `docker compose up -d sonar-client` and then `docker compose up -d sonar-cli`

## Documentation

### Basic installation

1. Install package: `pip install django-import-export-stomp`
2. Add `import_export_stomp` to your `INSTALLED_APPS` in your `settings.py`
3. Add `author.middlewares.AuthorDefaultBackendMiddleware` to your `MIDDLEWARE_CLASSES` in your `settings.py`
4. Setup [django-stomp](https://github.com/juntossomosmais/django-stomp)

### Running the consumer

Run `python manage.py import_export pubsub` to start processing messages from the queues.

### Setting up imports

On your settings.py add a `IMPORT_EXPORT_MODELS` variable:

```python
from import_export_stomp.resources import resource_importer

IMPORT_EXPORT_STOMP_MODELS = {
    "Name of your import": {
        "app_label": "fake_app",
        "model_name": "FakeModel",
        "resource": resource_importer(
            "tests.resources.fake_app.resources.FakeResource"
        ),  # optional
    }
}
```

By default a dry run of the import is initiated when the import object is created. To instead import the file immediately without a dry-run set the `IMPORT_DRY_RUN_FIRST_TIME` to `False`.

`IMPORT_DRY_RUN_FIRST_TIME = False`

### Setting up export

As with imports, a fully configured example project can be found in the `example` directory.

1. Add a `export_resource_classes` classmethod to the model you want to export.

    ```python
    @classmethod
    def export_resource_classes(cls):
        return {
            'winners': ('Winners resource', WinnersResource),
            'winners_all_caps': ('Winners with all caps column resource', WinnersWithAllCapsResource),
        }
    ```

    This should return a dictionary of tuples. The keys should be unique unchanging strings, the tuples should consist of a `resource <https://django-import-export.readthedocs.io/en/latest/getting_started.html#creating-import-export-resource>`__ and a human friendly description of that resource.

2. Add the `create_export_job_action` to the model's `ModelAdmin`.

    ```python
    from django.contrib import admin
    from import_export.admin_actions import create_export_job_action

    from . import models

    @admin.register(models.Winner)
    class WinnerAdmin(admin.ModelAdmin):
        list_display = (
            'name',
        )

        actions = (
            create_export_job_action,
        )
    ```

3. To customise export queryset you need to add `get_export_queryset` to the `ModelResource`.

    ```python
    class WinnersResource(ModelResource):
        class Meta:
            model = Winner

        def get_export_queryset(self):
            """To customise the queryset of the model resource with annotation override"""
            return self.Meta.model.objects.annotate(device_type=Subquery(FCMDevice.objects.filter(
                    user=OuterRef("pk")).values("type")[:1])
    ```

4. Done!

### How to use upload with aws s3 presigned url

1. Have `boto3` and `django-storages` installed in your project: `pip install boto3 django-storages`
2. Setup [django-storages](https://github.com/jschneier/django-storages) variables - `AWS_STORAGE_BUCKET_NAME` is required.
3. Set `IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST` to `True`.
4. Add urls from `import_export_stomp.urls` to your `urls.py`

    ```python
    from import_export_stomp.urls import urlpatterns as import_export_stomp_urlpatterns

    urlpatterns = [...]  # Your urls
    urlpatterns += import_export_stomp_urlpatterns
    ```

5. Done!

### Performing an import

You will find an example django application that uses django-import-export-stomp for importing data. Once you have it running, you can perform an import with the following steps.

1. Navigate to the example applications admin page:

    ![example](screenshots/admin.png)

2. Navigate to the ImportJobs table:

   ![example](screenshots/import_jobs.png)

3. Create a new import job. There is an example import CSV file in the example/example-data directory. Select that file. Select csv as the file format. We'll be importing to the Winner's model table.

   ![example](screenshots/new_import_job.png)

4. Select "Save and continue editing" to save the import job and refresh until you see that a "Summary of changes made by this import" file has been created.

   ![example](screenshots/summary.png)

5. You can view the summary if you want. Your import has NOT BEEN PERFORMED YET!

   ![example](screenshots/view-summary.png)

6. Return to the import-jobs table, select the import job we just created, and select the "Perform import" action from the actions drop down.

   ![example](screenshots/perform-import.png)

7. In a short time, your imported Winner object should show up in your Winners table.

   ![example](screenshots/new-winner.png)

### Performing an export

1. Perform the basic setup procedure described in the first section.

2. Open up the object list for your model in django admin, select the objects you wish to export, and select the `Export with stomp` admin action.

3. Select the file format and resource you want to use to export the data.

4. Save the model

5. You will receive an email when the export is done, click on the link in the email

6. Click on the link near the bottom of the page titled `Exported file`.

### Settings

- `IMPORT_EXPORT_STOMP_MODELS`
  **Required** Dict containing all the models that will be imported.

  ```python
    {
        "Name of your import": {
            "app_label": "fake_app",
            "model_name": "FakeModel",
            "resource": resource_importer(
                "tests.resources.fake_app.resources.FakeResource"
            ),  # optional -if not present will auto-create
        }
    }
  ```

- `IMPORT_EXPORT_STOMP_STORAGE`
  Storage class which import/export file field will use. Defaults to `None`.
  Example: `storages.backends.s3boto3.S3Boto3Storage`

- `IMPORT_EXPORT_STOMP_EXCLUDED_FORMATS`
  List of formats to exclude from import/export. Defaults to `[]`.
  Example: `["csv", "xlsx"]`

- `IMPORT_EXPORT_STOMP_PROCESSING_QUEUE`
  Name of the stomp queue that will be used to publish/consume the messages. Defaults to `/queue/django-import-export-stomp-runner`

- `IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST`
  Enables upload using presigned post url. Uses `boto3` and `django-storages`. Defaults to `False`.

- `IMPORT_EXPORT_STOMP_PRESIGNED_POST_EXPIRATION`
  Sets signed url expiration time. Defaults to `600`

- `IMPORT_EXPORT_STOMP_PRESIGNED_FOLDER`
  Prepends a path to the s3 key. Defaults to `""`

### Credits

`django-import-export-stomp` was based on [django-import-export-celery](https://github.com/auto-mat/django-import-export-celery) developed by the Czech non-profit [auto*mat z.s.](https://auto-mat.cz).
