import base64
import operator
from itertools import chain
from functools import reduce
from urllib.parse import unquote

from django.conf import settings
from django.views import View
from django.http import Http404, HttpResponseBadRequest
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import F, Q, Count
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from portal.utils import get_site_conf
from portal.models import Flatpage
from roster.models import RollingStock
from consist.models import Consist
from bookshelf.models import Book, Catalog, Magazine, MagazineIssue
from metadata.models import (
    Company,
    Manufacturer,
    Scale,
    RollingStockType,
    Tag,
)


def get_items_per_page():
    try:
        items_per_page = get_site_conf().items_per_page
    except (OperationalError, ProgrammingError):
        items_per_page = 6
    return int(items_per_page)


def get_items_ordering(config="items_ordering"):
    try:
        order_by = getattr(get_site_conf(), config)
    except (OperationalError, ProgrammingError):
        order_by = "type"

    fields = [
        "rolling_class__type",              # 0
        "rolling_class__company",           # 1
        "rolling_class__company__country",  # 2
        "rolling_class__identifier",        # 3
        "road_number_int",                  # 4
    ]

    order_map = {
        "type": (0, 1, 3, 4),
        "company": (1, 0, 3, 4),
        "country": (2, 0, 1, 3, 4),
        "cou+com": (2, 1, 0, 3, 4),
        "class": (0, 3, 1, 4),
    }

    return tuple(fields[i] for i in order_map.get(order_by, "type"))


class Render404(View):
    def get(self, request, exception):
        return render(request, "base.html", {"title": "404 page not found"})


class GetData(View):
    title = None
    template = "pagination.html"
    filter = Q()  # empty filter by default

    def get_data(self, request):
        return (
            RollingStock.objects.get_published(request.user)
            .order_by(*get_items_ordering())
            .filter(self.filter)
        )

    def get(self, request, page=1):
        if self.title is None or self.template is None:
            raise Exception("title and template must be defined")

        data = list(self.get_data(request))

        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return render(
            request,
            self.template,
            {
                "title": self.title,
                "data": data,
                "matches": paginator.count,
                "page_range": page_range,
            },
        )


class GetHome(GetData):
    title = "Home"
    template = "home.html"

    def get_data(self, request):
        max_items = min(settings.FEATURED_ITEMS_MAX, get_items_per_page())
        return (
            RollingStock.objects.get_published(request.user)
            .filter(featured=True)
            .order_by(*get_items_ordering(config="featured_items_ordering"))[
                :max_items
            ]
        ) or super().get_data(request)


class GetRoster(GetData):
    title = "The Roster"


class SearchObjects(View):
    def run_search(self, request, search, _filter, page=1):
        """
        Run the search query on the database and return the results.
        param request: HTTP request
        param search: search string
        param _filter: filter to apply (type, company, manufacturer, scale)
        param page: page number for pagination
        return: tuple (data, matches, page_range)
        1. data: list of dicts with keys "type" and "item"
        2. matches: total number of matches
        3. page_range: elided page range for pagination
        """
        if _filter is None:
            query = reduce(
                operator.or_,
                (
                    Q(
                        Q(rolling_class__identifier__icontains=s)
                        | Q(rolling_class__description__icontains=s)
                        | Q(rolling_class__type__type__icontains=s)
                        | Q(road_number__icontains=s)
                        | Q(item_number=s)
                        | Q(rolling_class__company__name__icontains=s)
                        | Q(rolling_class__company__country__icontains=s)
                        | Q(manufacturer__name__icontains=s)
                        | Q(scale__scale__icontains=s)
                        | Q(tags__name__icontains=s)
                    )
                    for s in search.split()
                ),
            )
        elif _filter == "type":
            query = Q(
                Q(rolling_class__type__type__icontains=search)
                | Q(rolling_class__type__category__icontains=search)
            )
        elif _filter == "company":
            query = Q(
                Q(rolling_class__company__name__icontains=search)
                | Q(rolling_class__company__extended_name__icontains=search)
            )
        elif _filter == "manufacturer":
            query = Q(
                Q(manufacturer__name__icontains=search)
                | Q(rolling_class__manufacturer__name__icontains=search)
            )
        elif _filter == "scale":
            query = Q(scale__scale__icontains=search)
        else:
            raise Http404

        # FIXME duplicated code!
        # FIXME see if it makes sense to filter calatogs and books by scale
        #       and manufacturer as well
        roster = (
            RollingStock.objects.get_published(request.user)
            .filter(query)
            .distinct()
            .order_by(*get_items_ordering())
        )
        data = list(roster)

        if _filter is None:
            consists = (
                Consist.objects.get_published(request.user)
                .filter(
                    Q(
                        Q(identifier__icontains=search)
                        | Q(company__name__icontains=search)
                    )
                )
                .distinct()
            )
            data = list(chain(data, consists))
            books = (
                Book.objects.get_published(request.user)
                .filter(
                    Q(
                        Q(title__icontains=search)
                        | Q(description__icontains=search)
                        | Q(toc__title__icontains=search)
                    )
                )
                .distinct()
            )
            catalogs = (
                Catalog.objects.get_published(request.user)
                .filter(
                    Q(
                        Q(manufacturer__name__icontains=search)
                        | Q(description__icontains=search)
                    )
                )
                .distinct()
            )
            data = list(chain(data, books, catalogs))
            magazine_issues = (
                MagazineIssue.objects.get_published(request.user)
                .filter(
                    Q(
                        Q(magazine__name__icontains=search)
                        | Q(description__icontains=search)
                        | Q(toc__title__icontains=search)
                    )
                )
                .distinct()
            )
            data = list(chain(data, magazine_issues))

        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return data, paginator.count, page_range

    def split_search(self, search):
        search = search.strip().split(":")
        if not search:
            raise Http404
        elif len(search) == 1:  # no filter
            _filter = None
            search = search[0].strip()
        elif len(search) == 2:  # filter: search
            _filter = search[0].strip().lower()
            search = search[1].strip()
        else:
            return HttpResponseBadRequest

        return _filter, search

    def get(self, request, search, page=1):
        try:
            encoded_search = search
            search = base64.b64decode(search.encode()).decode()
        except Exception:
            encoded_search = base64.b64encode(search.encode()).decode()
        _filter, keyword = self.split_search(search)
        data, matches, page_range = self.run_search(
            request, keyword, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "title": 'Search: "{}"'.format(search),
                "search": search,
                "encoded_search": encoded_search,
                "data": data,
                "matches": matches,
                "page_range": page_range,
            },
        )

    def post(self, request, page=1):
        search = request.POST.get("search")
        return self.get(request, search, page)


class GetManufacturerItem(View):
    def get(self, request, manufacturer, search="all", page=1):
        """
        Get all items from a specific manufacturer. If `search` is not "all",
        filter by item number as well, for example to get all itmes from the
        same set.
        The view returns both rolling stock and catalogs.
        param request: HTTP request
        param manufacturer: Manufacturer slug
        param search: item number slug or "all"
        param page: page number for pagination
        return: rendered template
        1. manufacturer: Manufacturer object
        2. search: item number slug or "all"
        3. data: list of dicts with keys "type" and "item"
        4. matches: total number of matches
        5. page_range: elided page range for pagination
        """
        manufacturer = get_object_or_404(
            Manufacturer, slug__iexact=manufacturer
        )
        if search != "all":
            roster = get_list_or_404(
                RollingStock.objects.get_published(request.user).order_by(
                    *get_items_ordering()
                ),
                Q(
                    Q(manufacturer=manufacturer)
                    & Q(item_number_slug__exact=search)
                ),
            )
            catalogs = []  # no catalogs when searching for a specific item
            title = "{0}: {1}".format(
                manufacturer,
                # all returned records must have the same `item_number``;
                # just pick it up the first result, otherwise `search`
                roster[0].item_number if roster else search,
            )
        else:
            roster = (
                RollingStock.objects.get_published(request.user)
                .filter(
                    Q(manufacturer=manufacturer)
                    | Q(rolling_class__manufacturer=manufacturer)
                )
                .distinct()
                .order_by(*get_items_ordering())
            )
            catalogs = Catalog.objects.get_published(request.user).filter(
                manufacturer=manufacturer
            )
            title = "Manufacturer: {0}".format(manufacturer)

        data = list(chain(roster, catalogs))
        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )
        return render(
            request,
            "manufacturer.html",
            {
                "title": title,
                "manufacturer": manufacturer,
                "search": search,
                "data": data,
                "matches": paginator.count,
                "page_range": page_range,
            },
        )


class GetObjectsFiltered(View):
    def run_filter(self, request, search, _filter, page=1):
        if _filter == "type":
            title = get_object_or_404(RollingStockType, slug__iexact=search)
            query = Q(rolling_class__type__slug__iexact=search)
        elif _filter == "company":
            title = get_object_or_404(Company, slug__iexact=search)
            query = Q(rolling_class__company__slug__iexact=search)
            query_2nd = Q(company__slug__iexact=search)
        elif _filter == "scale":
            title = get_object_or_404(Scale, slug__iexact=search)
            query = Q(scale__slug__iexact=search)
            query_2nd = Q(
                consist_item__rolling_stock__scale__slug__iexact=search
            )
        elif _filter == "tag":
            title = get_object_or_404(Tag, slug__iexact=search)
            query = Q(tags__slug__iexact=search)
            query_2nd = query  # For tags the 2nd level query doesn't change
        else:
            raise Http404

        roster = (
            RollingStock.objects.get_published(request.user)
            .filter(query)
            .distinct()
            .order_by(*get_items_ordering())
        )

        data = list(roster)

        if _filter == "scale":
            catalogs = (
                Catalog.objects.get_published(request.user)
                .filter(scales__slug=search)
                .distinct()
            )
            data = list(chain(data, catalogs))

        try:  # Execute only if query_2nd is defined
            consists = (
                Consist.objects.get_published(request.user)
                .filter(query_2nd)
                .distinct()
            )
            data = list(chain(data, consists))
            if _filter == "tag":  # Books can be filtered only by tag
                books = (
                    Book.objects.get_published(request.user)
                    .filter(query_2nd)
                    .distinct()
                )
                catalogs = (
                    Catalog.objects.get_published(request.user)
                    .filter(query_2nd)
                    .distinct()
                )
                magazine_issues = (
                    MagazineIssue.objects.get_published(request.user)
                    .filter(query_2nd)
                    .distinct()
                )
                data = list(chain(data, books, catalogs, magazine_issues))
        except NameError:
            pass

        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return data, title, paginator.count, page_range

    def get(self, request, search, _filter, page=1):
        data, title, matches, page_range = self.run_filter(
            request, unquote(search), _filter, page
        )

        return render(
            request,
            "filter.html",
            {
                "title": "{0}: {1}".format(_filter.capitalize(), title),
                "search": search,
                "filter": _filter,
                "data": data,
                "matches": matches,
                "page_range": page_range,
            },
        )


class GetRollingStock(View):
    def get(self, request, uuid):
        try:
            rolling_stock = RollingStock.objects.get_published(
                request.user
            ).get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404

        # FIXME there's likely a better and more efficient way of doing this
        # but keeping KISS for now
        decoder_documents = []
        class_properties = rolling_stock.rolling_class.property.get_public(
            request.user
        )
        properties = rolling_stock.property.get_public(request.user)
        documents = rolling_stock.document.get_public(request.user)
        journal = rolling_stock.journal.get_public(request.user)
        if rolling_stock.decoder:
            decoder_documents = rolling_stock.decoder.document.get_public(
                request.user
            )

        consists = list(
            Consist.objects.get_published(request.user).filter(
                consist_item__rolling_stock=rolling_stock
            )
        )

        trainset = list(
            RollingStock.objects.get_published(request.user)
            .filter(
                Q(
                    Q(item_number__exact=rolling_stock.item_number)
                    & Q(set=True)
                )
            )
            .order_by(*get_items_ordering())
        )

        return render(
            request,
            "rollingstock.html",
            {
                "title": rolling_stock,
                "rolling_stock": rolling_stock,
                "class_properties": class_properties,
                "properties": properties,
                "decoder_documents": decoder_documents,
                "documents": documents,
                "journal": journal,
                "set": trainset,
                "consists": consists,
            },
        )


class Consists(GetData):
    title = "Consists"

    def get_data(self, request):
        return Consist.objects.get_published(request.user).all()


class GetConsist(View):
    def get(self, request, uuid, page=1):
        try:
            consist = Consist.objects.get_published(request.user).get(
                uuid=uuid
            )
        except ObjectDoesNotExist:
            raise Http404

        data = list(
            RollingStock.objects.get_published(request.user).get(
                uuid=r.rolling_stock_id
            )
            for r in consist.consist_item.filter(load=False)
        )
        loads = list(
            RollingStock.objects.get_published(request.user).get(
                uuid=r.rolling_stock_id
            )
            for r in consist.consist_item.filter(load=True)
        )
        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return render(
            request,
            "consist.html",
            {
                "title": consist,
                "consist": consist,
                "data": data,
                "loads": loads,
                "page_range": page_range,
            },
        )


class Manufacturers(GetData):
    title = "Manufacturers"

    def get_data(self, request):
        return (
            Manufacturer.objects.filter(self.filter)
            .annotate(
                num_rollingstock=(
                    Count(
                        "rollingstock",
                        filter=Q(
                            rollingstock__in=(
                                RollingStock.objects.get_published(
                                    request.user
                                )
                            )
                        ),
                        distinct=True,
                    )
                )
            )
            .annotate(
                num_rollingclass=(
                    Count(
                        "rollingclass__rolling_stock",
                        filter=Q(
                            rollingclass__rolling_stock__in=(
                                RollingStock.objects.get_published(
                                    request.user
                                )
                            ),
                        ),
                        distinct=True,
                    )
                )
            )
            .annotate(
                num_catalogs=(
                    Count(
                        "catalogs",
                        filter=Q(
                            catalogs__in=(
                                Catalog.objects.get_published(request.user)
                            ),
                        ),
                        distinct=True,
                    )
                )
            )
            .annotate(
                num_items=(
                    F("num_rollingstock")
                    + F("num_rollingclass")
                    + F("num_catalogs")
                )
            )
            .order_by("name")
        )

    # overload get method to filter by category
    def get(self, request, category, page=1):
        if category not in ("real", "model"):
            raise Http404
        self.filter = Q(category=category)

        return super().get(request, page)


class Companies(GetData):
    title = "Companies"

    def get_data(self, request):
        return (
            Company.objects.annotate(
                num_rollingstock=(
                    Count(
                        "rollingclass__rolling_stock",
                        filter=Q(
                            rollingclass__rolling_stock__in=(
                                RollingStock.objects.get_published(
                                    request.user
                                )
                            )
                        ),
                        distinct=True,
                    )
                )
            )
            .annotate(
                num_consists=(
                    Count(
                        "consist",
                        filter=Q(
                            consist__in=(
                                Consist.objects.get_published(request.user)
                            ),
                        ),
                        distinct=True,
                    )
                )
            )
            .annotate(num_items=F("num_rollingstock") + F("num_consists"))
            .order_by("name")
        )


class Scales(GetData):
    title = "Scales"

    def get_data(self, request):
        return (
            Scale.objects.annotate(
                num_rollingstock=Count(
                    "rollingstock",
                    filter=Q(
                        rollingstock__in=RollingStock.objects.get_published(
                            request.user
                        )
                    ),
                    distinct=True,
                ),
                num_consists=Count(
                    "consist",
                    filter=Q(
                        consist__in=Consist.objects.get_published(request.user)
                    ),
                    distinct=True,
                ),
                num_catalogs=Count("catalogs", distinct=True),
            )
            .annotate(
                num_items=(
                    F("num_rollingstock")
                    + F("num_consists")
                    + F("num_catalogs")
                )
            )
            .order_by("-ratio_int", "-tracks", "scale")
        )


class Types(GetData):
    title = "Types"

    def get_data(self, request):
        return RollingStockType.objects.annotate(
            num_items=Count(
                "rollingclass__rolling_stock",
                filter=Q(
                    rollingclass__rolling_stock__in=(
                        RollingStock.objects.get_published(request.user)
                    )
                ),
            )
        ).order_by("order")


class Books(GetData):
    title = "Books"

    def get_data(self, request):
        return Book.objects.get_published(request.user).all()


class Catalogs(GetData):
    title = "Catalogs"

    def get_data(self, request):
        return Catalog.objects.get_published(request.user).all()


class Magazines(GetData):
    title = "Magazines"

    def get_data(self, request):
        return (
            Magazine.objects.get_published(request.user)
            .order_by(Lower("name"))
            .annotate(
                issues=Count(
                    "issue",
                    filter=Q(
                        issue__in=(
                            MagazineIssue.objects.get_published(request.user)
                        )
                    ),
                )
            )
        )


class GetMagazine(View):
    def get(self, request, uuid, page=1):
        try:
            magazine = Magazine.objects.get_published(request.user).get(
                uuid=uuid
            )
        except ObjectDoesNotExist:
            raise Http404
        data = list(magazine.issue.get_published(request.user).all())
        paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return render(
            request,
            "magazine.html",
            {
                "title": magazine,
                "magazine": magazine,
                "data": data,
                "matches": paginator.count,
                "page_range": page_range,
            },
        )


class GetMagazineIssue(View):
    def get(self, request, uuid, magazine, page=1):
        try:
            issue = MagazineIssue.objects.get_published(request.user).get(
                uuid=uuid,
                magazine__uuid=magazine,
            )
        except ObjectDoesNotExist:
            raise Http404
        properties = issue.property.get_public(request.user)
        documents = issue.document.get_public(request.user)
        return render(
            request,
            "bookshelf/book.html",
            {
                "title": issue,
                "data": issue,
                "documents": documents,
                "properties": properties,
            },
        )


class GetBookCatalog(View):
    def get_object(self, request, uuid, selector):
        if selector == "book":
            return Book.objects.get_published(request.user).get(uuid=uuid)
        elif selector == "catalog":
            return Catalog.objects.get_published(request.user).get(uuid=uuid)
        else:
            raise Http404

    def get(self, request, uuid, selector):
        try:
            book = self.get_object(request, uuid, selector)
        except ObjectDoesNotExist:
            raise Http404

        properties = book.property.get_public(request.user)
        documents = book.document.get_public(request.user)
        return render(
            request,
            "bookshelf/book.html",
            {
                "title": book,
                "data": book,
                "documents": documents,
                "properties": properties,
            },
        )


class GetFlatpage(View):
    def get(self, request, flatpage):
        try:
            flatpage = Flatpage.objects.get_published(request.user).get(
                path=flatpage
            )
        except ObjectDoesNotExist:
            raise Http404

        return render(
            request,
            "flatpages/flatpage.html",
            {"title": flatpage.name, "flatpage": flatpage},
        )
