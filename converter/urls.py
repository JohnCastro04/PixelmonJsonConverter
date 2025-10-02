from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.index, name='index'),
    path('convert-file/', views.convert_single_file, name='convert_file'),
    path('convert-zip/', views.convert_zip_file, name='convert_zip'),
    path('convert-text/', views.convert_text_input, name='convert_text'),
    path('help/', views.help_view, name='help'),
]