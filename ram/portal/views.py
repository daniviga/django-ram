import operator
from functools import reduce
from urllib.parse import quote_plus, unquote_plus

from django.views import View
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger

from portal.utils import get_site_conf
from portal.models import Flatpage
from roster.models import RollingStock
from consist.models import Consist
from metadata.models import Company, Manufacturer, Scale


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


class GetHome(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        rolling_stock = RollingStock.objects.order_by(*order_by_fields())

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            rolling_stock.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "home.html",
            {
                "title": "Home",
                "rolling_stock": rolling_stock,
                "page_range": page_range,
            },
        )


class GetHomeFiltered(View):
    def run_search(self, request, search, _filter, page=1):
        site_conf = get_site_conf()
        if _filter == "search":
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
        elif _filter == "company":
            query = Q(
                Q(rolling_class__company__name__icontains=search)
                | Q(rolling_class__company__extended_name__icontains=search)
            )
        elif _filter == "manufacturer":
            query = Q(
                Q(manufacturer__name__iexact=search)
                | Q(rolling_class__manufacturer__name__icontains=search)
            )
        elif _filter == "scale":
            query = Q(scale__scale__iexact=search)
        elif _filter == "tag":
            query = Q(tags__slug__iexact=search)
        else:
            raise Http404
        rolling_stock = (
            RollingStock.objects.filter(query)
            .distinct()
            .order_by(*order_by_fields())
        )
        matches = len(rolling_stock)

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            rolling_stock.number, on_each_side=2, on_ends=1
        )

        return rolling_stock, matches, page_range

    def get(self, request, search, _filter="search", page=1):
        search_unsafe = unquote_plus(search)  # expected to be encoded
        rolling_stock, matches, page_range = self.run_search(
            request, search_unsafe, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "title": "{0}: {1}".format(
                    _filter.capitalize(), search_unsafe),
                "search": search,
                "search_unsafe": search_unsafe,
                "filter": _filter,
                "matches": matches,
                "rolling_stock": rolling_stock,
                "page_range": page_range,
            },
        )

    def post(self, request, _filter="search", page=1):
        search = request.POST.get("search")
        # search = quote_plus(request.POST.get("search"), safe="&")
        # search_unsafe = unquote_plus(search)
        if not search:
            raise Http404
        rolling_stock, matches, page_range = self.run_search(
            request, search, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "title": "{0}: {1}".format(_filter.capitalize(), search),
                "search": search,
                # "search_unsafe": search_unsafe,
                "filter": _filter,
                "matches": matches,
                "rolling_stock": rolling_stock,
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


class Consists(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        consist = Consist.objects.all()

        paginator = Paginator(consist, site_conf.items_per_page)
        consist = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            consist.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "consists.html",
            {
                "title": "Consists",
                "consist": consist,
                "page_range": page_range,
            },
        )


class GetConsist(View):
    def get(self, request, uuid, page=1):
        site_conf = get_site_conf()
        try:
            consist = Consist.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404
        rolling_stock = consist.consist_item.all()

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
                "rolling_stock": rolling_stock,
                "page_range": page_range,
            },
        )


class Manufacturers(View):
    def get(self, request, category, page=1):
        site_conf = get_site_conf()
        if category not in ("real", "model"):
            raise Http404
        manufacturers = Manufacturer.objects.filter(category=category)

        paginator = Paginator(manufacturers, site_conf.items_per_page)
        manufacturers = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            manufacturers.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "manufacturers.html",
            {
                "title": "Manufacturers",
                "category": category,
                "manufacturers": manufacturers,
                "page_range": page_range,
            },
        )


class Companies(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        company = Company.objects.all()

        paginator = Paginator(company, site_conf.items_per_page)
        company = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            company.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "companies.html",
            {
                "title": "Companies",
                "company": company,
                "page_range": page_range,
            },
        )


class Scales(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        scale = Scale.objects.all()

        paginator = Paginator(scale, site_conf.items_per_page)
        scale = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(
            scale.number, on_each_side=2, on_ends=1
        )

        return render(
            request,
            "scales.html",
            {"title": "Scales", "scale": scale, "page_range": page_range},
        )


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
