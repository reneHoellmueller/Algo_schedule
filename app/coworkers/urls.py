from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import coworker_dashboard, ShiftPreferenceViewSet, NonWorkingDayViewSet, create_shift_preference, non_working_days, dienstplan_coworker
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'shift_preference', ShiftPreferenceViewSet)
router.register(r'nonworkingdays', NonWorkingDayViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('login/', auth_views.LoginView.as_view(template_name='coworkers/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('coworker_dashboard/', coworker_dashboard, name='coworker_dashboard'),
    path('coworker_dashboard/shift_preference', create_shift_preference, name='create_shift_preference'),
    path('submit_non_workingdays', non_working_days, name='non_working_days'),
    path('dienstplan/Mitarbeiter', dienstplan_coworker, name='dienstplan_coworker'),
    # ... (Ihre anderen URLs)
]
