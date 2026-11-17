from django.contrib import admin
#register our models here
from .models import Admission, Appointment, Bed, Bill, Doctor, Patients, Payment, Staff, Ward


@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ("name", "birth_date", "gender", "contact", "condition")
    search_fields = ("name", "contact", "condition")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "contact", "email")
    search_fields = ("name", "specialty")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "contact", "email")
    search_fields = ("name", "role")


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "ward", "status")
    list_filter = ("ward", "status")


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("patient", "bed", "admitted_at", "discharged_at")
    list_filter = ("bed__ward",)
    search_fields = ("patient__name", "bed__bed_number")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "scheduled_at")
    list_filter = ("scheduled_at",)
    search_fields = ("patient__name", "doctor__name")


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("patient", "description", "amount", "issued_at", "paid")
    list_filter = ("paid", "issued_at")
    search_fields = ("patient__name", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("bill", "amount", "method", "paid_at", "reference")
    list_filter = ("method", "paid_at")
    search_fields = ("reference", "bill__patient__name")
