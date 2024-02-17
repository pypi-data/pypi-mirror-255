from cms.plugin_pool import plugin_pool
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from djangocms_blog.cms_plugins import BlogPlugin
from djangocms_blog.forms import LatestEntriesForm
from djangocms_blog.settings import get_setting

from .models import PastEventsPlugin, UpcomingEventsPlugin


class BaseEntriesPlugin(BlogPlugin):
    form = LatestEntriesForm
    filter_horizontal = ("categories",)
    cache = False
    base_render_template = "latest_entries.html"

    def get_fields(self, request, obj=None):
        """
        Return the fields available when editing the plugin.

        'template_folder' field is added if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains multiple folders.

        """
        fields = ["app_config", "latest_posts", "tags", "categories"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1:
            fields.append("template_folder")
        return fields

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        context["posts_list"] = self.get_posts(
            instance, context["request"], published_only=False
        )
        context["TRUNCWORDS_COUNT"] = get_setting("POSTS_LIST_TRUNCWORDS_COUNT")
        return context


@plugin_pool.register_plugin
class AgendaUpcomingEntriesPlugin(BaseEntriesPlugin):
    """
    Return upcoming events
    """

    name = _("Upcoming events")
    model = UpcomingEventsPlugin

    def get_posts(self, instance, request, published_only=True):
        posts = instance.post_queryset(request, published_only)

        # Keep only posts with an event date in the futur
        posts = posts.order_by("extension__event_start_date").filter(
            (
                Q(extension__event_end_date__isnull=True)
                & Q(extension__event_start_date__gte=timezone.now())
            )
            | (
                Q(extension__event_end_date__isnull=False)
                & Q(extension__event_end_date__gte=timezone.now())
            )
        )

        if instance.tags.exists():
            posts = posts.filter(tags__in=list(instance.tags.all()))
        if instance.categories.exists():
            posts = posts.filter(categories__in=list(instance.categories.all()))
        return instance.optimize(posts.distinct())[: instance.latest_posts]


@plugin_pool.register_plugin
class AgendaPastEntriesPlugin(BaseEntriesPlugin):
    """
    Return past events
    """

    name = _("Past events")
    model = PastEventsPlugin

    def get_fields(self, request, obj=None):
        """
        Return the fields available when editing the plugin.

        'template_folder' field is added if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains multiple folders.

        """
        fields = ["app_config", "latest_posts", "tags", "categories"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1:
            fields.append("template_folder")
        return fields

    def get_posts(self, instance, request, published_only=True):
        posts = instance.post_queryset(request, published_only)

        # Keep only posts with an event date in the past
        posts = posts.order_by("-extension__event_start_date").filter(
            (
                Q(extension__event_end_date__isnull=True)
                & Q(extension__event_start_date__lt=timezone.now())
            )
            | (
                Q(extension__event_end_date__isnull=False)
                & Q(extension__event_end_date__lt=timezone.now())
            )
        )

        if instance.tags.exists():
            posts = posts.filter(tags__in=list(instance.tags.all()))
        if instance.categories.exists():
            posts = posts.filter(categories__in=list(instance.categories.all()))
        return instance.optimize(posts.distinct())[: instance.latest_posts]
