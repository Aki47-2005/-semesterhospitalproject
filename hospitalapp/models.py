from django.core.validators import MinValueValidator
from django.db import models


class Patients(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=20)
    contact = models.CharField(max_length=50)
    condition = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialty})"


class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.role}"


class Ward(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Bed(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        MAINTENANCE = "maintenance", "Maintenance"

    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name="beds")
    bed_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("ward", "bed_number"), name="unique_bed_number_per_ward")]

    def __str__(self):
        return f"{self.ward} - Bed {self.bed_number}"


class Admission(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.PROTECT, related_name="admissions")
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name="admissions")
    admitted_at = models.DateTimeField()
    discharged_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient} admitted {self.admitted_at:%Y-%m-%d}"


class Appointment(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    scheduled_at = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.scheduled_at:%Y-%m-%d %H:%M}"


class Bill(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.PROTECT, related_name="bills")
    issued_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Bill #{self.pk} - {self.patient}"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        MOBILE_MONEY = "mobile_money", "Mobile money"
        INSURANCE = "insurance", "Insurance"

    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, related_name="payments")
    paid_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=20, choices=Method.choices)
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment #{self.pk} for bill #{self.bill_id}"
