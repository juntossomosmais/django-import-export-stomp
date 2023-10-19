from typing import Any
from typing import Optional

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from import_export_stomp import admin_actions
from import_export_stomp.models import ExportJob
from import_export_stomp.models import ImportJob
from import_export_stomp.widgets import SignedUrlFileInput

IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST = getattr(
    settings, "IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST", False
)


class JobWithStatusMixin:
    @admin.display(description=_("Job status info"))
    def job_status_info(self, obj):
        job_status = cache.get(self.direction + "_job_status_%s" % obj.pk)
        if job_status:
            return job_status
        else:
            return obj.job_status


class ImportJobForm(forms.ModelForm):
    model = forms.ChoiceField(label=_("Name of model to import to"))
    signed_url_file_key = forms.CharField(
        max_length=255,
        required=True,
    )

    class Meta:
        model = ImportJob
        fields = [
            "file",
            "processing_initiated",
            "imported",
            "format",
            "change_summary",
            "errors",
            "model",
            "job_status",
            "signed_url_file_key",
        ]
        widgets = {
            "file": SignedUrlFileInput(attrs={"id": "signed_url_file_input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["model"].choices = [
                (x, x)
                for x in getattr(settings, "IMPORT_EXPORT_STOMP_MODELS", {}).keys()
            ]
            self.fields["format"].widget = forms.Select(
                choices=self.instance.get_format_choices()
            )

            self.fields["signed_url_file_key"].widget.attrs["style"] = "display: none;"
            self.fields["signed_url_file_key"].widget.attrs["readonly"] = True

        if (
            IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST
            and self.changed_data
            and not self.instance.pk
        ):
            del self.fields["file"]
        elif not IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST:
            self.fields["signed_url_file_key"].required = False

    def save(self, commit: bool = True) -> Any:
        if IMPORT_EXPORT_STOMP_USE_PRESIGNED_POST:
            self.instance.file = self.data["signed_url_file_key"]
        return super().save(commit)


@admin.register(ImportJob)
class ImportJobAdmin(JobWithStatusMixin, admin.ModelAdmin):
    direction = "import"
    form = ImportJobForm
    list_display = (
        "model",
        "job_status_info",
        "file",
        "change_summary",
        "imported",
        "author",
        "updated_by",
    )
    readonly_fields = (
        "job_status_info",
        "change_summary",
        "imported",
        "errors",
        "author",
        "updated_by",
        "processing_initiated",
    )
    exclude = ("job_status",)

    list_filter = ("model", "imported")

    actions = (
        admin_actions.run_import_job_action,
        admin_actions.run_import_job_action_dry,
    )

    def has_change_permission(
        self, request: HttpRequest, obj: Optional[ImportJob] = None
    ) -> bool:
        return False


class ExportJobForm(forms.ModelForm):
    class Meta:
        model = ExportJob
        exclude = ("site_of_origin",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(self.instance, "processing_initiated", True):
            self.fields["resource"].widget = forms.Select(
                choices=self.instance.get_resource_choices()
            )
            self.fields["format"].widget = forms.Select(
                choices=self.instance.get_format_choices()
            )


@admin.register(ExportJob)
class ExportJobAdmin(JobWithStatusMixin, admin.ModelAdmin):
    direction = "export"
    form = ExportJobForm
    list_display = (
        "model",
        "app_label",
        "file",
        "job_status_info",
        "author",
        "updated_by",
    )
    readonly_fields = (
        "job_status_info",
        "author",
        "updated_by",
        "app_label",
        "model",
        "file",
        "processing_initiated",
    )
    exclude = ("job_status",)

    list_filter = ("model",)

    def has_add_permission(
        self, request: HttpRequest, obj: Optional[ExportJob] = None
    ) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: Optional[ExportJob] = None
    ) -> bool:
        if getattr(obj, "processing_initiated", True):
            return False

        return True

    actions = (admin_actions.run_export_job_action,)
