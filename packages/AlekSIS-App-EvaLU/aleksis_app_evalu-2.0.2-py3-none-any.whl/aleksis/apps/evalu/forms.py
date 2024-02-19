from django import forms
from django.core.exceptions import ValidationError
from django.forms import RadioSelect
from django.utils.translation import gettext as _

from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from material import Fieldset, Layout, Row, Span2, Span3, Span5, Span6, Span8

from aleksis.apps.evalu.models import (
    ComparisonGroup,
    CustomEvaluationItem,
    EvaluationGroup,
    EvaluationItem,
    EvaluationPart,
    EvaluationPhase,
)


class EvaluationPartForm(forms.ModelForm):
    class Meta:
        model = EvaluationPart
        fields = ["name", "order", "optional"]


class EvaluationItemForm(forms.ModelForm):
    layout = Layout(
        Row(Span2("order"), Span3("item_type"), Span5("name"), Span2("DELETE")), Row("question")
    )

    class Meta:
        model = EvaluationItem
        fields = ["order", "name", "question", "item_type"]


EvaluationItemFormSet = forms.inlineformset_factory(
    EvaluationPart, EvaluationItem, form=EvaluationItemForm, min_num=1
)


class CustomEvaluationItemForm(forms.ModelForm):
    layout = Layout(
        Row(Span8("part"), Span2("order"), Span2("DELETE")),
        Row(
            Span6("item_type"),
            Span6("name"),
        ),
        Row("question"),
    )

    class Meta:
        model = CustomEvaluationItem
        fields = ["part", "order", "name", "question", "item_type"]


CustomEvaluationItemFormSet = forms.inlineformset_factory(
    EvaluationGroup, CustomEvaluationItem, form=CustomEvaluationItemForm, min_num=0
)


class EvaluationPhaseForm(forms.ModelForm):
    layout = Layout(
        Fieldset(_("Base data"), Row("name"), Row("evaluated_group")),
        Fieldset(
            _("Time range"),
            Row("registration_date_start", "registration_date_end"),
            Row("evaluation_date_start", "evaluation_date_end"),
        ),
        Fieldset(_("Additional data"), Row("privacy_notice")),
    )

    class Meta:
        model = EvaluationPhase
        fields = [
            "name",
            "evaluated_group",
            "registration_date_start",
            "registration_date_end",
            "evaluation_date_start",
            "evaluation_date_end",
            "privacy_notice",
        ]
        widgets = {
            "evaluated_group": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            )
        }


class ComparisonGroupForm(forms.ModelForm):
    layout = Layout(
        Row(Span5("name"), Span5("groups"), Span2("DELETE")),
    )

    class Meta:
        model = ComparisonGroup
        fields = ["name", "groups"]
        widgets = {
            "groups": ModelSelect2MultipleWidget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            )
        }


ComparisonGroupFormSet = forms.inlineformset_factory(
    EvaluationPhase, ComparisonGroup, form=ComparisonGroupForm, min_num=0
)


class RegisterForEvaluationForm(forms.Form):
    layout = Layout(Row("consent"), Row("delete_after_phase"))
    consent = forms.BooleanField(
        required=True,
        label=_(
            "I hereby declare that I agree that my data may be collected "
            "and processed in the above sense within the context of EvaLU."
        ),
        widget=forms.CheckboxInput(attrs={"class": "filled-in"}),
    )
    delete_after_phase = forms.BooleanField(
        initial=False,
        required=False,
        label=_("My data should be deleted after each evaluation phase."),
        widget=forms.CheckboxInput(attrs={"class": "filled-in"}),
    )
    password = forms.CharField(
        required=True, label=_("Evaluation password"), widget=forms.PasswordInput()
    )
    password_confirm = forms.CharField(
        required=True, label=_("Confirm evaluation password"), widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["password"] != cleaned_data["password_confirm"]:
            raise ValidationError("You have entered two different passwords.")


class AgreementWidget(RadioSelect):
    pass


class EvaluationFinishForm(forms.Form):
    pass


class PasswordForm(forms.Form):
    password = forms.CharField(
        required=True, label=_("Evaluation password"), widget=forms.PasswordInput()
    )
