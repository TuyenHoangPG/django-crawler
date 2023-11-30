from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.renderer import CustomRenderer

from .models import Property
from .pagination import PropertyPagination
from .serializers import CrawlPropertySerializer, PropertySerializer


class CrawlPropertyAPIView(GenericAPIView):
    serializer_class = CrawlPropertySerializer
    permission_classes = [AllowAny]
    renderer_classes = (CustomRenderer,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.get_property(serializer.validated_data)
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Successfully",
            },
            status.HTTP_200_OK,
        )


class ViewListPropertyAPIView(GenericAPIView):
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    renderer_classes = (CustomRenderer,)
    pagination_class = PropertyPagination

    def get_queryset(self):
        request = self.request
        properties = Property.objects.all()
        if request.query_params.get("sort_field"):
            source_mapping = {
                "1": "-price",
                "2": "price",
                "3": "-area",
                "4": "area",
                "5": "-bedrooms",
                "6": "bedrooms",
            }
            sort_field = request.query_params.get("sort_field")
            sort_param = source_mapping.get(sort_field)
            if not sort_param:
                ValidationError.default_detail = {
                    "exception": "Invalid sort field param",
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                raise ValidationError()
            return Property.objects.order_by(sort_param).all()

        return properties.order_by("-created_date")

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "data": self.get_paginated_response(serializer.data).data,
                    "message": "",
                    "exception": {},
                    "status": status.HTTP_200_OK,
                },
                status.HTTP_200_OK,
            )

        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "",
                "exception": {},
                "status": status.HTTP_200_OK,
            },
            status.HTTP_200_OK,
        )
