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

        self.assertEqual(res.items[0].label, "Pre-season testing")
        self.assertEqual(res.items[0].uri, "F1:Topic/Testing")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/ooyala-videos/2020/2/reg0.transform/5col/image.jpg")

        self.assertEqual(res.items[4].label, "Carlos Sainz: 'Much quicker' in all areas")
        self.assertEqual(res.items[4].uri, "Q4dWo4ajE6X8J8KUzUycDSs42CKdg3oL")
        self.assertEqual(res.items[4].thumb, "https://www.formula1.com/content/dam/fom-website/ooyala-videos/2020/2/vid0.transform/5col/image.jpg")

        self.assertEqual(res.next_href, "fom-assets/videos?limit=8&offset=6")

    def test_get_drivers(self):
        with open("./tests/mocks/api_editorial-driverlisting_listing.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "1 - Lewis Hamilton - 88 PTS")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png")

        self.assertEqual(res.items[1].label, "2 - Valtteri Bottas - 58 PTS")
        self.assertEqual(res.items[1].thumb, "https://www.formula1.com/content/dam/fom-website/drivers/V/VALBOT01_Valtteri_Bottas/valbot01.png")


    def test_get_constructors(self):
        with open("./tests/mocks/api_editorial-constructorlisting_listing.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "1 - Mercedes - 146 PTS")
        self.assertEqual(res.items[0].thumb, "https://www.formula1.com/content/dam/fom-website/teams/2020/mercedes-half.png")

        self.assertEqual(res.items[1].label, "2 - Red Bull Racing - 78 PTS")
        self.assertEqual(res.items[1].thumb, "https://www.formula1.com/content/dam/fom-website/teams/2020/red-bull-racing-half.png")

    def test_get_race_results(self):
        with open("./tests/mocks/api_fom-results_raceresults.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.standings("api_path")

        self.assertEqual(res.items[0].label, "Formula 1 Rolex Grosser Preis Von Österreich 2020")

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

        self.api.api_limit = 3
        res = self.api.call("foo?tag=bar&limit=3&offset=0")

        self.assertEqual(res.items[0].label, "Jolyon Palmer: Why times don't matter in testing")
        self.assertEqual(res.limit, 3)
        self.assertEqual(res.offset, 0)
        self.assertEqual(res.next_href, "foo?tag=bar&limit=3&offset=3")

        with open("./tests/mocks/api_fom-assets_videos_page_2.json") as f:
            mock_data = f.read()

        self.api._do_api_request = Mock(return_value=json.loads(mock_data))

        res = self.api.call("foo?tag=bar&limit=3&offset=3")

        self.assertEqual(res.items[0].label, "page 2 title")
        self.assertEqual(res.limit, 3)
        self.assertEqual(res.offset, 3)
        self.assertEqual(res.next_href, "foo?tag=bar&limit=3&offset=6")

    def test_resolve_embed_code(self):
        with open("./tests/mocks/player_auth_mp4.json") as f:
            mock_data = f.read()

        self.api._do_player_request = Mock(return_value=json.loads(mock_data))
        self.api.video_stream = "720p"

        res = self.api.resolve_embed_code("5paGs4ajE63XiRJPxIs6yH322NPXzKBZ")

        self.assertEqual(res, "https://f1.pc.cdn.bitgravity.com/5paGs4ajE63XiRJPxIs6yH322NPXzKBZ/DOcJ-FxaFrRg4gtDEwOjIwbTowODE7WK")

        with open("./tests/mocks/player_auth_hls.json") as f:
            mock_data = f.read()

        self.api._do_player_request = Mock(return_value=json.loads(mock_data))
        self.api.video_stream = "HLS (Adaptive)"

        res = self.api.resolve_embed_code("5paGs4ajE63XiRJPxIs6yH322NPXzKBZ")

        self.assertEqual(res, "https://player.ooyala.com/hls/player/iphone/5paGs4ajE63XiRJPxIs6yH322NPXzKBZ.m3u8?ssl=true&secure_ios_token=VTU3citINzFZVG9qYTMvc2VUVUpMRU1FcjBMWHZCMFgrZTkvQkNxQ1NjelBaNVptZmp0NVBmUlJ6Y0hQCmM4cytGQ1BsMmNpS1ZtU2FPRmQ1c3lhWlVRPT0K")
