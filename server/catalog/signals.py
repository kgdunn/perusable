from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Wine


@receiver(post_save, sender=Wine, dispatch_uid="on_wine_save")
def on_wine_save(sender, instance, *args, **kwargs):
    sender.objects.filter(pk=instance.id).update(
        search_vector=(
            SearchVector("variety", weight="A")
            + SearchVector("winery", weight="A")
            + SearchVector("description", weight="B")
        )
    )
