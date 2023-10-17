from django.urls import path, include
from . import views
from .views import (ManageClubView, DeleteClubView, ManageOpeningTimeView, EditOpeningTimeView, DeleteOpeningTimeView,
                    ManageEmployeeView, DeleteEmployeeView, CreateDienstplanView)
from rest_framework.routers import DefaultRouter
from .views import ShiftViewSet

router = DefaultRouter()
router.register(r'shifts', ShiftViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_schedule', CreateDienstplanView.as_view(), name='create_schedule'),
    path('manage_employee/', ManageEmployeeView.as_view(), name='manage_employee'),
    path('manage_employee/<int:employee_id>/', ManageEmployeeView.as_view(), name='edit_employee'),
    path('delete_employee/<int:employee_id>/', DeleteEmployeeView.as_view(), name='delete_employee'),
    path('manage_club/', ManageClubView.as_view(), name='manage_club'),
    path('manage_club/<int:club_id>/', ManageClubView.as_view(), name='manage_club_edit'),
    path('delete_club/<int:club_id>/', DeleteClubView.as_view(), name='delete_club'),
    path('add_opening_time/<int:club_id>/', ManageOpeningTimeView.as_view(), name='add_opening_time'),
    path('manage_opening_time/<int:club_id>/', ManageOpeningTimeView.as_view(), name='manage_opening_time'),
    path('edit_opening_time/<int:opening_time_id>/', EditOpeningTimeView.as_view(), name='edit_opening_time'),
    path('delete_opening_time/<int:opening_time_id>/', DeleteOpeningTimeView.as_view(), name='delete_opening_time'),
    path('Dienstplan-Admin', views.view_dienstplan, name='dienstplan'),
]
