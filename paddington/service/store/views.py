import requests
from bs4 import BeautifulSoup
from rest_framework import views
from rest_framework.response import Response

from service.store.models import AppRelease
from service.utils import cache_return_wrapper


class AppVersionAPI(views.APIView):

    def get_itunes_version(self, bundle_id):
        url = "https://itunes.apple.com/lookup?bundleId={}".format(bundle_id)
        try:
            content = requests.get(url).json()
            version = content['results'][0]['version']
        except Exception:
            return None, 500

        return version, 200

    def get_play_version(self, bundle_id):
        url = "https://play.google.com/store/apps/details?id={}".format(bundle_id)
        try:
            content = requests.get(url, timeout=5).content
        except Exception:
            return None, 500

        soup = BeautifulSoup(content, 'html.parser')
        div = soup.body.find('div', text="Current Version")
        version = div.parent.find('span').text
        return version, 200

    @cache_return_wrapper(except_self=True)
    def get_version(self, store, bundle_id):
        if store == 'play':
            return self.get_play_version(bundle_id)
        elif store == 'itunes':
            return self.get_itunes_version(bundle_id)
        return "", 400

    def get(self, request, *args, **kwargs):
        store = request.query_params.get('store')
        bundle_id = request.query_params.get('id')
        version, status = self.get_version(store, bundle_id)
        resp = {
            "store": store,
            "bundle_id": bundle_id,
            "version": version
        }
        return Response(resp, status=status)


class AppReleaseAPI(views.APIView):

    @cache_return_wrapper(except_self=True)
    def get_app_release(self, store):
        app_release = AppRelease.objects.filter(stores__icontains=store).order_by('-id').first()

        resp = {}
        if app_release is not None:
            resp = {
                'id': app_release.id,
                'version': app_release.version,
                'release_note': app_release.release_note,
                'stores': app_release.stores,
            }

        return resp

    def get(self, request, *args, **kwargs):
        store = request.query_params.get('store')
        resp = self.get_app_release(store)
        return Response(resp)


version = AppVersionAPI.as_view()
release = AppReleaseAPI.as_view()
