from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


from intranet.models import HolidaysRequest


class HolidaysRequestFeed(Feed):
    title = "Holiday requests feed"
    link = "/feed/holidays/"
    description = "Updates on changes and holiday requests"
    basic_auth_realm = 'Holiday requests feed'

    @method_decorator(user_passes_test(lambda u: u.is_authenticated() and u.is_staff))
    def __call__(self, request, *args, **kwargs):
        return super(HolidaysRequestFeed, self).__call__(request, *args, **kwargs)

    def items(self):
        return HolidaysRequest.objects.order_by('-id')

    def item_title(self, item):
        return item.__unicode__()

    def item_description(self, item):
        return item.__unicode__()

    def item_link(self, obj):
        return obj.get_admin_url()
