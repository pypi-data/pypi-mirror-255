from django.urls import path
from djangocms_blog.urls import urlpatterns as original_patterns

from .views import (
    AgendaAndPostListView,
    AgendaArchiveView,
    AgendaCategoryEntriesView,
    AgendaDetailView,
    AgendaTaggedListView,
)


# Here are the patched urls that still includes the original urlpattern of djangocms_blog.
# But it also adds an AgendaAndPostListView (that replace the original PostListView).

for pattern in original_patterns:
    if pattern.name == "post-detail":
        pattern.callback = AgendaDetailView.as_view()


urlpatterns = [
    path(
        "<int:year>/",
        AgendaArchiveView.as_view(),
        name="agenda-archive",
    ),
    path(
        "<int:year>/<int:month>/",
        AgendaArchiveView.as_view(),
        name="agenda-archive",
    ),
    path("", AgendaAndPostListView.as_view(), name="agenda-coming-soon"),
    path(
        "category/<str:category>/",
        AgendaCategoryEntriesView.as_view(),
        name="agenda-posts-category",
    ),
    path("tag/<slug:tag>/", AgendaTaggedListView.as_view(), name="posts-tagged"),
    *original_patterns,
]
