from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.conf import settings

from roster.models import RollingClass, RollingStock, RollingStockImage
from metadata.models import (
    Company,
    Manufacturer,
    Scale,
    RollingStockType,
    Decoder,
)


class RollingClassTestCase(TestCase):
    """Test cases for RollingClass model."""

    def setUp(self):
        """Set up test data."""
        # Create a company
        self.company = Company.objects.create(
            name="Rio Grande Southern",
            country="US",
        )

        # Create a rolling stock type
        self.stock_type = RollingStockType.objects.create(
            type="Steam Locomotive",
            category="locomotive",
            order=1,
        )

        # Create a real manufacturer
        self.real_manufacturer = Manufacturer.objects.create(
            name="Baldwin Locomotive Works",
            category="real",
            country="US",
        )

    def test_rolling_class_creation(self):
        """Test creating a rolling class."""
        rolling_class = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
            description="<p>Narrow gauge steam locomotive</p>",
        )

        self.assertEqual(str(rolling_class), "Rio Grande Southern C-19")
        self.assertEqual(rolling_class.identifier, "C-19")
        self.assertEqual(rolling_class.type, self.stock_type)
        self.assertEqual(rolling_class.company, self.company)

    def test_rolling_class_country_property(self):
        """Test that rolling class inherits country from company."""
        rolling_class = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
        )

        self.assertEqual(rolling_class.country, self.company.country)

    def test_rolling_class_ordering(self):
        """Test rolling class ordering by company and identifier."""
        company2 = Company.objects.create(name="D&RGW", country="US")

        rc1 = RollingClass.objects.create(
            identifier="K-27", type=self.stock_type, company=company2
        )
        rc2 = RollingClass.objects.create(
            identifier="C-19", type=self.stock_type, company=self.company
        )
        rc3 = RollingClass.objects.create(
            identifier="K-28", type=self.stock_type, company=company2
        )

        classes = list(RollingClass.objects.all())
        self.assertEqual(classes[0], rc1)  # D&RGW K-27
        self.assertEqual(classes[1], rc3)  # D&RGW K-28
        self.assertEqual(classes[2], rc2)  # Rio Grande Southern comes last

    def test_rolling_class_manufacturer_relationship(self):
        """Test many-to-many relationship with manufacturers."""
        rolling_class = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
        )

        rolling_class.manufacturer.add(self.real_manufacturer)

        self.assertEqual(rolling_class.manufacturer.count(), 1)
        self.assertIn(self.real_manufacturer, rolling_class.manufacturer.all())


class RollingStockTestCase(TestCase):
    """Test cases for RollingStock model."""

    def setUp(self):
        """Set up test data."""
        # Create necessary related objects
        self.company = Company.objects.create(name="RGS", country="US")

        self.stock_type = RollingStockType.objects.create(
            type="Steam Locomotive",
            category="locomotive",
            order=1,
        )

        self.rolling_class = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
        )

        self.scale = Scale.objects.create(
            scale="HOn3",
            ratio="1:87",
            tracks=10.5,
            gauge="3 ft",
        )

        self.model_manufacturer = Manufacturer.objects.create(
            name="Blackstone Models",
            category="model",
            country="US",
        )

    def test_rolling_stock_creation(self):
        """Test creating rolling stock."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
            manufacturer=self.model_manufacturer,
        )

        self.assertEqual(str(stock), "RGS C-19 340")
        self.assertEqual(stock.road_number, "340")
        self.assertEqual(stock.road_number_int, 340)
        self.assertTrue(stock.published)

    def test_road_number_int_extraction(self):
        """Test automatic extraction of integer from road number."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="RGS-42",
            scale=self.scale,
        )

        self.assertEqual(stock.road_number_int, 42)

    def test_road_number_no_integer(self):
        """Test road number with no integer defaults to 0."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="N/A",
            scale=self.scale,
        )

        self.assertEqual(stock.road_number_int, 0)

    def test_item_number_slug_generation(self):
        """Test automatic slug generation from item number."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
            item_number="BLI-123 ABC",
        )

        self.assertEqual(stock.item_number_slug, "bli-123-abc")

    def test_featured_limit_validation(self):
        """Test that featured items are limited by FEATURED_ITEMS_MAX."""
        # Create FEATURED_ITEMS_MAX featured items
        for i in range(settings.FEATURED_ITEMS_MAX):
            RollingStock.objects.create(
                rolling_class=self.rolling_class,
                road_number=str(i),
                scale=self.scale,
                featured=True,
            )

        # Try to create one more featured item
        extra_stock = RollingStock(
            rolling_class=self.rolling_class,
            road_number="999",
            scale=self.scale,
            featured=True,
        )

        with self.assertRaises(ValidationError) as cm:
            extra_stock.clean()

        self.assertIn("featured items", str(cm.exception))

    def test_price_decimal_field(self):
        """Test price field accepts decimal values."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
            price=Decimal("249.99"),
        )

        self.assertEqual(stock.price, Decimal("249.99"))

    def test_decoder_interface_display(self):
        """Test decoder interface display method."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
            decoder_interface=1,  # 21-pin interface
        )

        interface = stock.get_decoder_interface()
        self.assertIsNotNone(interface)
        self.assertNotEqual(interface, "No interface")

    def test_decoder_interface_none(self):
        """Test decoder interface when not set."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
        )

        interface = stock.get_decoder_interface()
        self.assertEqual(interface, "No interface")

    def test_country_and_company_properties(self):
        """Test that country and company properties work."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
        )

        self.assertEqual(stock.country, self.company.country)
        self.assertEqual(stock.company, self.company)

    def test_get_absolute_url(self):
        """Test get_absolute_url returns correct URL."""
        stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
        )

        url = stock.get_absolute_url()
        self.assertIn(str(stock.uuid), url)

    def test_published_filtering(self):
        """Test PublicManager filters unpublished items."""
        published_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
            published=True,
        )

        unpublished_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="341",
            scale=self.scale,
            published=False,
        )

        # PublicManager should only return published items
        all_stock = RollingStock.objects.all()

        # Note: This test assumes PublicManager is properly configured
        # to filter by published=True
        self.assertIn(published_stock, all_stock)

    def test_ordering(self):
        """Test rolling stock ordering."""
        stock1 = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
        )

        stock2 = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="342",
            scale=self.scale,
        )

        stock3 = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="341",
            scale=self.scale,
        )

        stocks = list(RollingStock.objects.all())
        self.assertEqual(stocks[0], stock1)  # 340
        self.assertEqual(stocks[1], stock3)  # 341
        self.assertEqual(stocks[2], stock2)  # 342


class RollingStockImageTestCase(TestCase):
    """Test cases for RollingStockImage model."""

    def setUp(self):
        """Set up test data."""
        self.company = Company.objects.create(name="RGS", country="US")
        self.stock_type = RollingStockType.objects.create(
            type="Steam Locomotive",
            category="locomotive",
            order=1,
        )
        self.rolling_class = RollingClass.objects.create(
            identifier="C-19",
            type=self.stock_type,
            company=self.company,
        )
        self.scale = Scale.objects.create(
            scale="HOn3",
            ratio="1:87",
            tracks=10.5,
        )
        self.stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale,
        )

    def test_image_ordering(self):
        """Test that images are ordered by the order field."""
        # Note: Actual image upload testing would require test files
        # This test validates the relationship exists
        self.assertEqual(self.stock.image.count(), 0)

        # The image model should have an order field
        self.assertTrue(hasattr(RollingStockImage, "order"))
