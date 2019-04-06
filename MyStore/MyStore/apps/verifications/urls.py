from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^image_codes/(?P<image_code_id>.+)/$', views.ImageCodeAPIView.as_view()),
    re_path(r'^sms_codes/(?P<mobile>1[3456789]\d{9})/$', views.SMSCodeGAPIView.as_view()),
]
