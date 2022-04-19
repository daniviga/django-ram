import operator
from functools import reduce

from django.views import View
from django.http import Http404
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from portal.utils import get_site_conf
from roster.models import RollingStock


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
    def run_search(self, request, search, page=1):
        # if not hasattr(RollingStock, _filter):
        #     raise Http404
        site_conf = get_site_conf()
        # query = {
        #     _filter: _value
        # }
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
        rolling_stock = RollingStock.objects.filter(query)
        paginator = Paginator(rolling_stock, site_conf.items_per_page)

        try:
            rolling_stock = paginator.page(page)
        except PageNotAnInteger:
            rolling_stock = paginator.page(1)
        except EmptyPage:
            rolling_stock = paginator.page(paginator.num_pages)

        return rolling_stock

    def get(self, request, search, page=1):
        rolling_stock = self.run_search(request, search, page)

        return render(
            request,
            "search.html",
            {"search": search, "rolling_stock": rolling_stock},
        )

    def post(self, request, page=1):
        search = request.POST.get("search")
        if not search:
            raise Http404
        rolling_stock = self.run_search(request, search, page)

        return render(
            request,
            "search.html",
            {"search": search, "rolling_stock": rolling_stock},
        )


class GetRollingStock(View):
    def get(self, request, uuid):
        rolling_stock = RollingStock.objects.get(uuid=uuid)

        return render(
            request,
            "page.html",
            {
                "rolling_stock": rolling_stock,
            },
        )
