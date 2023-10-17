from django import forms
from .models import Employee, Club, OpeningTime, Dienstplan
from django.core.exceptions import ValidationError


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'club', 'weekly_hours', 'color', 'password']


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name']


class OpeningTimeForm(forms.ModelForm):
    class Meta:
        model = OpeningTime
        fields = ['weekday', 'date', 'opening_time', 'closing_time']


MONTH_CHOICES = [
    (1, 'Jänner'),
    (2, 'Februar'),
    (3, 'März'),
    (4, 'April'),
    (5, 'Mai'),
    (6, 'Juni'),
    (7, 'Juli'),
    (8, 'August'),
    (9, 'September'),
    (10, 'Oktober'),
    (11, 'November'),
    (12, 'Dezember'),
]


class DienstplanForm(forms.ModelForm):
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=True)
    year = forms.IntegerField(required=False)

    class Meta:
        model = Dienstplan
        fields = ['club', 'month', 'year', 'minimale_arbeitszeit', 'maximale_arbeitszeit']
