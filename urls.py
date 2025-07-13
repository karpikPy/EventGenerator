
from django.urls import path
from . import views

app_name = 'event_planner'

urlpatterns = [
    path('', views.event_list, name='event_list'), 
    path('create/', views.event_create, name='event_create'), 
    path('<int:pk>/', views.event_detail, name='event_detail'), 
    path('<int:pk>/update/', views.event_update, name='event_update'), 
    path('<int:pk>/delete/', views.event_delete, name='event_delete'), 
    path('<int:pk>/invite/', views.event_invite, name='event_invite'), 
    path('invitations/', views.invitation_list, name='invitation_list'), 
    path('invitations/<int:pk>/respond/', views.invitation_respond, name='invitation_respond'), 
]
