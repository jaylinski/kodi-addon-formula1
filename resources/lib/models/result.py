from future import standard_library
standard_library.install_aliases()  # noqa: E402

from resources.lib.models.list_item import ListItem
import xbmcgui


class Result(ListItem):
    thumb = ""
    info = {}

    def to_list_item(self, addon_base):
        list_item = xbmcgui.ListItem(label=self.label)
        list_item.setArt({
            "thumb": self.thumb,
        })
        list_item.setProperty("isPlayable", "false")

        return None, list_item, False
