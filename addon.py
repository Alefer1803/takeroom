import json
import urllib.request
import xbmcgui
import xbmcplugin
import sys

url = sys.argv[1]
handle = int(sys.argv[1])
json_url = "https://github.com/SeuUsuario/SeuRepo/raw/master/menu.json"

response = urllib.request.urlopen(json_url)
data = json.load(response)

for item in data['channels']:
    li = xbmcgui.ListItem(label=item['name'])
    li.setArt({'thumb': item['thumbnail'], 'fanart': item['fanart']})
    xbmcplugin.addDirectoryItem(handle=handle, url=item['externallink'], listitem=li, isFolder=True)

xbmcplugin.endOfDirectory(handle)
