from future import standard_library
from future.utils import PY2
standard_library.install_aliases()  # noqa: E402

from resources.lib.f1.api import Api
from resources.lib.kodi.cache import Cache
from resources.lib.kodi.items import Items
from resources.lib.kodi.settings import Settings
from resources.lib.kodi.vfs import VFS
from resources.routes import *
import os
import sys
import urllib.parse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo("id")
addon_base = "plugin://" + addon_id
addon_profile_path = xbmc.translatePath(addon.getAddonInfo('profile'))
if PY2:
    addon_profile_path = addon_profile_path.decode('utf-8')
vfs = VFS(addon_profile_path)
vfs_cache = VFS(os.path.join(addon_profile_path, "cache/"))
settings = Settings(addon)
cache = Cache(settings, vfs_cache)
api = Api(settings, vfs, cache)
listItems = Items(addon, addon_base)


def run():
    url = urllib.parse.urlparse(sys.argv[0])
    path = url.path
    handle = int(sys.argv[1])
    args = urllib.parse.parse_qs(sys.argv[2][1:])
    xbmcplugin.setContent(handle, 'videos')

    if path == PATH_ROOT:
        action = args.get("action", None)
        if action is None:
            items = listItems.root()
            xbmcplugin.addDirectoryItems(handle, items, len(items))
            xbmcplugin.endOfDirectory(handle)
        elif "call" in action:
            collection = listItems.from_collection(api.call(args.get("call")[0]))
            xbmcplugin.addDirectoryItems(handle, collection, len(collection))
            xbmcplugin.endOfDirectory(handle)
        elif "editorial" in action:
            collection = listItems.from_collection(api.video_editorial())
            xbmcplugin.addDirectoryItems(handle, collection, len(collection))
            xbmcplugin.endOfDirectory(handle)
        elif "settings" in action:
            addon.openSettings()
        else:
            xbmc.log("Invalid root action", xbmc.LOGERROR)

    elif path == PATH_PLAY:
        embed_code = args.get("embed_code", [None])[0]

        if embed_code:
            resolved_url = api.resolve_embed_code(embed_code)
            item = xbmcgui.ListItem(path=resolved_url)
            xbmcplugin.setResolvedUrl(handle, succeeded=True, listitem=item)
        else:
            xbmc.log("Invalid play param", xbmc.LOGERROR)

    elif path == PATH_SETTINGS_CACHE_CLEAR:
        vfs_cache.destroy()
        dialog = xbmcgui.Dialog()
        dialog.ok('Formula 1', addon.getLocalizedString(30401))

    else:
        xbmc.log("Path not found", xbmc.LOGERROR)
