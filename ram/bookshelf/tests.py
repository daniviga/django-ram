from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from bookshelf.models import (
    Author,
    Publisher,
    Book,
    Catalog,
    Magazine,
    MagazineIssue,
    TocEntry,
)
from metadata.models import Manufacturer, Scale


class AuthorTestCase(TestCase):
    """Test cases for Author model."""

    def test_author_creation(self):
        """Test creating an author."""
        author = Author.objects.create(
            first_name="John",
            last_name="Smith",
        )

        self.assertEqual(str(author), "Smith, John")
        self.assertEqual(author.first_name, "John")
        self.assertEqual(author.last_name, "Smith")

    def test_author_short_name(self):
        """Test author short name property."""
        author = Author.objects.create(
            first_name="John",
            last_name="Smith",
        )

        self.assertEqual(author.short_name, "Smith J.")

    def test_author_ordering(self):
        """Test author ordering by last name, first name."""
        a1 = Author.objects.create(first_name="John", last_name="Smith")
        a2 = Author.objects.create(first_name="Jane", last_name="Doe")
        a3 = Author.objects.create(first_name="Bob", last_name="Smith")

        authors = list(Author.objects.all())
        self.assertEqual(authors[0], a2)  # Doe comes first
        self.assertEqual(authors[1], a3)  # Smith, Bob
        self.assertEqual(authors[2], a1)  # Smith, John


class PublisherTestCase(TestCase):
    """Test cases for Publisher model."""

    def test_publisher_creation(self):
        """Test creating a publisher."""
        publisher = Publisher.objects.create(
            name="Model Railroader",
            country="US",
            website="https://www.modelrailroader.com",
        )

        self.assertEqual(str(publisher), "Model Railroader")
        self.assertEqual(publisher.country.code, "US")

    def test_publisher_ordering(self):
        """Test publisher ordering by name."""
        p1 = Publisher.objects.create(name="Zebra Publishing")
        p2 = Publisher.objects.create(name="Alpha Books")
        p3 = Publisher.objects.create(name="Model Railroader")

        publishers = list(Publisher.objects.all())
        self.assertEqual(publishers[0], p2)
        self.assertEqual(publishers[1], p3)
        self.assertEqual(publishers[2], p1)


class BookTestCase(TestCase):
    """Test cases for Book model."""

    def setUp(self):
        """Set up test data."""
        self.publisher = Publisher.objects.create(
            name="Kalmbach Publishing",
            country="US",
        )

        self.author = Author.objects.create(
            first_name="Tony",
            last_name="Koester",
        )

    def test_book_creation(self):
        """Test creating a book."""
        book = Book.objects.create(
            title="Model Railroad Planning",
            publisher=self.publisher,
            ISBN="978-0-89024-567-8",
            language="en",
            number_of_pages=128,
            publication_year=2010,
            price=Decimal("24.95"),
        )

        self.assertEqual(str(book), "Model Railroad Planning")
        self.assertEqual(book.publisher_name, "Kalmbach Publishing")
        self.assertTrue(book.published)  # Default from BaseModel

    def test_book_authors_relationship(self):
        """Test many-to-many relationship with authors."""
        book = Book.objects.create(
            title="Test Book",
            publisher=self.publisher,
        )

        author2 = Author.objects.create(
            first_name="John",
            last_name="Doe",
        )

        book.authors.add(self.author, author2)

        self.assertEqual(book.authors.count(), 2)
        self.assertIn(self.author, book.authors.all())

    def test_book_authors_list_property(self):
        """Test authors_list property."""
        book = Book.objects.create(
            title="Test Book",
            publisher=self.publisher,
        )

        book.authors.add(self.author)

        self.assertEqual(book.authors_list, "Koester T.")

    def test_book_ordering(self):
        """Test book ordering by title."""
        b1 = Book.objects.create(
            title="Zebra Book",
            publisher=self.publisher,
        )
        b2 = Book.objects.create(
            title="Alpha Book",
            publisher=self.publisher,
        )

        books = list(Book.objects.all())
        self.assertEqual(books[0], b2)
        self.assertEqual(books[1], b1)


class CatalogTestCase(TestCase):
    """Test cases for Catalog model."""

    def setUp(self):
        """Set up test data."""
        self.manufacturer = Manufacturer.objects.create(
            name="Bachmann",
            category="model",
            country="US",
        )

        self.scale_ho = Scale.objects.create(
            scale="HO",
            ratio="1:87",
            tracks=16.5,
        )

        self.scale_n = Scale.objects.create(
            scale="N",
            ratio="1:160",
            tracks=9.0,
        )

    def test_catalog_creation(self):
        """Test creating a catalog."""
        catalog = Catalog.objects.create(
            manufacturer=self.manufacturer,
            years="2023",
            publication_year=2023,
        )
        catalog.scales.add(self.scale_ho)

        # Refresh to get the correct string representation
        catalog.refresh_from_db()

        self.assertIn("Bachmann", str(catalog))
        self.assertIn("2023", str(catalog))

    def test_catalog_multiple_scales(self):
        """Test catalog with multiple scales."""
        catalog = Catalog.objects.create(
            manufacturer=self.manufacturer,
            years="2023",
        )

        catalog.scales.add(self.scale_ho, self.scale_n)

        scales_str = catalog.get_scales()
        self.assertIn("HO", scales_str)
        self.assertIn("N", scales_str)

    def test_catalog_ordering(self):
        """Test catalog ordering by manufacturer and year."""
        man2 = Manufacturer.objects.create(
            name="Atlas",
            category="model",
        )

        c1 = Catalog.objects.create(
            manufacturer=self.manufacturer,
            years="2023",
            publication_year=2023,
        )
        c2 = Catalog.objects.create(
            manufacturer=man2,
            years="2023",
            publication_year=2023,
        )
        c3 = Catalog.objects.create(
            manufacturer=self.manufacturer,
            years="2022",
            publication_year=2022,
        )

        catalogs = list(Catalog.objects.all())
        # Should be ordered by manufacturer name, then year
        self.assertEqual(catalogs[0], c2)  # Atlas


class MagazineTestCase(TestCase):
    """Test cases for Magazine model."""

    def setUp(self):
        """Set up test data."""
        self.publisher = Publisher.objects.create(
            name="Kalmbach Publishing",
            country="US",
        )

    def test_magazine_creation(self):
        """Test creating a magazine."""
        magazine = Magazine.objects.create(
            name="Model Railroader",
            publisher=self.publisher,
            website="https://www.modelrailroader.com",
            ISBN="0746-9896",
            language="en",
        )

        self.assertEqual(str(magazine), "Model Railroader")
        self.assertEqual(magazine.publisher, self.publisher)

    def test_magazine_website_short(self):
        """Test website_short method."""
        magazine = Magazine.objects.create(
            name="Model Railroader",
            publisher=self.publisher,
            website="https://www.modelrailroader.com",
        )

        self.assertEqual(magazine.website_short(), "modelrailroader.com")

    def test_magazine_get_cover_no_image(self):
        """Test get_cover when magazine has no image."""
        magazine = Magazine.objects.create(
            name="Test Magazine",
            publisher=self.publisher,
        )

        # Should return None if no cover image exists
        self.assertIsNone(magazine.get_cover())


class MagazineIssueTestCase(TestCase):
    """Test cases for MagazineIssue model."""

    def setUp(self):
        """Set up test data."""
        self.publisher = Publisher.objects.create(
            name="Kalmbach Publishing",
        )

        self.magazine = Magazine.objects.create(
            name="Model Railroader",
            publisher=self.publisher,
            published=True,
        )

    def test_magazine_issue_creation(self):
        """Test creating a magazine issue."""
        issue = MagazineIssue.objects.create(
            magazine=self.magazine,
            issue_number="January 2023",
            publication_year=2023,
            publication_month=1,
            number_of_pages=96,
        )

        self.assertEqual(str(issue), "Model Railroader - January 2023")
        self.assertEqual(issue.obj_label, "Magazine Issue")

    def test_magazine_issue_unique_together(self):
        """Test that magazine+issue_number must be unique."""
        MagazineIssue.objects.create(
            magazine=self.magazine,
            issue_number="January 2023",
        )

        with self.assertRaises(IntegrityError):
            MagazineIssue.objects.create(
                magazine=self.magazine,
                issue_number="January 2023",
            )

    def test_magazine_issue_validation(self):
        """Test that published issue requires published magazine."""
        unpublished_magazine = Magazine.objects.create(
            name="Unpublished Magazine",
            publisher=self.publisher,
            published=False,
        )

        issue = MagazineIssue(
            magazine=unpublished_magazine,
            issue_number="Test Issue",
            published=True,
        )

        with self.assertRaises(ValidationError):
            issue.clean()

    def test_magazine_issue_publisher_property(self):
        """Test that issue inherits publisher from magazine."""
        issue = MagazineIssue.objects.create(
            magazine=self.magazine,
            issue_number="January 2023",
        )

        self.assertEqual(issue.publisher, self.publisher)


class TocEntryTestCase(TestCase):
    """Test cases for TocEntry model."""

    def setUp(self):
        """Set up test data."""
        publisher = Publisher.objects.create(name="Test Publisher")

        self.book = Book.objects.create(
            title="Test Book",
            publisher=publisher,
            number_of_pages=200,
        )

    def test_toc_entry_creation(self):
        """Test creating a table of contents entry."""
        entry = TocEntry.objects.create(
            book=self.book,
            title="Introduction to Model Railroading",
            subtitle="Getting Started",
            authors="John Doe",
            page=10,
        )

        self.assertIn("Introduction to Model Railroading", str(entry))
        self.assertIn("Getting Started", str(entry))
        self.assertIn("p. 10", str(entry))

    def test_toc_entry_without_subtitle(self):
        """Test TOC entry without subtitle."""
        entry = TocEntry.objects.create(
            book=self.book,
            title="Chapter One",
            page=5,
        )

        self.assertEqual(str(entry), "Chapter One (p. 5)")

    def test_toc_entry_page_validation_required(self):
        """Test that page number is required."""
        entry = TocEntry(
            book=self.book,
            title="Test Entry",
            page=None,
        )

        with self.assertRaises(ValidationError):
            entry.clean()

    def test_toc_entry_page_validation_min(self):
        """Test that page number must be >= 1."""
        entry = TocEntry(
            book=self.book,
            title="Test Entry",
            page=0,
        )

        with self.assertRaises(ValidationError):
            entry.clean()

    def test_toc_entry_page_validation_exceeds_book(self):
        """Test that page number cannot exceed book's page count."""
        entry = TocEntry(
            book=self.book,
            title="Test Entry",
            page=250,  # Book has 200 pages
        )

        with self.assertRaises(ValidationError):
            entry.clean()

    def test_toc_entry_ordering(self):
        """Test TOC entries are ordered by page number."""
        e1 = TocEntry.objects.create(
            book=self.book,
            title="Chapter Three",
            page=30,
        )
        e2 = TocEntry.objects.create(
            book=self.book,
            title="Chapter One",
            page=10,
        )
        e3 = TocEntry.objects.create(
            book=self.book,
            title="Chapter Two",
            page=20,
        )

        entries = list(TocEntry.objects.all())
        self.assertEqual(entries[0], e2)  # Page 10
        self.assertEqual(entries[1], e3)  # Page 20
        self.assertEqual(entries[2], e1)  # Page 30
