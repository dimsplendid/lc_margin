from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    # path(
    #     "calculator/",
    #     views.CalculatorView.as_view(),
    #     name="calculator",
    # ),
    path(
        "download/",
        views.TemplateDownload.as_view(),
        name="template_download",
    ),
    path(
        "calculator/batch/",
        views.BatchCalculatorView.as_view(),
        name="batch_calculator",
    ),
    path(
        "calculator/batch/result/download/",
        views.ResultDownloadView.as_view(),
        name="result_download",
    )
]
