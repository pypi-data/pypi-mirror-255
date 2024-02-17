from django.db import models
from django.utils.translation import gettext_lazy as _
from djangocms_blog.models import LatestPostsPlugin, Post


class PostExtension(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="extension")
    event_start_date = models.DateTimeField(verbose_name=_("Event start"))
    event_end_date = models.DateTimeField(
        verbose_name=_("Event end"),
        null=True,
        blank=True,
        help_text=_("If the event is held over several days"),
    )

    class Meta:
        verbose_name = _("Event infos")
        verbose_name_plural = _("Events infos")

    def __str__(self):
        return _("Event infos") + " (#" + str(self.id) + ")"


class UpcomingEventsPlugin(LatestPostsPlugin):
    def __str__(self):
        return _("{} upcoming events").format(self.latest_posts)

    class Meta:
        proxy = True
        verbose_name = _("Upcoming events plugin")
        verbose_name_plural = _("Upcoming events plugins")


class PastEventsPlugin(LatestPostsPlugin):
    def __str__(self):
        return _("{} past events").format(self.latest_posts)

    class Meta:
        proxy = True
        verbose_name = _("Past events plugin")
        verbose_name_plural = _("Past events plugins")
