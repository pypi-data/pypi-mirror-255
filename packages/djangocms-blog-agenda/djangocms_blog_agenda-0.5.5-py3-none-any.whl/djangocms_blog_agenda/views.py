from django.db.models import Q
from django.utils import timezone
from djangocms_blog.views import (
    BaseBlogListView,
    CategoryEntriesView,
    PostArchiveView,
    PostDetailView,
    PostListView,
    TaggedListView,
)


class AgendaDetailView(PostDetailView):
    def post(self, *args, **kwargs):
        return self.get(args, kwargs)


class AgendaComingEventsMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if "agenda" in self.config.template_prefix:
            return qs.order_by("extension__event_start_date").filter(
                (
                    Q(extension__event_end_date__isnull=True)
                    & Q(extension__event_start_date__gte=timezone.now())
                )
                | (
                    Q(extension__event_end_date__isnull=False)
                    & Q(extension__event_end_date__gte=timezone.now())
                )
            )
        return qs


class AgendaAndPostListView(AgendaComingEventsMixin, PostListView):
    ...


class AgendaCategoryEntriesView(AgendaComingEventsMixin, CategoryEntriesView):
    ...


class AgendaTaggedListView(AgendaComingEventsMixin, TaggedListView):
    ...


class AgendaArchiveView(PostArchiveView):
    start_date_field = "extension__event_start_date"
    end_date_field = "extension__event_end_date"

    def get_queryset(self):
        if "agenda" in self.config.template_prefix:
            # Bypass PostArchiveView.get_queryset() because it does not handle `end_date_field`
            qs = super(BaseBlogListView, self).get_queryset()

            if "month" in self.kwargs:
                qs = qs.filter(
                    Q(**{"%s__month" % self.start_date_field: self.kwargs["month"]})
                    | Q(**{"%s__month" % self.end_date_field: self.kwargs["month"]})
                )
            if "year" in self.kwargs:
                qs = qs.filter(
                    Q(**{"%s__year" % self.start_date_field: self.kwargs["year"]})
                    | Q(**{"%s__year" % self.end_date_field: self.kwargs["year"]})
                )

            return qs.order_by("-extension__event_start_date").filter(
                (
                    Q(extension__event_end_date__isnull=True)
                    & Q(extension__event_start_date__lt=timezone.now())
                )
                | (
                    Q(extension__event_end_date__isnull=False)
                    & Q(extension__event_end_date__lt=timezone.now())
                )
            )
        return super().get_queryset()
