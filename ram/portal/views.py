import operator
from functools import reduce

from django.views import View
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from portal.utils import get_site_conf
from roster.models import RollingStock
from consist.models import Consist
from metadata.models import Company, Scale


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
        page_range = paginator.get_elided_page_range(rolling_stock.number)

        return render(
            request,
            "home.html",
            {"rolling_stock": rolling_stock, "page_range": page_range},
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
        elif _filter == "scale":
            query = Q(scale__scale__iexact=search)
        elif _filter == "tag":
            query = Q(tags__slug__iexact=search)
        else:
            raise Http404
        rolling_stock = RollingStock.objects.filter(query).order_by(
            *order_by_fields()
        )
        matches = len(rolling_stock)

        paginator = Paginator(rolling_stock, site_conf.items_per_page)
        rolling_stock = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(rolling_stock.number)

        return rolling_stock, matches, page_range

    def get(self, request, search, _filter="search", page=1):
        rolling_stock, matches, page_range = self.run_search(
            request, search, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "search": search,
                "filter": _filter,
                "matches": matches,
                "rolling_stock": rolling_stock,
                "page_range": page_range,
            },
        )

    def post(self, request, _filter="search", page=1):
        search = request.POST.get("search")
        if not search:
            raise Http404
        rolling_stock, matches, page_range = self.run_search(
            request, search, _filter, page
        )

        return render(
            request,
            "search.html",
            {
                "search": search,
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

        return render(
            request,
            "page.html",
            {
                "rolling_stock": rolling_stock,
                "class_properties": class_properties,
                "rolling_stock_properties": rolling_stock_properties,
            },
        )


class Consists(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        consist = Consist.objects.all()

        paginator = Paginator(consist, site_conf.items_per_page)
        consist = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(consist.number)

        return render(
            request,
            "consists.html",
            {"consist": consist, "page_range": page_range},
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
        page_range = paginator.get_elided_page_range(rolling_stock.number)

        return render(
            request,
            "consist.html",
            {
                "consist": consist,
                "rolling_stock": rolling_stock,
                "page_range": page_range,
            },
        )


class Companies(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        company = Company.objects.all()

        paginator = Paginator(company, site_conf.items_per_page)
        company = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(company.number)

        return render(
            request,
            "companies.html",
            {"company": company, "page_range": page_range},
        )


class Scales(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        scale = Scale.objects.all()

        paginator = Paginator(scale, site_conf.items_per_page)
        scale = paginator.get_page(page)
        page_range = paginator.get_elided_page_range(scale.number)

        return render(
            request,
            "scales.html",
            {"scale": scale, "page_range": page_range},
        )
