from collections import OrderedDict
from typing import Any, Dict, Optional

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, Textarea, TypedChoiceField, model_to_dict
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from django_tables2 import SingleTableView
from formtools.wizard.views import CookieWizardView
from material import Layout
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.apps.evalu.forms import (
    AgreementWidget,
    ComparisonGroupFormSet,
    CustomEvaluationItemFormSet,
    EvaluationFinishForm,
    EvaluationItemFormSet,
    EvaluationPartForm,
    EvaluationPhaseForm,
    PasswordForm,
    RegisterForEvaluationForm,
)
from aleksis.apps.evalu.models import (
    Answer,
    DoneEvaluation,
    EvaluationGroup,
    EvaluationPart,
    EvaluationPhase,
    EvaluationRegistration,
    EvaluationResult,
    QuestionType,
)
from aleksis.apps.evalu.tables import EvaluationPartTable, EvaluationPhaseTable
from aleksis.core.mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from aleksis.core.util.pdf import render_pdf


class EvaluationPartListView(PermissionRequiredMixin, SingleTableView):
    """Table of all extra marks."""

    model = EvaluationPart
    table_class = EvaluationPartTable
    permission_required = "evalu.view_evaluationparts_rule"
    template_name = "evalu/part/list.html"


@method_decorator(never_cache, name="dispatch")
class EvaluationPartCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for extra marks."""

    model = EvaluationPart
    form_class = EvaluationPartForm
    permission_required = "evalu.add_evaluationpart_rule"
    template_name = "evalu/part/create.html"
    success_message = _("The evaluation part has been created.")

    def get_success_url(self):
        return reverse("edit_evaluation_part", args=[self.object.pk])


@method_decorator(never_cache, name="dispatch")
class EvaluationPartDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """Delete view for extra marks."""

    model = EvaluationPart
    permission_required = "evalu.delete_evaluationpart_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("evaluation_parts")
    success_message = _("The evaluation part has been deleted.")


@method_decorator(never_cache, name="dispatch")
class EvaluationPartEditView(PermissionRequiredMixin, AdvancedEditView):
    model = EvaluationPart
    form_class = EvaluationPartForm
    success_message = _("The evaluation part and it's items have been updated successfully.")
    permission_required = "evalu.edit_evaluationpart_rule"
    template_name = "evalu/part/edit.html"

    def get_success_url(self):
        return reverse("edit_evaluation_part", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = EvaluationItemFormSet(self.request.POST or None, instance=self.object)
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return super().form_valid(form)


class EvaluationPhaseListView(PermissionRequiredMixin, SingleTableView):
    """View to list all evaluation phases."""

    model = EvaluationPhase
    table_class = EvaluationPhaseTable
    permission_required = "evalu.view_evaluationphases_rule"
    template_name = "evalu/phase/list.html"


class EvaluationPhaseDetailView(PermissionRequiredMixin, DetailView):
    """Detail view for evaluation phases."""

    model = EvaluationPhase
    permission_required = "evalu.view_evaluationphase_rule"
    template_name = "evalu/phase/detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["members"] = self.object.members_with_registration
        return context


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for evaluation phases."""

    model = EvaluationPhase
    form_class = EvaluationPhaseForm
    permission_required = "evalu.create_evaluationphase_rule"
    template_name = "evalu/phase/create.html"
    success_message = _("The evaluation phase has been created.")

    def get_success_url(self):
        return reverse("edit_evaluation_phase", args=[self.object.pk])


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """Delete view for evaluation phases."""

    model = EvaluationPhase
    permission_required = "evalu.delete_evaluationphase_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("evaluation_phases")
    success_message = _("The evaluation phase has been deleted.")


@method_decorator(never_cache, name="dispatch")
class EvaluationPhaseEditView(PermissionRequiredMixin, AdvancedEditView):
    model = EvaluationPhase
    form_class = EvaluationPhaseForm
    success_message = _("The evaluation phase has been updated.")
    permission_required = "evalu.edit_evaluationphase_rule"
    template_name = "evalu/phase/edit.html"

    def get_success_url(self):
        return reverse("evaluation_phase", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = ComparisonGroupFormSet(self.request.POST or None, instance=self.object)
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return super().form_valid(form)


class EvaluationPhaseOverviewView(PermissionRequiredMixin, ListView):
    """View to list all evaluation phases a user can register or is registered for."""

    model = EvaluationPhase
    permission_required = "evalu.view_evaluationphases_overview_rule"
    template_name = "evalu/list.html"

    def get_queryset(self):
        return EvaluationPhase.objects.for_person_with_registrations(self.request.user.person)


class DeleteDataView(PermissionRequiredMixin, DetailView):
    """View to delete data after a certain date."""

    model = EvaluationPhase
    permission_required = "evalu.delete_data_rule"
    template_name = "evalu/phase/delete_data.html"

    def post(self, request, *args, **kwargs):
        if request.POST.get("delete"):
            self.object = self.get_object()
            self.object.delete_data()
            messages.success(request, _("The data have been deleted."))
            return redirect("evaluation_phase", pk=self.object.pk)
        else:
            return self.get(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class RegisterForEvaluationView(PermissionRequiredMixin, DetailView):
    """View to register for an evaluation phase."""

    model = EvaluationPhase
    permission_required = "evalu.register_for_evaluation_rule"
    template_name = "evalu/registration/register.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = RegisterForEvaluationForm(self.request.POST or None)
        return context

    def get_queryset(self):
        return EvaluationPhase.objects.can_register(self.request.user.person)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        form = context["form"]

        if form.is_valid():
            data = form.cleaned_data
            registration = EvaluationRegistration.register(
                self.object, self.request.user.person, data["password"], data["delete_after_phase"]
            )
            registration.generate_privacy_form()
            messages.success(
                request, _("You have successfully registered yourself for the evaluation.")
            )
            return redirect("evaluation_registration", registration.pk)

        return self.render_to_response(context)


class EvaluationGroupMixin:
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.object.sync_evaluation_groups()
        context["possible_groups"] = self.object.evaluation_groups_with_stats

        return context


class RegistrationDetailView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.view_evaluationregistration_rule"
    template_name = "evalu/registration/detail.html"


@method_decorator(never_cache, name="dispatch")
class ManageEvaluationProcessView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.manage_evaluation_process_rule"
    template_name = "evalu/registration/manage.html"


@method_decorator(never_cache, name="dispatch")
class StartEvaluationForGroupView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = "evalu.start_evaluation_for_group_rule"
    model = EvaluationGroup

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.unlock()
        messages.success(
            request,
            _("The evaluation for the group {} has been successfully unlocked.").format(
                group.group_name
            ),
        )
        return redirect("manage_evaluation_process", group.registration.pk)


@method_decorator(never_cache, name="dispatch")
class StopEvaluationForGroupView(PermissionRequiredMixin, SingleObjectMixin, View):
    permission_required = "evalu.stop_evaluation_for_group_rule"
    model = EvaluationGroup

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.lock()
        messages.success(
            request,
            _("The evaluation for the group {} has been successfully locked.").format(
                group.group_name
            ),
        )
        return redirect("manage_evaluation_process", group.registration.pk)


class EvaluationsAsParticipantListView(PermissionRequiredMixin, ListView):
    permission_required = "evalu.view_evaluations_as_participant_rule"
    template_name = "evalu/participate/list.html"

    def get_queryset(self):
        now_date = timezone.now().date()
        person = self.request.user.person
        return (
            EvaluationGroup.objects.for_person_with_done_evaluations(person)
            .filter(registration__phase__evaluation_date_start__lte=now_date)
            .distinct()
        )


@method_decorator(never_cache, name="dispatch")
class EvaluationFormView(PermissionRequiredMixin, SingleObjectMixin, CookieWizardView):
    permission_required = "evalu.evaluate_person_rule"
    model = EvaluationGroup
    template_name = "evalu/participate/form.html"
    form_list = [EvaluationFinishForm]

    def __init__(self, *args, **kwargs):
        self.field_mapping = {}
        self.parts = {}
        super().__init__(*args, **kwargs)

    def get_form_list(self):
        form_list = self._build_forms(self.object)
        computed_form_list = OrderedDict()
        for i, form in enumerate(form_list):
            computed_form_list[str(i)] = form

        return computed_form_list

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parts"] = self.parts

        if self.steps.current != self.steps.last:
            context["part"] = self.parts[self.steps.index]

        # Get data for preview table (last step)
        if self.steps.current == self.steps.last:
            forms = []
            for i, form_key in enumerate(self.get_form_list()):
                form = self.get_form(
                    step=form_key,
                    data=self.storage.get_step_data(form_key),
                    files=self.storage.get_step_files(form_key),
                )

                # Skip the form if it has no fields (e. g. finish form)
                if not form.fields:
                    continue

                # Make sure cleaned_data is filled
                form.is_valid()

                form_data = []
                for key, value in form.fields.items():
                    value_to_show = form.cleaned_data.get(key)

                    # Use speaking value from choices if set
                    if getattr(value, "choices", None):
                        value_to_show = dict(value.choices).get(value_to_show, "–")

                    form_data.append((value.label, value_to_show))
                forms.append((self.parts[i], form_data))
            context["form_data"] = forms

        return context

    def _build_forms(self, group: Optional[EvaluationGroup] = None):
        forms = []

        for i, part in enumerate(EvaluationPart.objects.order_by("order")):
            self.parts[i] = part
            layout = []
            form_class_attrs = {}
            agreement_keys = []

            for item in part.get_items(group):
                field_name = f"item_{item.pk}"

                # Build different types of form fields
                if item.item_type == QuestionType.AGREEMENT:
                    field = TypedChoiceField(
                        coerce=int,
                        choices=Answer.choices,
                        label=item.question,
                        widget=AgreementWidget(),
                        required=not part.optional,
                    )
                    agreement_keys.append(field_name)
                elif item.item_type == QuestionType.FREE_TEXT:
                    field = CharField(
                        required=False, label=item.question, widget=Textarea(attrs={"rows": 4})
                    )
                else:
                    continue

                form_class_attrs[field_name] = field
                self.field_mapping[field_name] = item
                layout.append(field_name)

            def clean_method(self, part=part, agreement_keys=agreement_keys):  # noqa
                if part.optional:
                    agreement_data = [
                        self.cleaned_data.get(key)
                        for key in agreement_keys
                        if self.cleaned_data.get(key)
                    ]
                    if len(agreement_data) != len(agreement_keys) and len(agreement_data) != 0:
                        raise ValidationError(
                            _("You have to answer no or all questions in an optional part.")
                        )

            # Build final evaluation form
            form_class_attrs["layout"] = Layout(*layout)
            form = type(Form)(f"EvaluationForm{part.pk}", (Form,), form_class_attrs)
            form.clean = clean_method

            forms.append(form)

        # Add dummy form for review page (just to make sure that it appears)
        forms.append(EvaluationFinishForm)
        self.parts[len(forms) - 1] = {"name": _("Finish")}

        return forms

    def done(self, form_list, **kwargs):
        # Prevent errors with doubled evaluations
        if DoneEvaluation.objects.filter(
            group=self.object, evaluated_by=self.request.user.person
        ).exists():
            return redirect("evaluations_as_participant")

        done_evaluation = DoneEvaluation(group=self.object, evaluated_by=self.request.user.person)
        for form in form_list:
            for key, value in form.cleaned_data.items():
                item = self.field_mapping[key]
                result = EvaluationResult(group=self.object, item=item)
                result.store_result(value)
                result.save()
                result.add_comparison_results(value)
        done_evaluation.save()
        messages.success(
            self.request,
            _("The evaluation has been finished. Thank you for doing this evaluation!"),
        )
        return redirect("evaluations_as_participant")


@method_decorator(never_cache, name="dispatch")
class FinishEvaluationView(PermissionRequiredMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.finish_evaluation_rule"
    template_name = "evalu/registration/finish.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "finish" in request.POST:
            self.object.finish()
            return redirect("evaluation_phases_overview")

        return self.get(request, *args, **kwargs)


@method_decorator(never_cache, name="dispatch")
class EvaluationResultsView(PermissionRequiredMixin, EvaluationGroupMixin, DetailView):
    model = EvaluationRegistration
    permission_required = "evalu.view_evaluation_results_rule"
    template_name = "evalu/password.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["as_pdf"] = self.kwargs.get("as_pdf", False)

        self.form = PasswordForm(self.request.POST or None)
        context["form"] = self.form

        return context

    def post(self, request, as_pdf: bool, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.form.is_valid():
            password = self.form.cleaned_data["password"]
            keys = self.object.keys

            try:
                private_key = keys.get_private_key(password)
            except ValueError:
                messages.error(
                    request,
                    _(
                        "There was an error with decrypting the data. "
                        "Please check if you have entered the correct password."
                    ),
                )
                return self.render_to_response(context)
        else:
            return self.render_to_response(context)

        # Result calculation
        groups = self.object.groups_with_done_evaluations.prefetch_related("results")
        context["groups"] = groups

        all_results = []
        for group in groups:
            results_per_group = {}
            results_per_group["choices"] = {key: value for key, value in Answer.choices}
            results_per_group["average"] = group.get_average_results(private_key)
            results_per_group["comparison"] = group.get_comparison_results()
            results_per_group["frequency"] = group.get_frequency_results(private_key)
            results_per_group["free_text"] = group.get_free_text_results(private_key)

            by_part = OrderedDict()
            for part in EvaluationPart.objects.order_by("order"):
                by_part[part.id] = {
                    "part": model_to_dict(part),
                    "results": [],
                    "average_results": [],
                }
                for item in part.get_items(group):
                    # Agreement result
                    if item.item_type == QuestionType.AGREEMENT:
                        result = group.get_frequency_result(item, private_key)
                        by_part[part.id]["results"].append(result)

                    # Free text result
                    elif item.item_type == QuestionType.FREE_TEXT:
                        result = group.get_free_text_result(item, private_key)
                        by_part[part.id]["results"].append(result)

            for result in results_per_group["average"]:
                part_id = result["part"]["id"]
                by_part.setdefault(part_id, {"part": result["part"], "results": []})
                by_part[part_id]["average_results"].append(result)
            results_per_group["results_by_part"] = by_part

            all_results.append((model_to_dict(group), results_per_group))

        context["results"] = all_results

        if as_pdf:
            return render_pdf(request, "evalu/results_pdf.html", context)

        return render(request, "evalu/results.html", context)


@method_decorator(never_cache, name="dispatch")
class CustomEvaluationItemsEditView(PermissionRequiredMixin, DetailView):
    model = EvaluationGroup
    permission_required = "evalu.edit_custom_evaulation_items_for_group_rule"
    template_name = "evalu/registration/edit_custom_items.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = CustomEvaluationItemFormSet(self.request.POST or None, instance=self.object)
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.get_context_data(**kwargs)
        if self.formset.is_valid():
            self.formset.instance = self.object
            self.formset.save()
            messages.success(
                request, _("The custom evaluation items have been saved successfully.")
            )
        #       else:
        #     return self.form_invalid(form)
        #
        return super().get(request, *args, **kwargs)
