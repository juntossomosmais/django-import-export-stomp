import json

from http import HTTPStatus

from botocore.client import Config
from django.conf import settings
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from import_export_stomp.utils import get_formats


@require_POST
# @staff_member_required
@csrf_exempt
def generate_presigned_post(request: HttpRequest) -> JsonResponse:
    if not getattr(settings, "IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST"):
        return JsonResponse(
            {"error": "IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST is set to false."},
            status=HTTPStatus.FAILED_DEPENDENCY,
        )

    try:
        import boto3
    except ImportError:
        return JsonResponse(
            {"error": "boto3 or django-storages required for this action."},
            status=HTTPStatus.FAILED_DEPENDENCY,
        )

    data = json.loads(request.body)

    filename, mimetype, allowed_formats = (
        data["filename"],
        data["mimetype"],
        get_formats(),
    )

    if mimetype not in [_format.CONTENT_TYPE for _format in allowed_formats]:
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
        config=Config(signature_version="s3v4"),
    )

    file_path = getattr(settings, "IMPORT_EXPORT_STOMP_PRESIGNED_FOLDER", "") + filename

    response = client.generate_presigned_post(
        getattr(settings, "AWS_STORAGE_BUCKET_NAME"),
        file_path,
        ExpiresIn=getattr(settings, "IMPORT_EXPORT_STOMP_PRESIGNED_POST_EXPIRATION"),
    )

    return JsonResponse(response, status=HTTPStatus.CREATED)
