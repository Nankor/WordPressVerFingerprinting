from django.conf.urls import url
import views

urlpatterns = [
    url(r'^detect/$', views.detectversion)
]