from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import remove_query_param, replace_query_param


class StandardResultsSetPagination(PageNumberPagination):
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'first': self.get_first_link(),
                'last': self.get_last_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

    def get_first_link(self):
        page_size_value = self.get_page_size(self.request)
        count = self.page.paginator.count
        if page_size_value is not None and page_size_value >= count:
            return None
        num_pages = self.page.paginator.num_pages
        if num_pages < 1:
            return None
        url = self.request.build_absolute_uri()
        return remove_query_param(url, self.page_query_param)

    def get_last_link(self):
        page_size_value = self.get_page_size(self.request)
        count = self.page.paginator.count
        if page_size_value is not None and page_size_value >= count:
            return None
        num_pages = self.page.paginator.num_pages
        if num_pages < 1:
            return None
        url = self.request.build_absolute_uri()
        page_number = num_pages
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
