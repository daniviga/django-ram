from django.apps import apps


def get_site_conf():
    SiteConfiguration = apps.get_model("portal", "SiteConfiguration")
    return SiteConfiguration.get_solo()
