from django.conf.urls import url
from . import happyPhone

urlpatterns = [
    url(r'phone/$', happyPhone.getDisplayPhone, name='graph'),
]
