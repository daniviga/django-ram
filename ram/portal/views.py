import base64
import operator
from functools import reduce
from urllib.parse import unquote

from django.views import View
from django.http import Http404, HttpResponseBadRequest
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from portal.utils import get_site_conf
from portal.models import Flatpage
from roster.models import RollingStock
from consist.models import Consist
from metadata.models import Company, Manufacturer, Scale, RollingStockType, Tag


def order_by_fields():
    order_by = get_site_conf().items_ordering
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


class GetData(View):
    def __init__(self):
        self.title = "Home"
        self.template = "home.html"
        self.data = RollingStock.objects.order_by(*order_by_fields())

    def get(self, request, page=1):
        site_conf = get_site_conf()

        paginator = Paginator(self.data, site_conf.items_per_page)
        data = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            data.number, on_each_side=2, on_ends=1
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


class GetRoster(GetData):
    def __init__(self):
        self.title = "Rolling stock"
        self.template = "roster.html"
        self.data = RollingStock.objects.order_by(*order_by_fields())


class SearchRoster(View):
    def run_search(self, request, search, _filter, page=1):
        site_conf = get_site_conf()
        if _filter is None:
            query = reduce(
                operator.or_,
                (
                    Q(
                        Q(rolling_class__identifier__icontains=s)
                        | Q(rolling_class__description__icontains=s)
                        | Q(rolling_class__type__type__icontains=s)
                        | Q(road_number__icontains=s)
                        | Q(sku=s)
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

        rolling_stock = (
            RollingStock.objects.filter(query)
            .distinct()
            .order_by(*order_by_fields())
        )
        matches = rolling_stock.count()

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            rolling_stock.number, on_each_side=2, on_ends=1
        )

        return rolling_stock, matches, page_range

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
            encoded_search = base64.b64encode(
                search.encode()).decode()
        _filter, keyword = self.split_search(search)
        rolling_stock, matches, page_range = self.run_search(
            request, keyword, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "title": "Search: \"{}\"".format(search),
                "search": search,
                "encoded_search": encoded_search,
                "matches": matches,
                "data": rolling_stock,
                "page_range": page_range,
            },
        )

    def post(self, request, page=1):
        search = request.POST.get("search")
        return self.get(request, search, page)


class GetRosterFiltered(View):
    def run_filter(self, request, search, _filter, page=1):
        site_conf = get_site_conf()
        if _filter == "type":
            type_ = " ".join(search.split()[:-1])
            category = search.split()[-1]
            try:
                title = (
                    RollingStockType.objects.filter(type__iexact=type_)
                    .get(category__iexact=category)
                )
            except ObjectDoesNotExist:
                raise Http404
            query = Q(
                Q(rolling_class__type__type__iexact=type_)
                & Q(rolling_class__type__category__iexact=category)
            )
        elif _filter == "company":
            title = get_object_or_404(Company, name__iexact=search)
            query = Q(rolling_class__company__name__iexact=search)
        elif _filter == "manufacturer":
            title = get_object_or_404(Manufacturer, name__iexact=search)
            query = Q(
                Q(rolling_class__manufacturer__name__iexact=search)
                | Q(manufacturer__name__iexact=search)
            )
        elif _filter == "scale":
            title = get_object_or_404(Scale, scale__iexact=search)
            query = Q(scale__scale__iexact=search)
        elif _filter == "tag":
            title = get_object_or_404(Tag, slug=search)
            query = Q(tags__slug__iexact=search)
        else:
            raise Http404

        rolling_stock = (
            RollingStock.objects.filter(query)
            .distinct()
            .order_by(*order_by_fields())
        )
        matches = rolling_stock.count()

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            rolling_stock.number, on_each_side=2, on_ends=1
        )

        return rolling_stock, title, matches, page_range

    def get(self, request, search, _filter, page=1):
        data, title, matches, page_range = self.run_filter(
            request, unquote(search), _filter, page
        )

        return render(
            request,
            "filter.html",
            {
                "title": "{0}: {1}".format(
                    _filter.capitalize(), title),
                "search": search,
                "filter": _filter,
                "matches": matches,
                "data": data,
                "page_range": page_range,
            },
        )


class GetRollingStock(View):
    def get(self, request, uuid):
        try:
            rolling_stock = RollingStock.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404

        class_properties = (
            rolling_stock.rolling_class.property.all()
            if request.user.is_authenticated
            else rolling_stock.rolling_class.property.filter(
                property__private=False
            )
        )
        rolling_stock_properties = (
            rolling_stock.property.all()
            if request.user.is_authenticated
            else rolling_stock.property.filter(property__private=False)
        )

        rolling_stock_journal = (
            rolling_stock.journal.all()
            if request.user.is_authenticated
            else rolling_stock.journal.filter(private=False)
        )

        return render(
            request,
            "rollingstock.html",
            {
                "title": rolling_stock,
                "rolling_stock": rolling_stock,
                "class_properties": class_properties,
                "rolling_stock_properties": rolling_stock_properties,
                "rolling_stock_journal": rolling_stock_journal,
            },
        )


class Consists(GetData):
    def __init__(self):
        self.title = "Consists"
        self.template = "consists.html"
        self.data = Consist.objects.all()


class GetConsist(View):
    def get(self, request, uuid, page=1):
        site_conf = get_site_conf()
        try:
            consist = Consist.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404
        rolling_stock = [
            RollingStock.objects.get(uuid=r.rolling_stock_id) for r in
            consist.consist_item.all()
        ]

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            rolling_stock.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "consist.html",
            {
                "title": consist,
                "consist": consist,
                "data": rolling_stock,
                "page_range": page_range,
            },
        )


class Manufacturers(GetData):
    def __init__(self):
        self.title = "Manufacturers"
        self.template = "manufacturers.html"
        self.data = None  # Set via method get

    # overload get method to filter by category
    def get(self, request, category, page=1):
        if category not in ("real", "model"):
            raise Http404
        self.data = Manufacturer.objects.filter(category=category)
        return super().get(request, page)


class Companies(GetData):
    def __init__(self):
        self.title = "Companies"
        self.template = "companies.html"
        self.data = Company.objects.all()


class Scales(GetData):
    def __init__(self):
        self.title = "Scales"
        self.template = "scales.html"
        self.data = Scale.objects.all()


class Types(GetData):
    def __init__(self):
        self.title = "Types"
        self.template = "types.html"
        self.data = RollingStockType.objects.all()


class GetFlatpage(View):
    def get(self, request, flatpage):
        try:
            flatpage = Flatpage.objects.get(
                Q(Q(path=flatpage) & Q(published=True))
            )
        except ObjectDoesNotExist:
            raise Http404

        return render(
            request,
            "flatpage.html",
            {"title": flatpage.name, "flatpage": flatpage},
        )
