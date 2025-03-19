import importlib
import json

from http import HTTPStatus
from importlib import util

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from import_export_stomp.utils import get_formats


@require_POST
@staff_member_required
def generate_presigned_post(request: HttpRequest) -> JsonResponse:
    if not getattr(settings, "IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST"):
        return JsonResponse(
            {"error": "IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST is set to false."},
            status=HTTPStatus.FAILED_DEPENDENCY,
        )

    boto3_spec = util.find_spec("boto3")
    storages_spec = util.find_spec("storages")

    if not boto3_spec and not storages_spec:
        return JsonResponse(
            {"error": "boto3 and django-storages required for this action."},
            status=HTTPStatus.FAILED_DEPENDENCY,
        )

    # Import boto3
    boto3 = importlib.import_module("boto3")

    # Import Config from botocore.config
    botocore = importlib.import_module("botocore")
    botocore_config = botocore.config.Config

    data = json.loads(request.body)

    filename, mimetype, allowed_formats = (
        data["filename"],
        data["mimetype"],
        [_format.CONTENT_TYPE for _format in get_formats()],
    )

    if mimetype not in allowed_formats:
        return JsonResponse(
            {
                "error": f"File format {mimetype} is not allowed. Accepted formats: {allowed_formats}"
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    client = boto3.client(
        "s3",
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        region_name=getattr(settings, "AWS_DEFAULT_REGION", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
        config=botocore_config(signature_version="s3v4"),
    )

    file_path = getattr(settings, "IMPORT_EXPORT_STOMP_PRESIGNED_FOLDER", "") + filename

    response = client.generate_presigned_post(
        getattr(settings, "AWS_STORAGE_BUCKET_NAME"),
        file_path,
        ExpiresIn=getattr(
            settings, "IMPORT_EXPORT_STOMP_PRESIGNED_POST_EXPIRATION", 600
        ),
    )

    return JsonResponse(response, status=HTTPStatus.CREATED)
