# chats/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    page_size = 20  # 20 messages per page
    page_size_query_param = "page_size"
    max_page_size = 100  # prevent abuse

    def get_paginated_response(self, data):
        """
        Override to ensure pagination includes total count
        """
        return Response({
            "count": self.page.paginator.count,   # ✅ total items
            "next": self.get_next_link(),         # ✅ next page link
            "previous": self.get_previous_link(),  # ✅ previous page
            "results": data                       # ✅ paginated results
        })
