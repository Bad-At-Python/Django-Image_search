from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("upload/", views.upload, name="upload"),
    path("add_tag", views.add_tag, name="add_tag"),
    path("result/<str:result_text>", views.result, name="result"),
    path("view/<str:image_ids>/", views.view, name="view"),
    path("search_processing/", views.search_processing, name="search_processing"),
    path("upload_processing/", views.upload_processing, name="upload_processing"),
    path("add_tag_processing/", views.add_tag_processing, name="add_tag_processing"),
]
