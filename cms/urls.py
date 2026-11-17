from django.urls import path

from . import views

app_name = "cms"

urlpatterns = [
    path("", views.home, name="home"),
    path("security/two-factor/", views.two_factor_switch, name="two_factor_switch"),
    path("messages/", views.inbox, name="inbox"),
    path("messages/read-all/", views.inbox_mark_all, name="inbox_mark_all"),
    path("messages/<int:pk>/", views.message_detail, name="message"),
    path("content/<slug:slug>/", views.section, name="section"),
    path("items/<slug:slug>/add/", views.item_edit, name="item_add"),
    path("items/<slug:slug>/<int:pk>/", views.item_edit, name="item_edit"),
    path("items/<slug:slug>/<int:pk>/delete/", views.item_delete, name="item_delete"),
    path("items/<slug:slug>/<int:pk>/toggle/", views.item_toggle, name="item_toggle"),
    path("items/<slug:slug>/<int:pk>/<str:direction>/", views.item_move, name="item_move"),
]
