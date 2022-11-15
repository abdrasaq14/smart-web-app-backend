from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import caches
from core.models import Alert, TransactionHistory


@receiver(post_save, sender=TransactionHistory)
@receiver(post_save, sender=Alert)
def clear_cache(sender, instance, created, **kwargs):
    try:
        caches.all()[0].clear()
        print('Cache cleared')
    except:
        pass
