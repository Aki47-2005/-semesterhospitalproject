from django.contrib import messages
from django.contrib.auth import login, logout
from django.db.models import ProtectedError, Sum
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from .forms import LoginForm, SignUpForm
from .models import Admission, Appointment, Bed, Bill, Doctor, Patients, Payment, Staff, Ward


RECORD_TYPES = {
    "patients": (Patients, "Patients"),
    "doctors": (Doctor, "Doctors"),
    "staff": (Staff, "Staff"),
    "wards": (Ward, "Wards"),
    "beds": (Bed, "Beds"),
    "admissions": (Admission, "Admissions"),
    "appointments": (Appointment, "Appointments"),
    "bills": (Bill, "Bills"),
    "payments": (Payment, "Payments"),
}

def _record_type(kind):
    return RECORD_TYPES.get(kind)


def index_view(request):
    patient_count = Patients.objects.count()
    doctor_count = Doctor.objects.count()
    appointment_count = Appointment.objects.count()
    admission_count = Admission.objects.count()
    staff_count = Staff.objects.count()
    ward_count = Ward.objects.count()
    bed_count = Bed.objects.count()
    bill_count = Bill.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
    recent_patients = Patients.objects.order_by("-pk")[:6]
    recent_payments = Payment.objects.select_related("bill", "bill__patient").order_by("-pk")[:7]

    return render(request, "index.html", {
        "patient_count": patient_count,
        "doctor_count": doctor_count,
        "appointment_count": appointment_count,
        "admission_count": admission_count,
        "staff_count": staff_count,
        "ward_count": ward_count,
        "bed_count": bed_count,
        "bill_count": bill_count,
        "total_revenue": total_revenue,
        "recent_patients": recent_patients,
        "recent_payments": recent_payments,
    })


def record_list(request, kind):
    record_type = _record_type(kind)
    if record_type is None:
        raise Http404("Unknown record type")
    model, title = record_type
    fields = [field for field in model._meta.fields if field.name != "id"]
    records = model.objects.order_by("pk")
    relation_fields = [field.name for field in model._meta.fields if field.is_relation]
    if relation_fields:
        records = records.select_related(*relation_fields)
    form_class = modelform_factory(model, fields="__all__")
    empty_form = form_class(auto_id="id_new_%s")
    rows = [
        (record, [getattr(record, field.name) for field in fields], form_class(instance=record, auto_id=f"id_{record.pk}_%s"))
        for record in records
    ]
    return render(request, "records.html", {
        "kind": kind,
        "title": title,
        "records": records,
        "fields": fields,
        "rows": rows,
        "empty_form": empty_form,
    })


def record_form(request, kind, pk=None):
    record_type = _record_type(kind)
    if record_type is None:
        raise Http404("Unknown record type")
    model, title = record_type
    instance = get_object_or_404(model, pk=pk) if pk is not None else None
    form_class = modelform_factory(model, fields="__all__")
    form = form_class(request.POST if request.method == "POST" else None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Record saved.")
        return redirect("records", kind=kind)
    return render(request, "record_form.html", {
        "kind": kind,
        "title": title,
        "form": form,
        "record": instance,
    })


def record_delete(request, kind, pk):
    record_type = _record_type(kind)
    if record_type is None:
        raise Http404("Unknown record type")
    model, title = record_type
    record = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        try:
            record.delete()
        except ProtectedError:
            messages.error(request, "This record is linked to other records and cannot be deleted yet.")
        else:
            messages.success(request, "Record deleted.")
        return redirect("records", kind=kind)
    return render(request, "record_confirm_delete.html", {
        "kind": kind,
        "title": title,
        "record": record,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("HOME")
    
    next_url = request.GET.get("next") or request.POST.get("next") or "HOME"
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()
    
    return render(request, "login.html", {
        "form": form,
        "next": next_url,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("HOME")
    
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created! Welcome to CarePoint, {user.get_full_name() or user.username}.")
            return redirect("HOME")
        else:
            messages.error(request, "Please correct the errors below to complete registration.")
    else:
        form = SignUpForm()
    
    return render(request, "signup.html", {
        "form": form,
    })


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")


