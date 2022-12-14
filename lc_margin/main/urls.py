from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path(
        "calculator/",
        views.CalculatorView.as_view(),
        name="calculator",
    ),
    path(
        "download/",
        views.SampleDownload.as_view(),
        name="download",
    )
]
