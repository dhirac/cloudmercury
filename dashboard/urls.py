from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("services/", views.services, name="services"),
    path("services/<int:pk>/", views.service_detail, name="service"),
    path("services/order/", views.order, name="order"),
    path("projects/", views.projects, name="projects"),
    path("marketing/", views.campaigns, name="campaigns"),
    path("billing/", views.billing, name="billing"),
    path("support/", views.support, name="support"),
    path("support/<int:pk>/", views.ticket, name="ticket"),
]
