from django.db import models
from django.core.exceptions import FieldError


class PublicManager(models.Manager):
    def get_published(self, user):
        """
        Get published items based on user authentication status.
        Returns all items for authenticated users, only published for anonymous.
        """
        if user.is_authenticated:
            return self.get_queryset()
        else:
            return self.get_queryset().filter(published=True)

    def get_public(self, user):
        """
        Get public items based on user authentication status.
        Returns all items for authenticated users, only non-private for anonymous.
        """
        if user.is_authenticated:
            return self.get_queryset()
        else:
            try:
                return self.get_queryset().filter(private=False)
            except FieldError:
                return self.get_queryset().filter(property__private=False)


class RollingStockManager(PublicManager):
    """Optimized manager for RollingStock with prefetch methods."""

    def with_related(self):
        """
        Optimize queryset by prefetching commonly accessed related objects.
        Use this for list views to avoid N+1 queries.
        """
        return self.select_related(
            'rolling_class',
            'rolling_class__company',
            'rolling_class__type',
            'manufacturer',
            'scale',
            'decoder',
            'shop',
        ).prefetch_related('tags', 'image')

    def with_details(self):
        """
        Optimize queryset for detail views with all related objects.
        Includes properties, documents, and journal entries.
        """
        return self.with_related().prefetch_related(
            'property',
            'document',
            'journal',
            'rolling_class__property',
            'rolling_class__manufacturer',
            'decoder__document',
        )

    def get_published_with_related(self, user):
        """
        Convenience method combining get_published with related objects.
        """
        return self.get_published(user).with_related()


class ConsistManager(PublicManager):
    """Optimized manager for Consist with prefetch methods."""

    def with_related(self):
        """
        Optimize queryset by prefetching commonly accessed related objects.
        Note: Consist.image is a direct ImageField, not a relation.
        """
        return self.select_related('company', 'scale').prefetch_related(
            'tags', 'consist_item'
        )

    def with_rolling_stock(self):
        """
        Optimize queryset including consist items and their rolling stock.
        Use for detail views showing consist composition.
        """
        return self.with_related().prefetch_related(
            'consist_item__rolling_stock',
            'consist_item__rolling_stock__rolling_class',
            'consist_item__rolling_stock__rolling_class__company',
            'consist_item__rolling_stock__rolling_class__type',
            'consist_item__rolling_stock__manufacturer',
            'consist_item__rolling_stock__scale',
            'consist_item__rolling_stock__image',
        )


class BookManager(PublicManager):
    """Optimized manager for Book/Catalog with prefetch methods."""

    def with_related(self):
        """
        Optimize queryset by prefetching commonly accessed related objects.
        """
        return self.select_related('publisher', 'shop').prefetch_related(
            'authors', 'tags', 'image', 'toc'
        )

    def with_details(self):
        """
        Optimize queryset for detail views with properties and documents.
        """
        return self.with_related().prefetch_related('property', 'document')


class CatalogManager(PublicManager):
    """Optimized manager for Catalog with prefetch methods."""

    def with_related(self):
        """
        Optimize queryset by prefetching commonly accessed related objects.
        """
        return self.select_related('manufacturer', 'shop').prefetch_related(
            'scales', 'tags', 'image'
        )

    def with_details(self):
        """
        Optimize queryset for detail views with properties and documents.
        """
        return self.with_related().prefetch_related('property', 'document')


class MagazineIssueManager(PublicManager):
    """Optimized manager for MagazineIssue with prefetch methods."""

    def with_related(self):
        """
        Optimize queryset by prefetching commonly accessed related objects.
        """
        return self.select_related('magazine').prefetch_related(
            'tags', 'image', 'toc'
        )

    def with_details(self):
        """
        Optimize queryset for detail views with properties and documents.
        """
        return self.with_related().prefetch_related('property', 'document')
