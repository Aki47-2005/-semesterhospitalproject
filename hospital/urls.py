from django.contrib import admin
from django.urls import path

from hospitalapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_view, name="HOME"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("<str:kind>/", views.record_list, name="records"),
    path("<str:kind>/new/", views.record_form, name="record_create"),
    path("<str:kind>/<int:pk>/edit/", views.record_form, name="record_update"),
    path("<str:kind>/<int:pk>/delete/", views.record_delete, name="record_delete"),
]
