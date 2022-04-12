from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from portal.utils import get_site_conf
from roster.models import RollingStock, RollingStockImage


class GetHome(View):
    def get(self, request, page=1):
        site_conf = get_site_conf()
        rolling_stock = RollingStock.objects.all()
        thumbnails = RollingStockImage.objects.filter(is_thumbnail=True)
        paginator = Paginator(rolling_stock, site_conf.items_per_page)

        try:
            rolling_stock = paginator.page(page)
        except PageNotAnInteger:
            rolling_stock = paginator.page(1)
        except EmptyPage:
            rolling_stock = paginator.page(paginator.num_pages)

        return render(request, 'home.html', {
            'rolling_stock': rolling_stock,
            'thumbnails': thumbnails
        })


class GetRollingStock(View):
    def get(self, request, uuid):
        rolling_stock = RollingStock.objects.get(uuid=uuid)

        return render(request, 'page.html', {
            'rolling_stock': rolling_stock,
        })
