from django.urls import include, re_path


urlpatterns = [
    re_path(r'^property/', include("modules.property.urls"), name='property'),
]
