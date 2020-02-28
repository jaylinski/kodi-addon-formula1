import json
import sys
from unittest import TestCase
from unittest.mock import MagicMock, Mock
sys.modules['xbmc'] = MagicMock()
sys.modules['xbmcaddon'] = MagicMock()
sys.modules['xbmcgui'] = MagicMock()
from resources.lib.kodi.settings import Settings
from resources.lib.f1.api import Api


class ApiTestCase(TestCase):

    def setUp(self):
        self.api = Api(Settings(MagicMock()), MagicMock(), MagicMock())

    def test_get_editorial(self):
        with open("./tests/mocks/api_editorial-assemblies_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))
        self.api.api_limit = 8

        res = self.api.video_editorial()

        self.assertEqual(res.items[0].label, "Pre-season testing")
        self.assertEqual(res.items[0].uri, "F1:Topic/Testing")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/ooyala-videos/2020/2/reg0.transform/5col/image.jpg")

        self.assertEqual(res.items[4].label, "Carlos Sainz: 'Much quicker' in all areas")
        self.assertEqual(res.items[4].uri, "Q4dWo4ajE6X8J8KUzUycDSs42CKdg3oL")
        self.assertEqual(res.items[4].thumb, "https://www.formula1.com/content/dam/fom-website/ooyala-videos/2020/2/vid0.transform/5col/image.jpg")

        self.assertEqual(res.next_href, "fom-assets/videos?limit=8&offset=6")

    def test_call(self):
        with open("./tests/mocks/api_fom-assets_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.call("foo")

        self.assertEqual(res.items[0].label, "Jolyon Palmer: Why times don't matter in testing")
        self.assertEqual(res.items[0].uri, "5paGs4ajE63XiRJPxIs6yH322NPXzKBZ")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/ooyala-videos/2020/2/vid0.transform/5col/image.jpg")

    def test_paging(self):
        with open("./tests/mocks/api_fom-assets_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        self.api.api_limit = 500
        res = self.api.call("foo?query")

        self.assertEqual(res.items[0].label, "Jolyon Palmer: Why times don't matter in testing")
        self.assertEqual(res.next_href, None)

        self.api.api_limit = 10
        res = self.api.call("foo?tag=bar&limit=10&offset=0")

        self.assertEqual(res.items[0].label, "Jolyon Palmer: Why times don't matter in testing")
        self.assertEqual(res.next_href, "foo?tag=bar&limit=10&offset=10")

    def test_resolve_embed_code(self):
        with open("./tests/mocks/player_auth.json") as f:
            mock_data = f.read()

        self.api._do_player_request = Mock(return_value=json.loads(mock_data))
        self.api.video_stream = "720p"

        res = self.api.resolve_embed_code("5paGs4ajE63XiRJPxIs6yH322NPXzKBZ")

        self.assertEqual(res, "https://f1.pc.cdn.bitgravity.com/5paGs4ajE63XiRJPxIs6yH322NPXzKBZ/DOcJ-FxaFrRg4gtDEwOjIwbTowODE7WK")
