from django.contrib import admin
from edc_action_item import action_fieldset_tuple
from edc_lab_panel.panels import blood_glucose_panel
from edc_lab_results.admin import BloodResultsModelAdminMixin
from edc_lab_results.fieldsets import BloodResultFieldset
from edc_model_admin.history import SimpleHistoryAdmin

from ...admin_site import meta_subject_admin
from ...forms import BloodResultsGluForm
from ...models import BloodResultsGlu
from ..modeladmin import CrfModelAdminMixin

# TODO: add is poc? YES


@admin.register(BloodResultsGlu, site=meta_subject_admin)
class BloodResultsGluAdmin(
    BloodResultsModelAdminMixin, CrfModelAdminMixin, SimpleHistoryAdmin
):
    form = BloodResultsGluForm
    fieldsets = BloodResultFieldset(
        blood_glucose_panel,
        extra_fieldsets=[
            (2, ("Fasting", {"fields": ["fasting"]})),
            (-1, action_fieldset_tuple),
        ],
    ).fieldsets

    radio_fields = {
        "fasting": admin.VERTICAL,
        "results_abnormal": admin.VERTICAL,
        "results_reportable": admin.VERTICAL,
    }
