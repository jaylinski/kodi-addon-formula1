import json
import sys
from unittest import TestCase
from unittest.mock import MagicMock, Mock
sys.modules["xbmc"] = MagicMock()
sys.modules["xbmcaddon"] = MagicMock()
sys.modules["xbmcgui"] = MagicMock()
from resources.lib.kodi.settings import Settings
from resources.lib.f1.api import Api


class ApiTestCase(TestCase):

    def setUp(self):
        self.api = Api(Settings(MagicMock()))

    def test_get_editorial(self):
        with open("./tests/mocks/api_editorial-assemblies_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))
        self.api.api_limit = 8

        res = self.api.video_editorial()

        self.assertEqual(res.items[0].label, "Must-see")
        self.assertEqual(res.items[0].uri, "F1:Topic/Must See")
        self.assertEqual(res.items[0].thumb, "https://d2n9h2wits23hf.cloudfront.net/image/v1/static/6057949432001/ba77f5dc-5216-4f8a-8af1-f0c5904c59ac/df63d8b3-5445-40b8-a6ae-cea539a279a9/658x370/match/image.jpg")

        self.assertEqual(res.items[4].label, "Polesitter Charles Leclerc")
        self.assertEqual(res.items[4].info["description"], "Polesitter Charles Leclerc is ...")
        self.assertEqual(res.items[4].uri, "1700475935169308929")
        self.assertEqual(res.items[4].thumb, "https://d2n9h2wits23hf.cloudfront.net/image/v1/static/6057949432001/270fdcdb-4275-4a3a-82d0-5d532efd7057/21e8cf3e-334f-4ef3-90b8-adad686dcba3/658x370/match/image.jpg")

        self.assertEqual(res.next_href, "/v1/video-assets/videos?limit=8&offset=6")

    def test_get_drivers(self):
        with open("./tests/mocks/api_editorial-driverlisting_listing.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "1 - Oscar Piastri - 324 PTS")
        self.assertEqual(res.items[0].thumb, "https://media.formula1.com/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png")

        self.assertEqual(res.items[1].label, "2 - Lando Norris - 299 PTS")
        self.assertEqual(res.items[1].thumb, "https://media.formula1.com/drivers/L/LANNOR01_Lando_Norris/lannor01.png")

        self.assertEqual(res.items[2].label, "3 - Max Verstappen - 255 PTS")
        self.assertEqual(res.items[2].thumb, "https://media.formula1.com/M/MAXVER01_Max_Verstappen/maxver01.png")

        self.assertEqual(res.items[5].label, "? - Nikita Mazepin - 0 PTS")

    def test_get_constructors(self):
        with open("./tests/mocks/api_editorial-constructorlisting_listing.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "1 - Mercedes - 146 PTS")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/teams/2020/mercedes-half.png")

        self.assertEqual(res.items[1].label, "2 - Red Bull Racing - 78 PTS")
        self.assertEqual(res.items[1].thumb, "https://www.formula1.com/content/dam/fom-website/teams/2020/red-bull-racing-half.png")

    def test_get_events(self):
        with open("./tests/mocks/api_editorial-eventlisting_events.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "Formula 1 Rolex Grosser Preis Von Österreich 2020")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/2018-redesign-assets/Flags%2016x9/austria-flag.png")

        # Check if only "racing" events are returned
        self.assertEqual(len(res.items), 12)

    def test_get_race_results_detail(self):
        with open("./tests/mocks/api_fom-results_race.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.call("api_path")

        self.assertEqual(res.items[0].label, "1 - HAM - 25 PTS - 1:31:45.279")
        self.assertEqual(res.items[1].label, "2 - VER - 18 PTS - +24.177s")
        self.assertEqual(res.items[19].label, "DNF - LEC - 0 PTS - 55:31.636")

    def test_call(self):
        with open("./tests/mocks/api_video-assets_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.call("foo")

        self.assertEqual(res.items[0].label, "Video Caption 1")
        self.assertEqual(res.items[0].uri, "1700475935169308929")
        self.assertEqual(res.items[0].thumb, "https://d2n9h2wits23hf.cloudfront.net/image/v1/static/658x370/match/image.jpg")

    def test_paging(self):
        with open("./tests/mocks/api_video-assets_videos.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        self.api.api_limit = 500
        res = self.api.call("foo?query")

        self.assertEqual(res.items[0].label, "Video Caption 1")
        self.assertEqual(res.next_href, None)

        self.api.api_limit = 3
        res = self.api.call("foo?tag=bar&limit=3&offset=0")

        self.assertEqual(res.items[0].label, "Video Caption 1")
        self.assertEqual(res.limit, 3)
        self.assertEqual(res.offset, 0)
        self.assertEqual(res.next_href, "foo?tag=bar&limit=3&offset=3")

        with open("./tests/mocks/api_video-assets_videos_page_2.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.call("foo?tag=bar&limit=3&offset=3")

        self.assertEqual(res.items[0].label, "page 2 title")
        self.assertEqual(res.limit, 3)
        self.assertEqual(res.offset, 3)
        self.assertEqual(res.next_href, "foo?tag=bar&limit=3&offset=6")

    def test_resolve_video_id(self):
        with open("./tests/mocks/player_video.json") as f:
            mock_data = f.read()

        # Progressive
        self.api._do_player_request = Mock(return_value=json.loads(mock_data))
        self.api.video_stream = "720p"

        res = self.api.resolve_video_id("123")

        self.assertEqual(res, "http://d2n9h2wits23hf.cloudfront.net/media/v1/pmp4/static/clear/6057949432001/main.mp4")

        # HLS
        self.api._do_player_request = Mock(return_value=json.loads(mock_data))
        self.api.video_stream = "HLS (Adaptive)"

        res = self.api.resolve_video_id("123")

        self.assertEqual(res, "http://manifest.prod.boltdns.net/manifest/v1/hls/v4/clear/6057949432001/10s/master.m3u8")
