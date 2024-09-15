from django.db import models


class PublicManager(models.Manager):
    def get_published(self, user):
        if user.is_authenticated:
            return self.get_queryset()
        else:
            return self.get_queryset().filter(published=True)

    def get_public(self, user):
        if user.is_authenticated:
            return self.get_queryset()
        else:
            return self.get_queryset().filter(private=False)
