from django.forms import FileInput


class SignedUrlFileInput(FileInput):
    template_name = "widgets/signed_url_file.html"
