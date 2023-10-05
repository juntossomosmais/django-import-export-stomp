from django.urls import path

from import_export_stomp.views import generate_presigned_post

urlpatterns = [
    path(
        "import-export-stomp/presigned-url/",
        generate_presigned_post,
        name="import_export_stomp_presigned_url",
    ),
]
