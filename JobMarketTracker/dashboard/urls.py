from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard-index'),
    path('api/data/', views.api_data, name='dashboard-api-data'),
]

