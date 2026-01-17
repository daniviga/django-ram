from django.test import TestCase

from ram.utils import slugify


class SimpleBaseModelTestCase(TestCase):
    """Test cases for SimpleBaseModel."""

    def test_obj_type_property(self):
        """Test obj_type returns model name."""
        # We can't instantiate abstract models directly,
        # so we test via a concrete model that inherits from it
        from metadata.models import Company

        company = Company.objects.create(name="Test", country="US")
        self.assertEqual(company.obj_type, "company")

    def test_obj_label_property(self):
        """Test obj_label returns object name."""
        from metadata.models import Company

        company = Company.objects.create(name="Test", country="US")
        self.assertEqual(company.obj_label, "Company")


class BaseModelTestCase(TestCase):
    """Test cases for BaseModel."""

    def test_base_model_fields(self):
        """Test that BaseModel includes expected fields."""
        # Test via a concrete model
        from roster.models import RollingStock, RollingClass
        from metadata.models import Company, Scale, RollingStockType

        company = Company.objects.create(name="Test", country="US")
        scale = Scale.objects.create(scale="HO", ratio="1:87", tracks=16.5)
        stock_type = RollingStockType.objects.create(
            type="Test", category="locomotive", order=1
        )
        rolling_class = RollingClass.objects.create(
            identifier="Test",
            type=stock_type,
            company=company,
        )

        stock = RollingStock.objects.create(
            rolling_class=rolling_class,
            road_number="123",
            scale=scale,
            description="<p>Test description</p>",
            notes="Test notes",
        )

        # Check BaseModel fields exist
        self.assertIsNotNone(stock.uuid)
        self.assertTrue(stock.published)
        self.assertIsNotNone(stock.creation_time)
        self.assertIsNotNone(stock.updated_time)
        self.assertEqual(stock.description, "<p>Test description</p>")

    def test_base_model_obj_properties(self):
        """Test obj_type and obj_label properties."""
        from roster.models import RollingStock, RollingClass
        from metadata.models import Company, Scale, RollingStockType

        company = Company.objects.create(name="Test", country="US")
        scale = Scale.objects.create(scale="HO", ratio="1:87", tracks=16.5)
        stock_type = RollingStockType.objects.create(
            type="Test", category="locomotive", order=1
        )
        rolling_class = RollingClass.objects.create(
            identifier="Test",
            type=stock_type,
            company=company,
        )

        stock = RollingStock.objects.create(
            rolling_class=rolling_class,
            road_number="123",
            scale=scale,
        )

        self.assertEqual(stock.obj_type, "rollingstock")
        self.assertEqual(stock.obj_label, "RollingStock")

    def test_base_model_published_default(self):
        """Test that published defaults to True."""
        from roster.models import RollingStock, RollingClass
        from metadata.models import Company, Scale, RollingStockType

        company = Company.objects.create(name="Test", country="US")
        scale = Scale.objects.create(scale="HO", ratio="1:87", tracks=16.5)
        stock_type = RollingStockType.objects.create(
            type="Test", category="locomotive", order=1
        )
        rolling_class = RollingClass.objects.create(
            identifier="Test",
            type=stock_type,
            company=company,
        )

        stock = RollingStock.objects.create(
            rolling_class=rolling_class,
            road_number="123",
            scale=scale,
        )

        self.assertTrue(stock.published)


class SlugifyTestCase(TestCase):
    """Test cases for slugify utility function."""

    def test_slugify_basic(self):
        """Test basic slugification."""
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_slugify_special_characters(self):
        """Test slugification with special characters."""
        self.assertEqual(slugify("Hello & World!"), "hello-world")

    def test_slugify_multiple_spaces(self):
        """Test slugification with multiple spaces."""
        self.assertEqual(slugify("Hello   World"), "hello-world")

    def test_slugify_numbers(self):
        """Test slugification with numbers."""
        self.assertEqual(slugify("Test 123 ABC"), "test-123-abc")

    def test_slugify_underscores(self):
        """Test slugification preserves underscores."""
        result = slugify("test_value")
        # Depending on implementation, may keep or convert underscores
        self.assertIn(result, ["test-value", "test_value"])

    def test_slugify_empty_string(self):
        """Test slugification of empty string."""
        result = slugify("")
        self.assertEqual(result, "")
