# -*- coding: utf-8 -*-
import sys
import urllib.request
import urllib.parse
import xbmcaddon
import xbmcgui
import xbmcplugin
import xml.etree.ElementTree as ET

handle = int(sys.argv[1])

# URL do menu principal remoto
URL_MENU = "https://raw.githubusercontent.com/Alefer1803/takeroom/main/menuprincipal.xml"

def listar_menu():
    try:
        response = urllib.request.urlopen(URL_MENU)
        xml_data = response.read().decode('utf-8')
        root = ET.fromstring(xml_data)

        for item in root.findall('item'):
            name = item.findtext('name', 'Sem nome')
            link = item.findtext('link', '')
            thumbnail = item.findtext('thumbnail', '')

            list_item = xbmcgui.ListItem(label=name)
            list_item.setArt({'thumb': thumbnail, 'icon': thumbnail})
            url = f"{sys.argv[0]}?action=listar&url={urllib.parse.quote(link)}"
            xbmcplugin.addDirectoryItem(handle, url, list_item, isFolder=True)

        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        xbmcgui.Dialog().notification("Erro Menu", str(e), xbmcgui.NOTIFICATION_ERROR)

def listar_canais(url_xml):
    try:
        response = urllib.request.urlopen(url_xml)
        xml_data = response.read().decode('utf-8')
        root = ET.fromstring(xml_data)

        for channel in root.findall('channel'):
            name = channel.findtext('name', 'Sem nome')
            link = channel.findtext('externallink', '')
            thumbnail = channel.findtext('thumbnail', '')
            fanart = channel.findtext('fanart', '')
            info = channel.findtext('info', '')

            list_item = xbmcgui.ListItem(label=name)
            list_item.setArt({'thumb': thumbnail, 'icon': thumbnail, 'fanart': fanart})
            list_item.setInfo('video', {'title': name, 'plot': info})

            url = f"{sys.argv[0]}?action=abrir_lista&url={urllib.parse.quote(link)}"
            xbmcplugin.addDirectoryItem(handle, url, list_item, isFolder=True)

        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        xbmcgui.Dialog().notification("Erro Lista", str(e), xbmcgui.NOTIFICATION_ERROR)

def abrir_lista(url):
    xbmc.executebuiltin(f"PlayMedia({url})")

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')
    if action == 'listar':
        listar_canais(params.get('url'))
    elif action == 'abrir_lista':
        abrir_lista(params.get('url'))
    else:
        listar_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])
