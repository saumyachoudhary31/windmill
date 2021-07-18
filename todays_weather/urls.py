
from django.urls import path
from todays_weather import views

urlpatterns = [
    path('weather/',views.home ),
    path('maintaince/',views.maint),
    path('graph/',views.graph),
    path('weathers/',views.curr),
    
    
]