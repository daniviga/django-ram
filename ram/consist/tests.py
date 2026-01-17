from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from consist.models import Consist, ConsistItem
from roster.models import RollingClass, RollingStock
from metadata.models import Company, Scale, RollingStockType


class ConsistTestCase(TestCase):
    """Test cases for Consist model."""

    def setUp(self):
        """Set up test data."""
        self.company = Company.objects.create(
            name="Rio Grande Southern",
            country="US",
        )

        self.scale = Scale.objects.create(
            scale="HOn3",
            ratio="1:87",
            tracks=10.5,
        )

    def test_consist_creation(self):
        """Test creating a consist."""
        consist = Consist.objects.create(
            identifier="RGS Freight #1",
            company=self.company,
            scale=self.scale,
            era="1930s",
        )

        self.assertEqual(str(consist), "Rio Grande Southern RGS Freight #1")
        self.assertEqual(consist.identifier, "RGS Freight #1")
        self.assertEqual(consist.era, "1930s")

    def test_consist_country_property(self):
        """Test that consist inherits country from company."""
        consist = Consist.objects.create(
            identifier="Test Consist",
            company=self.company,
            scale=self.scale,
        )

        self.assertEqual(consist.country, self.company.country)

    def test_consist_dcc_address(self):
        """Test consist with DCC address."""
        consist = Consist.objects.create(
            identifier="DCC Consist",
            company=self.company,
            scale=self.scale,
            consist_address=99,
        )

        self.assertEqual(consist.consist_address, 99)

    def test_consist_get_absolute_url(self):
        """Test get_absolute_url returns correct URL."""
        consist = Consist.objects.create(
            identifier="Test Consist",
            company=self.company,
            scale=self.scale,
        )

        url = consist.get_absolute_url()
        self.assertIn(str(consist.uuid), url)


class ConsistItemTestCase(TestCase):
    """Test cases for ConsistItem model."""

    def setUp(self):
        """Set up test data."""
        self.company = Company.objects.create(name="RGS", country="US")

        self.scale_hon3 = Scale.objects.create(
            scale="HOn3",
            ratio="1:87",
            tracks=10.5,
        )

        self.scale_ho = Scale.objects.create(
            scale="HO",
            ratio="1:87",
            tracks=16.5,
        )

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

        self.consist = Consist.objects.create(
            identifier="Test Consist",
            company=self.company,
            scale=self.scale_hon3,
            published=True,
        )

        self.rolling_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="340",
            scale=self.scale_hon3,
            published=True,
        )

    def test_consist_item_creation(self):
        """Test creating a consist item."""
        item = ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
            load=False,
        )

        self.assertEqual(str(item), "RGS C-19 340")
        self.assertEqual(item.order, 1)
        self.assertFalse(item.load)

    def test_consist_item_unique_constraint(self):
        """Test that consist+rolling_stock must be unique."""
        ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
        )

        # Cannot add same rolling stock to same consist twice
        with self.assertRaises(IntegrityError):
            ConsistItem.objects.create(
                consist=self.consist,
                rolling_stock=self.rolling_stock,
                order=2,
            )

    def test_consist_item_scale_validation(self):
        """Test that consist item scale must match consist scale."""
        different_scale_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="341",
            scale=self.scale_ho,  # Different scale
        )

        item = ConsistItem(
            consist=self.consist,
            rolling_stock=different_scale_stock,
            order=1,
            load=False,
        )

        with self.assertRaises(ValidationError):
            item.clean()

    def test_consist_item_load_ratio_validation(self):
        """Test that load ratio must match consist ratio."""
        different_scale = Scale.objects.create(
            scale="N",
            ratio="1:160",  # Different ratio
            tracks=9.0,
        )

        load_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="342",
            scale=different_scale,
        )

        item = ConsistItem(
            consist=self.consist,
            rolling_stock=load_stock,
            order=1,
            load=True,
        )

        with self.assertRaises(ValidationError):
            item.clean()

    def test_consist_item_published_validation(self):
        """Test that unpublished stock cannot be in published consist."""
        unpublished_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="343",
            scale=self.scale_hon3,
            published=False,
        )

        item = ConsistItem(
            consist=self.consist,
            rolling_stock=unpublished_stock,
            order=1,
        )

        with self.assertRaises(ValidationError):
            item.clean()

    def test_consist_item_properties(self):
        """Test consist item properties."""
        item = ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
        )

        self.assertEqual(item.scale, self.rolling_stock.scale)
        self.assertEqual(item.company, self.rolling_stock.company)
        self.assertEqual(item.type, self.stock_type.type)

    def test_consist_length_calculation(self):
        """Test consist length calculation."""
        # Add three items (not loads)
        for i in range(3):
            stock = RollingStock.objects.create(
                rolling_class=self.rolling_class,
                road_number=str(340 + i),
                scale=self.scale_hon3,
            )
            ConsistItem.objects.create(
                consist=self.consist,
                rolling_stock=stock,
                order=i + 1,
                load=False,
            )

        self.assertEqual(self.consist.length, 3)

    def test_consist_length_excludes_loads(self):
        """Test that consist length excludes loads."""
        # Add one regular item
        ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
            load=False,
        )

        # Add one load (same ratio, different scale tracks OK for loads)
        load_stock = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="LOAD-1",
            scale=self.scale_hon3,
        )
        ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=load_stock,
            order=2,
            load=True,
        )

        # Length should only count non-load items
        self.assertEqual(self.consist.length, 1)

    def test_consist_item_ordering(self):
        """Test consist items are ordered by order field."""
        stock2 = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="341",
            scale=self.scale_hon3,
        )
        stock3 = RollingStock.objects.create(
            rolling_class=self.rolling_class,
            road_number="342",
            scale=self.scale_hon3,
        )

        item3 = ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=stock3,
            order=3,
        )
        item1 = ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
        )
        item2 = ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=stock2,
            order=2,
        )

        items = list(self.consist.consist_item.all())
        self.assertEqual(items[0], item1)
        self.assertEqual(items[1], item2)
        self.assertEqual(items[2], item3)

    def test_unpublish_consist_signal(self):
        """Test that unpublishing rolling stock unpublishes consists."""
        # Create a consist item
        ConsistItem.objects.create(
            consist=self.consist,
            rolling_stock=self.rolling_stock,
            order=1,
        )

        self.assertTrue(self.consist.published)

        # Unpublish the rolling stock
        self.rolling_stock.published = False
        self.rolling_stock.save()

        # Reload consist from database
        self.consist.refresh_from_db()

        # Consist should now be unpublished
        self.assertFalse(self.consist.published)
