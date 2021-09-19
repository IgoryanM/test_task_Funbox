from django.urls import path

from .views import visited_links_view, visited_domains_view

urlpatterns = [
    path('visited_links/', visited_links_view),
    path('visited_domains/', visited_domains_view),
]
