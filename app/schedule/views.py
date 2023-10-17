from django.shortcuts import render, redirect, get_object_or_404
from .models import Club, Dienstplan, Employee, Shift, OpeningTime
from django.contrib.auth.models import User
from .forms import EmployeeForm, ClubForm, OpeningTimeForm, DienstplanForm
from django.contrib import messages
from django.views import View
from django.utils import timezone
from . generate_binary_schedule import employee_scheduling
from . save_shifts_to_database import save_shifts_to_database
from rest_framework import viewsets
from .serializers import ShiftSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


def admin_dashboard(request):
    clubs = Club.objects.all()
    dienstplanes = Dienstplan.objects.all()
    employees = Employee.objects.all()
    shifts = Shift.objects.all()

    context = {
        'clubs': clubs,
        'dienstplanes': dienstplanes,
        'employees': employees,
        'shifts': shifts
    }

    return render(request, 'schedule/admin_dashboard.html', context)


class CreateDienstplanView(View):
    template_name = 'schedule/create_schedule.html'

    def get(self, request, *args, **kwargs):
        form = DienstplanForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = DienstplanForm(request.POST)
        if form.is_valid():
            dienstplan = form.save(commit=False)
            if dienstplan.year is None:
                dienstplan.year = timezone.now().year
            dienstplan.save()

            employees = Employee.objects.all()
            employee_ids = [e.id for e in employees]
            employee_id_to_idx = {id: idx for idx, id in enumerate(employee_ids)}

            employee_weekly_hours = [e.weekly_hours for e in employees]
            #Schichlängen:
            #n = dienstplan.minimale_arbeitszeit
            #max_blocks = dienstplan.maximale_arbeitszeit
            # Beispielwerte für Strafen
            penalty = 13
            overtime_penalty = 5
            prob, x, u = employee_scheduling(dienstplan.year, dienstplan.month, dienstplan.club_id, employee_id_to_idx, employee_weekly_hours, penalty, overtime_penalty, n=5, max_blocks=8)
            save_shifts_to_database(prob, x, u, dienstplan, employee_id_to_idx)

            return render(request, self.template_name, {
                'form': form,

                'dienstplan_created': True
            })
        return render(request, self.template_name, {'form': form})


def view_dienstplan(request):
    return render(request, 'schedule/dienstplan.html', {})


class ManageEmployeeView(View):
    template_name = 'schedule/manage_employee.html'

    def get(self, request, employee_id=None):
        employee = get_object_or_404(Employee, pk=employee_id) if employee_id else None
        form = EmployeeForm(instance=employee)
        employees = Employee.objects.all()
        return render(request, self.template_name, {'form': form, 'employees': employees})

    def post(self, request, employee_id=None):
        employee = get_object_or_404(Employee, pk=employee_id) if employee_id else None
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']  # Eingegebenes Passwort auslesen

            user, created = User.objects.get_or_create(username=username, defaults={'email': username})
            if created or password:  # Wenn der Benutzer neu ist oder ein Passwort eingegeben wurde
                user.set_password(password)
                user.save()

            employee.user = user
            employee.save()

            messages.success(request, f'Mitarbeiter {employee.first_name} wurde erfolgreich gespeichert!')
            return redirect('manage_employee')
        else:
            employees = Employee.objects.all()
            return render(request, self.template_name, {'form': form, 'employees': employees})


class DeleteEmployeeView(View):
    template_name = 'schedule/confirm_delete.html'

    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        context = {
            'object': employee,
            'object_name': 'Employee',
            'return_url': 'manage_employee'
        }
        return render(request, self.template_name, context)

    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, pk=employee_id)
        employee.delete()
        return redirect('manage_employee')


class ManageClubView(View):
    template_name = 'schedule/manage_club.html'

    def get(self, request, club_id=None):
        clubs = Club.objects.prefetch_related('opening_times').all()
        if club_id:
            club = get_object_or_404(Club, pk=club_id)
            form = ClubForm(instance=club)
        else:
            form = ClubForm()
        return render(request, self.template_name, {'form': form, 'clubs': clubs})

    def post(self, request, club_id=None):
        if club_id:
            club = get_object_or_404(Club, pk=club_id)
            form = ClubForm(request.POST, instance=club)
        else:
            form = ClubForm(request.POST)
        if form.is_valid():
            saved_club = form.save()
            return redirect('manage_opening_time', club_id=saved_club.id)
        return render(request, self.template_name, {'form': form})


class DeleteClubView(View):
    template_name = 'schedule/confirm_delete.html'

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        context = {
            'object': club,
            'object_name': 'Club',
            'return_url': 'manage_club'
            # Oder die URL, zu der zurückgekehrt werden soll, wenn "Abbrechen" ausgewählt ist
        }
        return render(request, self.template_name, context)

    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        club.delete()
        return redirect('admin_dashboard')


class ManageOpeningTimeView(View):
    template_name = 'schedule/manage_opening_time.html'

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        form = OpeningTimeForm(initial={'club': club})
        return render(request, self.template_name, {'form': form, 'club': club})

    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        form = OpeningTimeForm(request.POST)
        if form.is_valid():
            opening_time = form.save(commit=False)
            opening_time.club = club
            opening_time.save()
            return redirect('manage_club')
        return render(request, self.template_name, {'form': form, 'club': club})


class EditOpeningTimeView(View):
    template_name = 'schedule/manage_opening_time.html'

    def get(self, request, opening_time_id):
        opening_time = get_object_or_404(OpeningTime, pk=opening_time_id)
        form = OpeningTimeForm(instance=opening_time)
        return render(request, self.template_name, {'form': form, 'opening_time': opening_time})

    def post(self, request, opening_time_id):
        opening_time = get_object_or_404(OpeningTime, pk=opening_time_id)
        form = OpeningTimeForm(request.POST, instance=opening_time)
        if form.is_valid():
            form.save()
            return redirect('manage_club')
        return render(request, self.template_name, {'form': form, 'opening_time': opening_time})


class DeleteOpeningTimeView(View):
    template_name = 'schedule/confirm_delete.html'

    def get(self, request, opening_time_id):
        opening_time = get_object_or_404(OpeningTime, pk=opening_time_id)
        context = {
            'object': opening_time,
            'object_name': 'Öffnungszeit',
            'return_url': 'manage_club'
        }
        return render(request, self.template_name, context)

    def post(self, request, opening_time_id):
        opening_time = get_object_or_404(OpeningTime, pk=opening_time_id)
        opening_time.delete()
        return redirect('manage_club')


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
