from django.contrib import admin
from django.urls import path
from . import views
from . import admin_view

urlpatterns = [
    path('', views.home),
    path('add/<str:pk1>/<str:pk2>', views.add_new),
    path('dsp/<str:pk>', views.view),
    path('dsp/<str:pk>/', views.view),
    path('logout', views.logout),
    path('save/<str:pk>/', views.save_new),
    path("update/<str:pk1>/<str:pk2>/", views.update),
    path("delete/<str:pk1>/<str:pk2>", views.delete),
    path('view/<str:pk1>/<str:pk2>', views.view_2),
    path("gen_pdf/<str:pk1>/<str:pk2>", views.gen_pdf),
    path("gen_csv/<str:pk1>/<str:pk2>", views.gen_csv),


    path("save_in_admin/<str:pk>/", admin_view.save_in_admin),
    path("show_message", admin_view.show_message),


]
