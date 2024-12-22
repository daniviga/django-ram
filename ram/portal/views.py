import base64
import operator
from itertools import chain
from functools import reduce
from urllib.parse import unquote

from django.views import View
from django.http import Http404, HttpResponseBadRequest
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from portal.utils import get_site_conf
from portal.models import Flatpage
from roster.models import RollingStock
from consist.models import Consist
from bookshelf.models import Book, Catalog
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
    return items_per_page


def get_order_by_field():
    try:
        order_by = get_site_conf().items_ordering
    except (OperationalError, ProgrammingError):
        order_by = "type"

    fields = [
        "rolling_class__type",
        "rolling_class__company",
        "rolling_class__identifier",
        "road_number_int",
    ]

    if order_by == "type":
        return (fields[0], fields[1], fields[2], fields[3])
    elif order_by == "company":
        return (fields[1], fields[0], fields[2], fields[3])
    elif order_by == "identifier":
        return (fields[2], fields[0], fields[1], fields[3])


class Render404(View):
    def get(self, request, exception):
        return render(request, "base.html", {"title": "404 page not found"})


class GetData(View):
    title = "Home"
    template = "roster.html"
    item_type = "rolling_stock"
    filter = Q()  # empty filter by default

    def get_data(self, request):
        return (
            RollingStock.objects.get_published(request.user)
            .order_by(*get_order_by_field())
            .filter(self.filter)
        )

    def get(self, request, page=1):
        data = []
        for item in self.get_data(request):
            data.append({"type": self.item_type, "item": item})

        paginator = Paginator(data, 3)
        # paginator = Paginator(data, get_items_per_page())
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=1, on_ends=1
        )

        return render(
            request,
            self.template,
            {
                "title": self.title,
                "type": self.item_type,
                "data": data,
                "matches": paginator.count,
                "page_range": page_range,
            },
        )


class GetRoster(GetData):
    title = "Roster"
    item_type = "rolling_stock"

    def get_data(self, request):
        return RollingStock.objects.get_published(request.user).order_by(
            *get_order_by_field()
        )


class SearchObjects(View):
    def run_search(self, request, search, _filter, page=1):
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
        data = []
        rolling_stock = (
            RollingStock.objects.get_published(request.user)
            .filter(query)
            .distinct()
            .order_by(*get_order_by_field())
        )
        for item in rolling_stock:
            data.append({"type": "rolling_stock", "item": item})

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
            for item in consists:
                data.append({"type": "consist", "item": item})
            books = (
                Book.objects.get_published(request.user)
                .filter(title__icontains=search)
                .distinct()
            )
            catalogs = (
                Catalog.objects.get_published(request.user)
                .filter(manufacturer__name__icontains=search)
                .distinct()
            )
            for item in list(chain(books, catalogs)):
                data.append({"type": "book", "item": item})

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
        manufacturer = get_object_or_404(
            Manufacturer, slug__iexact=manufacturer
        )

        if search != "all":
            rolling_stock = get_list_or_404(
                RollingStock.objects.get_published(request.user).order_by(
                    *get_order_by_field()
                ),
                Q(
                    Q(manufacturer=manufacturer)
                    & Q(item_number_slug__exact=search)
                ),
            )
            title = "{0}: {1}".format(
                manufacturer,
                # all returned records must have the same `item_number``;
                # just pick it up the first result, otherwise `search`
                rolling_stock[0].item_number if rolling_stock else search,
            )
        else:
            rolling_stock = (
                RollingStock.objects.get_published(request.user)
                .order_by(*get_order_by_field())
                .filter(
                    Q(manufacturer=manufacturer)
                    | Q(rolling_class__manufacturer=manufacturer)
                )
            )
            title = "Manufacturer: {0}".format(manufacturer)

        data = []
        for item in rolling_stock:
            data.append({"type": "rolling_stock", "item": item})

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

        rolling_stock = (
            RollingStock.objects.get_published(request.user)
            .filter(query)
            .distinct()
            .order_by(*get_order_by_field())
        )

        data = []
        for item in rolling_stock:
            data.append({"type": "rolling_stock", "item": item})

        try:  # Execute only if query_2nd is defined
            consists = (
                Consist.objects.get_published(request.user)
                .filter(query_2nd)
                .distinct()
            )
            for item in consists:
                data.append({"type": "consist", "item": item})
            if _filter == "tag":  # Books can be filtered only by tag
                books = (
                    Book.objects.get_published(request.user)
                    .filter(query_2nd)
                    .distinct()
                )
                for item in books:
                    data.append({"type": "book", "item": item})
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

        consists = [
            {"type": "consist", "item": c}
            for c in Consist.objects.get_published(request.user).filter(
                consist_item__rolling_stock=rolling_stock
            )
        ]  # A dict with "item" is required by the consists card

        set = [
            {"type": "set", "item": s}
            for s in RollingStock.objects.get_published(request.user)
            .filter(
                Q(
                    Q(item_number__exact=rolling_stock.item_number)
                    & Q(set=True)
                )
            )
            .order_by(*get_order_by_field())
        ]

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
                "set": set,
                "consists": consists,
            },
        )


class Consists(GetData):
    title = "Consists"
    item_type = "consist"

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
        data = [
            {
                "type": "rolling_stock",
                "item": RollingStock.objects.get_published(request.user).get(
                    uuid=r.rolling_stock_id
                ),
            }
            for r in consist.consist_item.all()
        ]

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
                "page_range": page_range,
            },
        )


class Manufacturers(GetData):
    title = "Manufacturers"
    item_type = "manufacturer"

    def get_data(self, request):
        return Manufacturer.objects.filter(self.filter)

    # overload get method to filter by category
    def get(self, request, category, page=1):
        if category not in ("real", "model"):
            raise Http404
        self.filter = Q(category=category)

        return super().get(request, page)


class Companies(GetData):
    title = "Companies"
    item_type = "company"

    def get_data(self, request):
        return Company.objects.all()


class Scales(GetData):
    title = "Scales"
    item_type = "scale"
    queryset = Scale.objects.all()

    def get_data(self, request):
        return Scale.objects.all()


class Types(GetData):
    title = "Types"
    item_type = "rolling_stock_type"

    def get_data(self, request):
        return RollingStockType.objects.all()


class Books(GetData):
    title = "Books"
    item_type = "book"

    def get_data(self, request):
        return Book.objects.get_published(request.user).all()


class Catalogs(GetData):
    title = "Catalogs"
    item_type = "catalog"

    def get_data(self, request):
        return Catalog.objects.get_published(request.user).all()


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

        book_properties = book.property.get_public(request.user)
        return render(
            request,
            "bookshelf/book.html",
            {
                "title": book,
                "book_properties": book_properties,
                "book": book,
                "type": selector
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
