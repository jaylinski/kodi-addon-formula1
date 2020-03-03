from future import standard_library
standard_library.install_aliases()  # noqa: E402

import base64
import requests
import urllib.parse
import xbmc

from .api_collection import ApiCollection
from resources.lib.models.editorial import Editorial
from resources.lib.models.video import Video


class Api:
    """This class uses the Formula 1 v1 API."""

    api_base_url = "https://api.formula1.com/v1/"
    api_key = "jHveMyuKQgXOCG3DN2ucX5zVmCpWNsFM"  # Extracted from public Formula 1 Android App
    api_limit = 10

    api_path_editorial = "editorial-assemblies/videos/2BiKQUC040cmuysoQsgwcK"
    api_path_videos = "fom-assets/videos"

    # Ooyala (https://help.ooyala.com/video-platform/concepts/book_ref_apis.html)
    player_api_url = "https://player.ooyala.com"
    player_api_path = "/sas/player_api/v2/authorization/embed_code/{pcode}/{embed_codes}"
    player_api_pcode = "tudTgyOkO_Oa2kec6fNFnApvZ8ig"

    video_stream = ""
    thumbnail_quality = "transform/5col/image.jpg"

    def __init__(self, settings):
        self.settings = settings

        self.api_limit = int(self.settings.get("list.size"))
        self.video_stream = self.settings.get("video.format")

    def call(self, url):
        url_components = urllib.parse.urlparse(url)
        qs_components = urllib.parse.parse_qs(url_components.query)

        if "limit" not in qs_components:
            qs_components["limit"] = [self.api_limit]

        res = self._do_api_request(url_components.path, qs_components)
        collection = self._map_json_to_collection(res)

        if res.get("total", 0) > (res.get("skip", 0) + collection.limit):
            qs_components["offset"] = [collection.offset + collection.limit]
            collection.next_href = "{}?{}".format(
                url_components.path,
                urllib.parse.urlencode(query=qs_components, doseq=True),
            )

        return collection

    def video_editorial(self):
        res = self._do_api_request(self.api_path_editorial, {})
        collection = self._map_json_to_collection(res)
        collection.next_href = self.api_path_videos + "?" + urllib.parse.urlencode({
            "limit": self.api_limit,
            "offset": collection.limit,
        })

        return collection

    def resolve_embed_code(self, embed_code):
        auth = self.player_api_path.format(pcode=self.player_api_pcode, embed_codes=embed_code)
        res = self._do_player_request(auth, {
            "domain": "http%3A%2F%2Fooyala.com",
            "supportedFormats": "mp4",
        })

        return self._get_stream_by_format(res["authorization_data"][embed_code]["streams"])

    def _do_api_request(self, path, params):
        headers = {
            "Accept-Encoding": "gzip",
            "apikey": self.api_key,
        }
        path = self.api_base_url + path

        xbmc.log(
            "plugin.video.formula1::Api() Calling %s with header %s and payload %s" %
            (path, str(headers), str(params)),
            xbmc.LOGDEBUG
        )

        return requests.get(path, headers=headers, params=params).json()

    def _do_player_request(self, path, params):
        headers = {"Accept-Encoding": "gzip"}
        path = self.player_api_url + path

        xbmc.log(
            "plugin.video.formula1::Api() Calling %s with header %s and payload %s" %
            (path, str(headers), str(params)),
            xbmc.LOGDEBUG
        )

        # Send the request.
        return requests.get(path, headers=headers, params=params).json()

    def _map_json_to_collection(self, json_obj):
        collection = ApiCollection()
        collection.items = []  # Reset list in order to resolve problems in unit tests
        collection.limit = self.api_limit
        collection.next_href = None

        if "skip" in json_obj:
            collection.offset = json_obj.get("skip")

        # Get content type
        if "contentType" in json_obj and json_obj["contentType"] == "viewAssembly":
            items = json_obj.get("regions")
        elif "videos" in json_obj:
            items = json_obj.get("videos")
        else:
            raise RuntimeError("Api JSON seems to be invalid")

        # Create collection from items
        for item in items:

            if item.get("contentType", "") == "assemblyRegionVideoListByTag":
                editorial = Editorial(id=item["tags"][0]["id"], label=item["title"])
                editorial.thumb = self._get_thumbnail(item["videos"][0])
                editorial.uri = item["tags"][0]["id"]
                collection.items.append(editorial)

            elif item.get("contentType", "") == "latestVideoList" and "videos" in item:
                collection.limit = item.get("limit", self.api_limit)
                video_collection = self._map_json_to_collection(item)
                for video in video_collection.items:
                    collection.items.append(video)

            elif "ooyalaVideoId" in item:
                video = Video(id=item["ooyalaVideoId"], label=item["caption"])
                video.thumb = self._get_thumbnail(item)
                video.uri = item["ooyalaVideoId"]
                video.info = {
                    "duration": item["ooyalaVideoDurationInSeconds"],
                }
                collection.items.append(video)

        return collection

    def _get_thumbnail(self, item):
        return "{}.{}".format(item["thumbnail"]["url"], self.thumbnail_quality)

    def _get_stream_by_format(self, streams):
        video_format = self.settings.VIDEO_FORMAT[self.video_stream]
        video_format = video_format.split(":")
        video_quality = int(video_format[1])

        for stream in streams:
            if stream.get("height") == video_quality:
                return base64.b64decode(stream["url"]["data"]).decode('ascii')

        # Fallback (if no matching resolution was found
        return base64.b64decode(streams[0]["url"]["data"]).decode('ascii')
