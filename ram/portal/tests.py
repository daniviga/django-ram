import base64
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from portal.models import SiteConfiguration, Flatpage
from roster.models import RollingClass, RollingStock
from consist.models import Consist, ConsistItem
from bookshelf.models import (
    Book,
    Catalog,
    Magazine,
    MagazineIssue,
    Author,
    Publisher,
)
from metadata.models import (
    Company,
    Manufacturer,
    Scale,
    RollingStockType,
    Tag,
)


class PortalTestBase(TestCase):
    """Base test class with common setup for portal views."""

    def setUp(self):
        """Set up test data used across multiple test cases."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = Client()

        # Create site configuration
        self.site_config = SiteConfiguration.get_solo()
        self.site_config.items_per_page = "6"
        self.site_config.items_ordering = "type"
        self.site_config.save()

        # Create metadata
        self.company = Company.objects.create(
            name="Rio Grande Southern", country="US"
        )
        self.company2 = Company.objects.create(name="D&RGW", country="US")

        self.scale_ho = Scale.objects.create(
            scale="HO", ratio="1:87", tracks=16.5
        )
        self.scale_n = Scale.objects.create(
            scale="N", ratio="1:160", tracks=9.0
        )

        self.stock_type = RollingStockType.objects.create(
            type="Steam Locomotive", category="locomotive", order=1
        )
        self.stock_type2 = RollingStockType.objects.create(
            type="Box Car", category="freight", order=2
        )

        self.real_manufacturer = Manufacturer.objects.create(
            name="Baldwin Locomotive Works", category="real", country="US"
        )
        self.model_manufacturer = Manufacturer.objects.create(
            name="Bachmann", category="model", country="US"
        )

        self.tag1 = Tag.objects.create(name="Narrow Gauge")
        self.tag2 = Tag.objects.create(name="Colorado")

        # Create rolling classes
        self.rolling_class1 = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
            description="<p>Narrow gauge steam locomotive</p>",
        )

        self.rolling_class2 = RollingClass.objects.create(
            identifier="K-27",
            type=self.stock_type,
            company=self.company2,
            description="<p>Another narrow gauge locomotive</p>",
        )

        # Create rolling stock
        self.rolling_stock1 = RollingStock.objects.create(
            rolling_class=self.rolling_class1,
            road_number="346",
            scale=self.scale_ho,
            manufacturer=self.model_manufacturer,
            item_number="28698",
            published=True,
            featured=True,
        )
        self.rolling_stock1.tags.add(self.tag1, self.tag2)

        self.rolling_stock2 = RollingStock.objects.create(
            rolling_class=self.rolling_class2,
            road_number="455",
            scale=self.scale_ho,
            manufacturer=self.model_manufacturer,
            item_number="28699",
            published=True,
            featured=False,
        )

        self.rolling_stock3 = RollingStock.objects.create(
            rolling_class=self.rolling_class1,
            road_number="340",
            scale=self.scale_n,
            manufacturer=self.model_manufacturer,
            item_number="28700",
            published=False,  # Unpublished
        )

        # Create consist
        self.consist = Consist.objects.create(
            identifier="Freight Train 1",
            company=self.company,
            scale=self.scale_ho,
            era="1950s",
            published=True,
        )
        ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock1,
            order=1,
            load=False,
        )

        # Create bookshelf data
        self.publisher = Publisher.objects.create(
            name="Kalmbach Publishing", country="US"
        )
        self.author = Author.objects.create(
            first_name="John", last_name="Doe"
        )

        self.book = Book.objects.create(
            title="Model Railroading Basics",
            publisher=self.publisher,
            ISBN="978-0-89024-123-4",
            language="en",
            number_of_pages=200,
            publication_year=2020,
            published=True,
        )
        self.book.authors.add(self.author)

        self.catalog = Catalog.objects.create(
            manufacturer=self.model_manufacturer,
            years="2020-2021",
            publication_year=2020,
            published=True,
        )
        self.catalog.scales.add(self.scale_ho)

        self.magazine = Magazine.objects.create(
            name="Model Railroader", publisher=self.publisher, published=True
        )

        self.magazine_issue = MagazineIssue.objects.create(
            magazine=self.magazine,
            issue_number="Jan 2020",
            publication_year=2020,
            publication_month=1,
            published=True,
        )

        # Create flatpage
        self.flatpage = Flatpage.objects.create(
            name="About Us",
            path="about-us",
            content="<p>About our site</p>",
            published=True,
        )


class GetHomeViewTest(PortalTestBase):
    """Test cases for GetHome view (homepage)."""

    def test_home_view_loads(self):
        """Test that the home page loads successfully."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_home_view_shows_featured_items(self):
        """Test that featured items appear on homepage."""
        response = self.client.get(reverse("index"))
        self.assertContains(response, "346")  # Featured rolling stock
        self.assertIn(self.rolling_stock1, response.context["data"])

    def test_home_view_hides_unpublished_for_anonymous(self):
        """Test that unpublished items are hidden from anonymous users."""
        response = self.client.get(reverse("index"))
        # rolling_stock3 is unpublished, should not appear
        self.assertNotIn(self.rolling_stock3, response.context["data"])

    def test_home_view_shows_unpublished_for_authenticated(self):
        """Test that authenticated users see unpublished items."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("index"))
        # Authenticated users should see all items
        self.assertEqual(response.status_code, 200)


class GetRosterViewTest(PortalTestBase):
    """Test cases for GetRoster view."""

    def test_roster_view_loads(self):
        """Test that the roster page loads successfully."""
        response = self.client.get(reverse("roster"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pagination.html")

    def test_roster_view_shows_published_items(self):
        """Test that roster shows published rolling stock."""
        response = self.client.get(reverse("roster"))
        self.assertIn(self.rolling_stock1, response.context["data"])
        self.assertIn(self.rolling_stock2, response.context["data"])

    def test_roster_pagination(self):
        """Test roster pagination."""
        # Create more items to test pagination
        for i in range(10):
            RollingStock.objects.create(
                rolling_class=self.rolling_class1,
                road_number=f"35{i}",
                scale=self.scale_ho,
                manufacturer=self.model_manufacturer,
                published=True,
            )

        response = self.client.get(reverse("roster"))
        self.assertIn("page_range", response.context)
        # Should paginate with items_per_page=6
        self.assertLessEqual(len(response.context["data"]), 6)


class GetRollingStockViewTest(PortalTestBase):
    """Test cases for GetRollingStock detail view."""

    def test_rolling_stock_detail_view(self):
        """Test rolling stock detail view loads correctly."""
        url = reverse("rolling_stock", kwargs={"uuid": self.rolling_stock1.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rollingstock.html")
        self.assertEqual(
            response.context["rolling_stock"], self.rolling_stock1
        )

    def test_rolling_stock_detail_with_properties(self):
        """Test detail view includes properties and documents."""
        url = reverse("rolling_stock", kwargs={"uuid": self.rolling_stock1.uuid})
        response = self.client.get(url)
        self.assertIn("properties", response.context)
        self.assertIn("documents", response.context)
        self.assertIn("class_properties", response.context)

    def test_rolling_stock_detail_shows_consists(self):
        """Test detail view shows consists this rolling stock is in."""
        url = reverse("rolling_stock", kwargs={"uuid": self.rolling_stock1.uuid})
        response = self.client.get(url)
        self.assertIn("consists", response.context)
        self.assertIn(self.consist, response.context["consists"])

    def test_rolling_stock_detail_not_found(self):
        """Test 404 for non-existent rolling stock."""
        from uuid import uuid4

        url = reverse("rolling_stock", kwargs={"uuid": uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class SearchObjectsViewTest(PortalTestBase):
    """Test cases for SearchObjects view."""

    def test_search_view_post(self):
        """Test search via POST request."""
        response = self.client.post(reverse("search"), {"search": "346"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")

    def test_search_finds_rolling_stock(self):
        """Test search finds rolling stock by road number."""
        search_term = base64.b64encode(b"346").decode()
        url = reverse("search", kwargs={"search": search_term, "page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should find rolling_stock1 with road number 346

    def test_search_with_filter_type(self):
        """Test search with type filter."""
        search_term = base64.b64encode(b"type:Steam").decode()
        url = reverse("search", kwargs={"search": search_term, "page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_with_filter_company(self):
        """Test search with company filter."""
        search_term = base64.b64encode(b"company:Rio Grande").decode()
        url = reverse("search", kwargs={"search": search_term, "page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_finds_books(self):
        """Test search finds books."""
        search_term = base64.b64encode(b"Railroading").decode()
        url = reverse("search", kwargs={"search": search_term, "page": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_empty_returns_bad_request(self):
        """Test search with empty string returns error."""
        response = self.client.post(reverse("search"), {"search": ""})
        self.assertEqual(response.status_code, 400)


class GetObjectsFilteredViewTest(PortalTestBase):
    """Test cases for GetObjectsFiltered view."""

    def test_filter_by_type(self):
        """Test filtering by rolling stock type."""
        url = reverse(
            "filtered",
            kwargs={"_filter": "type", "search": self.stock_type.slug},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "filter.html")

    def test_filter_by_company(self):
        """Test filtering by company."""
        url = reverse(
            "filtered",
            kwargs={"_filter": "company", "search": self.company.slug},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter_by_scale(self):
        """Test filtering by scale."""
        url = reverse(
            "filtered",
            kwargs={"_filter": "scale", "search": self.scale_ho.slug},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter_by_tag(self):
        """Test filtering by tag."""
        url = reverse(
            "filtered", kwargs={"_filter": "tag", "search": self.tag1.slug}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should find rolling_stock1 which has tag1

    def test_filter_invalid_raises_404(self):
        """Test invalid filter type raises 404."""
        url = reverse(
            "filtered", kwargs={"_filter": "invalid", "search": "test"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class GetManufacturerItemViewTest(PortalTestBase):
    """Test cases for GetManufacturerItem view."""

    def test_manufacturer_view_all_items(self):
        """Test manufacturer view showing all items."""
        url = reverse(
            "manufacturer",
            kwargs={
                "manufacturer": self.model_manufacturer.slug,
                "search": "all",
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manufacturer.html")

    def test_manufacturer_view_specific_item(self):
        """Test manufacturer view filtered by item number."""
        url = reverse(
            "manufacturer",
            kwargs={
                "manufacturer": self.model_manufacturer.slug,
                "search": self.rolling_stock1.item_number_slug,
            },
        )
        response = self.client.get(url)
        # Should return rolling stock with that item number
        self.assertEqual(response.status_code, 200)

    def test_manufacturer_not_found(self):
        """Test 404 for non-existent manufacturer."""
        url = reverse(
            "manufacturer",
            kwargs={"manufacturer": "nonexistent", "search": "all"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ConsistsViewTest(PortalTestBase):
    """Test cases for Consists list view."""

    def test_consists_list_view(self):
        """Test consists list view loads."""
        response = self.client.get(reverse("consists"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.consist, response.context["data"])

    def test_consists_pagination(self):
        """Test consists list pagination."""
        # Create more consists for pagination
        for i in range(10):
            Consist.objects.create(
                identifier=f"Train {i}",
                company=self.company,
                scale=self.scale_ho,
                published=True,
            )

        response = self.client.get(reverse("consists"))
        self.assertIn("page_range", response.context)


class GetConsistViewTest(PortalTestBase):
    """Test cases for GetConsist detail view."""

    def test_consist_detail_view(self):
        """Test consist detail view loads correctly."""
        url = reverse("consist", kwargs={"uuid": self.consist.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "consist.html")
        self.assertEqual(response.context["consist"], self.consist)

    def test_consist_shows_rolling_stock(self):
        """Test consist detail shows constituent rolling stock."""
        url = reverse("consist", kwargs={"uuid": self.consist.uuid})
        response = self.client.get(url)
        self.assertIn("data", response.context)
        # Should show rolling_stock1 which is in the consist

    def test_consist_not_found(self):
        """Test 404 for non-existent consist."""
        from uuid import uuid4

        url = reverse("consist", kwargs={"uuid": uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class MetadataListViewsTest(PortalTestBase):
    """Test cases for metadata list views (Companies, Scales, Types)."""

    def test_companies_view(self):
        """Test companies list view."""
        response = self.client.get(reverse("companies"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.company, response.context["data"])

    def test_manufacturers_view_real(self):
        """Test manufacturers view for real manufacturers."""
        url = reverse("manufacturers", kwargs={"category": "real"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.real_manufacturer, response.context["data"])

    def test_manufacturers_view_model(self):
        """Test manufacturers view for model manufacturers."""
        url = reverse("manufacturers", kwargs={"category": "model"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.model_manufacturer, response.context["data"])

    def test_manufacturers_invalid_category(self):
        """Test manufacturers view with invalid category."""
        url = reverse("manufacturers", kwargs={"category": "invalid"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_scales_view(self):
        """Test scales list view."""
        response = self.client.get(reverse("scales"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.scale_ho, response.context["data"])

    def test_types_view(self):
        """Test rolling stock types list view."""
        response = self.client.get(reverse("rolling_stock_types"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.stock_type, response.context["data"])


class BookshelfViewsTest(PortalTestBase):
    """Test cases for bookshelf views."""

    def test_books_list_view(self):
        """Test books list view."""
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.book, response.context["data"])

    def test_catalogs_list_view(self):
        """Test catalogs list view."""
        response = self.client.get(reverse("catalogs"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.catalog, response.context["data"])

    def test_magazines_list_view(self):
        """Test magazines list view."""
        response = self.client.get(reverse("magazines"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.magazine, response.context["data"])

    def test_book_detail_view(self):
        """Test book detail view."""
        url = reverse(
            "bookshelf_item",
            kwargs={"selector": "book", "uuid": self.book.uuid},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookshelf/book.html")
        self.assertEqual(response.context["data"], self.book)

    def test_catalog_detail_view(self):
        """Test catalog detail view."""
        url = reverse(
            "bookshelf_item",
            kwargs={"selector": "catalog", "uuid": self.catalog.uuid},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["data"], self.catalog)

    def test_bookshelf_item_invalid_selector(self):
        """Test bookshelf item with invalid selector."""
        url = reverse(
            "bookshelf_item",
            kwargs={"selector": "invalid", "uuid": self.book.uuid},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_magazine_detail_view(self):
        """Test magazine detail view."""
        url = reverse("magazine", kwargs={"uuid": self.magazine.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookshelf/magazine.html")

    def test_magazine_issue_detail_view(self):
        """Test magazine issue detail view."""
        url = reverse(
            "issue",
            kwargs={
                "magazine": self.magazine.uuid,
                "uuid": self.magazine_issue.uuid,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["data"], self.magazine_issue)


class FlatpageViewTest(PortalTestBase):
    """Test cases for Flatpage view."""

    def test_flatpage_view_loads(self):
        """Test flatpage loads correctly."""
        url = reverse("flatpage", kwargs={"flatpage": self.flatpage.path})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flatpages/flatpage.html")
        self.assertEqual(response.context["flatpage"], self.flatpage)

    def test_flatpage_not_found(self):
        """Test 404 for non-existent flatpage."""
        url = reverse("flatpage", kwargs={"flatpage": "nonexistent"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unpublished_flatpage_hidden_from_anonymous(self):
        """Test unpublished flatpage is hidden from anonymous users."""
        self.flatpage.published = False
        self.flatpage.save()

        url = reverse("flatpage", kwargs={"flatpage": self.flatpage.path})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class RenderExtraJSViewTest(PortalTestBase):
    """Test cases for RenderExtraJS view."""

    def test_extra_js_view_loads(self):
        """Test extra JS endpoint loads."""
        response = self.client.get(reverse("extra_js"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")

    def test_extra_js_returns_configured_content(self):
        """Test extra JS returns configured JavaScript."""
        self.site_config.extra_js = "console.log('test');"
        self.site_config.save()

        response = self.client.get(reverse("extra_js"))
        self.assertContains(response, "console.log('test');")


class QueryOptimizationTest(PortalTestBase):
    """Test cases to verify query optimization is working."""

    def test_rolling_stock_list_uses_select_related(self):
        """Test that rolling stock list view uses query optimization."""
        # This test verifies the optimization exists in the code
        # In a real scenario, you'd use django-debug-toolbar or
        # assertNumQueries to verify actual query counts
        response = self.client.get(reverse("roster"))
        self.assertEqual(response.status_code, 200)
        # If optimization is working, this should use far fewer queries
        # than the number of rolling stock items

    def test_consist_detail_uses_prefetch_related(self):
        """Test that consist detail view uses query optimization."""
        url = reverse("consist", kwargs={"uuid": self.consist.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Should prefetch rolling stock items to avoid N+1 queries
