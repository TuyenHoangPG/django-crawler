from django.urls import path

from .views import CrawlPropertyAPIView, ViewListPropertyAPIView

urlpatterns = [
    path("crawl-data", CrawlPropertyAPIView.as_view(), name="crawl_property"),
    path("list", ViewListPropertyAPIView.as_view(), name="list_property"),
]
