import sys
import json
import urllib.request
import xbmcgui
import xbmcplugin

handle = int(sys.argv[1])

# Pega o URL clicado, se não existir, usa o menu principal
if len(sys.argv) > 2:
    json_url = sys.argv[2][1:]
else:
    json_url = "https://raw.githubusercontent.com/Alefer1803/takeroom/refs/heads/main/channels.json"

# Lê o JSON
response = urllib.request.urlopen(json_url)
data = json.load(response)

for item in data['channels']:
    li = xbmcgui.ListItem(label=item['name'])
    li.setArt({'thumb': item.get('thumbnail', ''), 'fanart': item.get('fanart', '')})
    url = f"{sys.argv[0]}?{item['externallink']}"
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

xbmcplugin.endOfDirectory(handle)
