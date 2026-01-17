from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from metadata.models import (
    Manufacturer,
    Company,
    Scale,
    RollingStockType,
    Decoder,
    Shop,
    Tag,
    calculate_ratio,
)


class ManufacturerTestCase(TestCase):
    """Test cases for Manufacturer model."""

    def test_manufacturer_creation(self):
        """Test creating a manufacturer."""
        manufacturer = Manufacturer.objects.create(
            name="Blackstone Models",
            category="model",
            country="US",
            website="https://www.blackstonemodels.com",
        )

        self.assertEqual(str(manufacturer), "Blackstone Models")
        self.assertEqual(manufacturer.slug, "blackstone-models")
        self.assertEqual(manufacturer.category, "model")

    def test_manufacturer_slug_auto_generation(self):
        """Test that slug is automatically generated."""
        manufacturer = Manufacturer.objects.create(
            name="Baldwin Locomotive Works",
            category="real",
        )

        self.assertEqual(manufacturer.slug, "baldwin-locomotive-works")

    def test_manufacturer_unique_constraint(self):
        """Test that name+category must be unique."""
        Manufacturer.objects.create(
            name="Baldwin",
            category="real",
        )

        # Should not be able to create another with same name+category
        with self.assertRaises(IntegrityError):
            Manufacturer.objects.create(
                name="Baldwin",
                category="real",
            )

    def test_manufacturer_different_categories(self):
        """Test that same name is allowed with different categories."""
        Manufacturer.objects.create(
            name="Baldwin",
            category="real",
        )

        # Should be able to create with different category
        manufacturer2 = Manufacturer.objects.create(
            name="Alco",
            category="model",
        )

        self.assertEqual(manufacturer2.name, "Alco")
        self.assertIsNotNone(manufacturer2.pk)

    def test_manufacturer_website_short(self):
        """Test website_short extracts domain."""
        manufacturer = Manufacturer.objects.create(
            name="Test Manufacturer",
            category="model",
            website="https://www.example.com/path",
        )

        self.assertEqual(manufacturer.website_short(), "example.com")

    def test_manufacturer_ordering(self):
        """Test manufacturer ordering by category and slug."""
        m1 = Manufacturer.objects.create(name="Zebra", category="model")
        m2 = Manufacturer.objects.create(name="Alpha", category="accessory")
        m3 = Manufacturer.objects.create(name="Beta", category="model")

        manufacturers = list(Manufacturer.objects.all())
        # Ordered by category, then slug
        self.assertEqual(manufacturers[0], m2)  # accessory comes first
        self.assertTrue(manufacturers.index(m3) < manufacturers.index(m1))


class CompanyTestCase(TestCase):
    """Test cases for Company model."""

    def test_company_creation(self):
        """Test creating a company."""
        company = Company.objects.create(
            name="RGS",
            extended_name="Rio Grande Southern Railroad",
            country="US",
            freelance=False,
        )

        self.assertEqual(str(company), "RGS")
        self.assertEqual(company.slug, "rgs")
        self.assertEqual(company.extended_name, "Rio Grande Southern Railroad")

    def test_company_slug_generation(self):
        """Test automatic slug generation."""
        company = Company.objects.create(
            name="Denver & Rio Grande Western",
            country="US",
        )

        self.assertEqual(company.slug, "denver-rio-grande-western")

    def test_company_unique_name(self):
        """Test that company name must be unique."""
        Company.objects.create(name="RGS", country="US")

        with self.assertRaises(IntegrityError):
            Company.objects.create(name="RGS", country="GB")

    def test_company_extended_name_pp(self):
        """Test extended name pretty print."""
        company = Company.objects.create(
            name="RGS",
            extended_name="Rio Grande Southern Railroad",
            country="US",
        )

        self.assertEqual(
            company.extended_name_pp(),
            "(Rio Grande Southern Railroad)"
        )

    def test_company_extended_name_pp_empty(self):
        """Test extended name pretty print when empty."""
        company = Company.objects.create(name="RGS", country="US")

        self.assertEqual(company.extended_name_pp(), "")

    def test_company_freelance_flag(self):
        """Test freelance flag."""
        company = Company.objects.create(
            name="Fake Railroad",
            country="US",
            freelance=True,
        )

        self.assertTrue(company.freelance)


class ScaleTestCase(TestCase):
    """Test cases for Scale model."""

    def test_scale_creation(self):
        """Test creating a scale."""
        scale = Scale.objects.create(
            scale="HOn3",
            ratio="1:87",
            tracks=10.5,
            gauge="3 ft",
        )

        self.assertEqual(str(scale), "HOn3")
        self.assertEqual(scale.slug, "hon3")
        self.assertEqual(scale.ratio, "1:87")
        self.assertEqual(scale.tracks, 10.5)

    def test_scale_ratio_calculation(self):
        """Test automatic ratio_int calculation."""
        scale = Scale.objects.create(
            scale="HO",
            ratio="1:87",
            tracks=16.5,
        )

        # 1/87 * 10000 = 114.94...
        self.assertAlmostEqual(scale.ratio_int, 114, delta=1)

    def test_scale_ratio_validation_valid(self):
        """Test that valid ratios are accepted."""
        ratios = ["1:87", "1:160", "1:22.5", "1:48"]

        for ratio in ratios:
            result = calculate_ratio(ratio)
            self.assertIsInstance(result, (int, float))

    def test_scale_ratio_validation_invalid(self):
        """Test that invalid ratios raise ValidationError."""
        with self.assertRaises(ValidationError):
            calculate_ratio("invalid")

        with self.assertRaises(ValidationError):
            calculate_ratio("1:0")  # Division by zero

    def test_scale_ordering(self):
        """Test scale ordering by ratio_int (descending)."""
        s1 = Scale.objects.create(scale="G", ratio="1:22.5", tracks=45.0)
        s2 = Scale.objects.create(scale="HO", ratio="1:87", tracks=16.5)
        s3 = Scale.objects.create(scale="N", ratio="1:160", tracks=9.0)

        scales = list(Scale.objects.all())
        # Ordered by -ratio_int (larger ratios first)
        self.assertEqual(scales[0], s1)  # G scale (largest)
        self.assertEqual(scales[1], s2)  # HO scale
        self.assertEqual(scales[2], s3)  # N scale (smallest)


class RollingStockTypeTestCase(TestCase):
    """Test cases for RollingStockType model."""

    def test_rolling_stock_type_creation(self):
        """Test creating a rolling stock type."""
        stock_type = RollingStockType.objects.create(
            type="Steam Locomotive",
            category="locomotive",
            order=1,
        )

        self.assertEqual(str(stock_type), "Steam Locomotive locomotive")
        self.assertEqual(stock_type.slug, "steam-locomotive-locomotive")

    def test_rolling_stock_type_unique_constraint(self):
        """Test that category+type must be unique."""
        RollingStockType.objects.create(
            type="Steam Locomotive",
            category="locomotive",
            order=1,
        )

        with self.assertRaises(IntegrityError):
            RollingStockType.objects.create(
                type="Steam Locomotive",
                category="locomotive",
                order=2,
            )

    def test_rolling_stock_type_ordering(self):
        """Test ordering by order field."""
        t3 = RollingStockType.objects.create(
            type="Caboose", category="railcar", order=3
        )
        t1 = RollingStockType.objects.create(
            type="Steam", category="locomotive", order=1
        )
        t2 = RollingStockType.objects.create(
            type="Boxcar", category="railcar", order=2
        )

        types = list(RollingStockType.objects.all())
        self.assertEqual(types[0], t1)
        self.assertEqual(types[1], t2)
        self.assertEqual(types[2], t3)


class DecoderTestCase(TestCase):
    """Test cases for Decoder model."""

    def setUp(self):
        """Set up test data."""
        self.manufacturer = Manufacturer.objects.create(
            name="ESU",
            category="accessory",
            country="DE",
        )

    def test_decoder_creation(self):
        """Test creating a decoder."""
        decoder = Decoder.objects.create(
            name="LokSound 5",
            manufacturer=self.manufacturer,
            version="5.0",
            sound=True,
        )

        self.assertEqual(str(decoder), "ESU - LokSound 5")
        self.assertTrue(decoder.sound)

    def test_decoder_without_sound(self):
        """Test creating a non-sound decoder."""
        decoder = Decoder.objects.create(
            name="LokPilot 5",
            manufacturer=self.manufacturer,
            sound=False,
        )

        self.assertFalse(decoder.sound)

    def test_decoder_ordering(self):
        """Test decoder ordering by manufacturer name and decoder name."""
        man2 = Manufacturer.objects.create(
            name="Digitrax",
            category="accessory",
        )

        d1 = Decoder.objects.create(
            name="LokSound 5",
            manufacturer=self.manufacturer,
        )
        d2 = Decoder.objects.create(
            name="DZ123",
            manufacturer=man2,
        )
        d3 = Decoder.objects.create(
            name="LokPilot 5",
            manufacturer=self.manufacturer,
        )

        decoders = list(Decoder.objects.all())
        # Ordered by manufacturer name, then decoder name
        self.assertEqual(decoders[0], d2)  # Digitrax
        self.assertTrue(decoders.index(d3) < decoders.index(d1))  # LokPilot before LokSound


class ShopTestCase(TestCase):
    """Test cases for Shop model."""

    def test_shop_creation(self):
        """Test creating a shop."""
        shop = Shop.objects.create(
            name="Caboose Hobbies",
            country="US",
            website="https://www.caboosehobbies.com",
            on_line=True,
            active=True,
        )

        self.assertEqual(str(shop), "Caboose Hobbies")
        self.assertTrue(shop.on_line)
        self.assertTrue(shop.active)

    def test_shop_defaults(self):
        """Test shop default values."""
        shop = Shop.objects.create(name="Local Shop")

        self.assertTrue(shop.on_line)  # Default True
        self.assertTrue(shop.active)   # Default True

    def test_shop_offline(self):
        """Test creating an offline shop."""
        shop = Shop.objects.create(
            name="Brick and Mortar Store",
            on_line=False,
        )

        self.assertFalse(shop.on_line)


class TagTestCase(TestCase):
    """Test cases for Tag model."""

    def test_tag_creation(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            name="Narrow Gauge",
            slug="narrow-gauge",
        )

        self.assertEqual(str(tag), "Narrow Gauge")
        self.assertEqual(tag.slug, "narrow-gauge")

    def test_tag_unique_name(self):
        """Test that tag name must be unique."""
        Tag.objects.create(name="Narrow Gauge", slug="narrow-gauge")

        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Narrow Gauge", slug="narrow-gauge")
