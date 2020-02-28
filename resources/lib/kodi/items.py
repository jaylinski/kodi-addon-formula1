from future import standard_library
standard_library.install_aliases()  # noqa: E402

import urllib.parse
import xbmcgui


class Items:
    def __init__(self, addon, addon_base):
        self.addon = addon
        self.addon_base = addon_base

    def root(self):
        items = []

        # Videos
        list_item = xbmcgui.ListItem(label=self.addon.getLocalizedString(30101))
        url = self.addon_base + "/?" + urllib.parse.urlencode({
            "action": "editorial",
        })
        items.append((url, list_item, True))

        # Settings
        list_item = xbmcgui.ListItem(label=self.addon.getLocalizedString(30109))
        url = self.addon_base + "/?action=settings"
        items.append((url, list_item, False))

        return items

    def from_collection(self, collection):
        items = []

        for item in collection.items:
            items.append(item.to_list_item(self.addon_base))

        if collection.next_href:
            next_item = xbmcgui.ListItem(label=self.addon.getLocalizedString(30901))
            url = self.addon_base + "/?" + urllib.parse.urlencode({
                "action": "call",
                "call": collection.next_href,
            })
            items.append((url, next_item, True))

        return items
