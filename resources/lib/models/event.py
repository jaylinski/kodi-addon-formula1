from future import standard_library
from future.utils import PY2
standard_library.install_aliases()  # noqa: E402

from resources.lib.models.list_item import ListItem
import xbmcgui


class Event(ListItem):
    thumb = ""
    info = {}

    def to_list_item(self, addon_base):
        list_item = xbmcgui.ListItem(label=self.label)
        list_item.setArt({
            "thumb": self.thumb,
        })
        list_item.setInfo("video", {
            "plot": self.info["description"],
        })
        list_item.setProperty("isPlayable", "false")

        return None, list_item, False

    @staticmethod
    def get_description(item):
        if PY2:
            template = u"{} / {}\nStart: {}\nStatus: {}"
        else:
            template = "{} / {}\nStart: {}\nStatus: {}"

        return template.format(
            item["meetingCountryName"],
            item["meetingLocation"],
            item["meetingStartDate"],
            item["status"]
        )
