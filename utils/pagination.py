from rest_framework.pagination import PageNumberPagination
from .helpers import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            success=True,
            status=200,
            message="Data fetched successfully.",
            data=data,
            meta={
                "total": self.page.paginator.count,
                "page": self.page.number,
                "limit": self.get_page_size(self.request),
                "totalPages": self.page.paginator.num_pages
            }
        )
