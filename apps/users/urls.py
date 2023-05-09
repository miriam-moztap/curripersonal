from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateListUser.as_view()),
    path('profile/', views.UpdateUser.as_view()),
    path('<int:id>/', views.ListUpdateDeleteUser.as_view()),
]
