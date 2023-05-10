from collections import OrderedDict
from typing import Union

from django.urls import re_path
from rest_framework.routers import Route, DynamicRoute, DefaultRouter, \
    SimpleRouter, APIRootView
from rest_framework.urlpatterns import format_suffix_patterns


class MyDefaultRouter:
    include_root_view = True
    include_format_suffixes = True
    root_view_name = 'api-root'
    APIRootView = APIRootView

    def __init__(self):
        self._urls = []
        self.routers = []

    def register(self, prefix, viewset, basename=None):
        router = SimpleRouter()
        router.register(prefix, viewset, basename)
        self.routers.append(router)

        if self._urls:
            del self._urls

    def include_router(self, router: Union[DefaultRouter, SimpleRouter]):
        if router not in self.routers:
            self.routers.append(router)

            if self._urls:
                del self._urls

    def get_api_root_view(self):
        api_root_dict = OrderedDict()
        for router in self.routers:
            list_name = router.routes[0].name
            for prefix, viewset, basename in router.registry:
                api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)

    def get_urls(self):
        urls = []

        if not self.routers:
            raise Exception("Not added routers")

        for router in self.routers:
            urls.extend(self._get_urls(router))

        if self.include_root_view:
            view = self.get_api_root_view()
            root_url = re_path(r'^$', view, name=self.root_view_name)
            urls.append(root_url)

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        return urls

    def _get_urls(self, router):
        ret = []

        for prefix, viewset, basename in router.registry:
            lookup = router.get_lookup_regex(viewset)
            routes = router.get_routes(viewset)

            for route in routes:
                mapping = router.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=router.trailing_slash
                )

                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'basename': basename,
                    'detail': route.detail,
                })

                view = viewset.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)
                ret.append(re_path(regex, view, name=name))

        return ret

    @property
    def urls(self):
        if not self._urls:
            self._urls = self.get_urls()
        return self._urls


class ChatRouter(DefaultRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'put': 'update',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]
