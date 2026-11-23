from django.urls import path
from reconcile.views import disagreements, organizations

urlpatterns = [
    path("api/orgs/", organizations, name="organizations"),
    path("api/disagreements/", disagreements, name="disagreements"),
]
