from rest_framework.pagination import PageNumberPagination


class TablePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page'
    max_page_size = 1000
