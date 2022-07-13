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


class GetHome(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        rolling_stock = RollingStock.objects.all()
        paginator = Paginator(rolling_stock, site_conf.items_per_page)

        try:
            rolling_stock = paginator.page(page)
        except PageNotAnInteger:
            rolling_stock = paginator.page(1)
        except EmptyPage:
            rolling_stock = paginator.page(paginator.num_pages)

        return render(request, "home.html", {"rolling_stock": rolling_stock})


class GetHomeFiltered(View):
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
            query = Q(scale__scale__icontains=search)
        else:
            raise Http404
        rolling_stock = RollingStock.objects.filter(query)
        matches = len(rolling_stock)
        paginator = Paginator(rolling_stock, site_conf.items_per_page)

        try:
            rolling_stock = paginator.page(page)
        except PageNotAnInteger:
            rolling_stock = paginator.page(1)
        except EmptyPage:
            rolling_stock = paginator.page(paginator.num_pages)

        return rolling_stock, matches

    def get(self, request, search, _filter=None, page=1):
        rolling_stock, matches = self.run_search(
            request, search, _filter, page)

        return render(
            request,
            "search.html",
            {
                "search": search,
                "filter": _filter,
                "matches": matches,
                "rolling_stock": rolling_stock,
            },
        )

    def post(self, request, _filter=None, page=1):
        search = request.POST.get("search")
        if not search:
            raise Http404
        rolling_stock, matches = self.run_search(
            request, search, _filter, page)

        return render(
            request,
            "search.html",
            {
                "search": search,
                "filter": _filter,
                "matches": matches,
                "rolling_stock": rolling_stock,
            },
        )


class GetRollingStock(View):
    def get(self, request, uuid):
        try:
            rolling_stock = RollingStock.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404

        class_properties = (
            rolling_stock.rolling_class.property.all() if
            request.user.is_authenticated else
            rolling_stock.rolling_class.property.filter(
                property__private=False)
        )
        rolling_stock_properties = (
            rolling_stock.property.all() if
            request.user.is_authenticated else
            rolling_stock.property.filter(property__private=False)
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

        try:
            consist = paginator.page(page)
        except PageNotAnInteger:
            consist = paginator.page(1)
        except EmptyPage:
            consist = paginator.page(paginator.num_pages)

        return render(request, "consists.html", {"consist": consist})


class GetConsist(View):
    def get(self, request, uuid, page=1):
        site_conf = get_site_conf()
        try:
            consist = Consist.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise Http404
        rolling_stock = consist.consist_item.all()
        paginator = Paginator(rolling_stock, site_conf.items_per_page)

        try:
            rolling_stock = paginator.page(page)
        except PageNotAnInteger:
            rolling_stock = paginator.page(1)
        except EmptyPage:
            rolling_stock = paginator.page(paginator.num_pages)

        return render(
            request,
            "consist.html",
            {"consist": consist, "rolling_stock": rolling_stock},
        )
