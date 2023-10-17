from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Create your models here.


class Club(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class OpeningTime(models.Model):
    WEEKDAYS = [
        (0, 'Montag'),
        (1, 'Dienstag'),
        (2, 'Mittwoch'),
        (3, 'Donnerstag'),
        (4, 'Freitag'),
        (5, 'Samstag'),
        (6, 'Sonntag'),
    ]

    club = models.ForeignKey(Club, related_name='opening_times', on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=WEEKDAYS, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        unique_together = ['club', 'weekday', 'date']
        ordering = ['weekday']

    def __str__(self):
        if self.date:
            return f"{self.date} {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return f"{self.get_weekday_display()} {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.SmallIntegerField(primary_key=True, default=0)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    weekly_hours = models.FloatField(help_text="Bitte geben Sie die wöchentliche Arbeitszeit in Stunden ein.")
    color = models.CharField(null=True, max_length=7, help_text="Hinterlegen Sie den Farbcode in #hex")

    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class NonWorkingDay(models.Model):
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='nonworking_days')
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} | {self.date} - {self.note}"


class ShiftPreference(models.Model):
    EMPLOYEE_PREFERENCE = [
        ('P', 'Preferred'),
        ('N', 'Not Available'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    day_of_week = models.IntegerField(null=True, blank=True)  # 0: Monday, 1: Tuesday, ..., 6: Sunday
    preference_type = models.CharField(max_length=1, choices=EMPLOYEE_PREFERENCE)

    def __str__(self):
        return f"{self.employee.first_name} {self.day_of_week} {self.start_time} {self.end_time}"


class Dienstplan(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1: January, 2: February, ..., 12: December
    year = models.IntegerField()
    minimale_arbeitszeit = models.PositiveSmallIntegerField()
    maximale_arbeitszeit = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.get_month_display()} {self.year} - {self.club.name}"

    def get_month_display(self):
        # Dies könnte eine Funktion sein, die eine lesbarere Darstellung des Monats liefert.
        return [
            "January", "February", "March", "April", "May",
            "June", "July", "August", "September", "October",
            "November", "December"
        ][self.month - 1]


class Shift(models.Model):
    dienstplan = models.ForeignKey(Dienstplan, on_delete=models.CASCADE, related_name='shifts')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_month = models.IntegerField()  # 1 to 31


