from django.shortcuts import render
from rest_framework import viewsets
from schedule.models import ShiftPreference, NonWorkingDay
from .serializers import ShiftPreferenceSerializer, NonWorkingDaySerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


# Create your views here.


def coworker_dashboard(request):
    return render(request, 'coworkers/coworker_dashboard.html', {})


def dienstplan_coworker(request):
    return render(request, 'coworkers/dienstplan.html', {})


def create_shift_preference(request):
    shift_preferences = ShiftPreference.objects.filter(employee=request.user.employee)
    return render(request, 'coworkers/shift_preference_form.html', {'shift_preferences': shift_preferences})


def non_working_days(request):
    return render(request, 'coworkers/non_working_days.html', {})


class ShiftPreferenceViewSet(viewsets.ModelViewSet):
    queryset = ShiftPreference.objects.all()
    serializer_class = ShiftPreferenceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save(employee=instance.employee)


class NonWorkingDayViewSet(viewsets.ModelViewSet):
    queryset = NonWorkingDay.objects.all()
    serializer_class = NonWorkingDaySerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save(employee=instance.employee)
