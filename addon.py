# -*- coding: utf-8 -*-
# Kodi Video Plugin - IPTV JSON Example

import json
import sys
from pathlib import Path
from urllib.parse import urlencode, parse_qsl

import xbmcgui
import xbmcplugin
from xbmcaddon import Addon
from xbmcvfs import translatePath

# Caminhos principais
URL = sys.argv[0]
HANDLE = int(sys.argv[1])
ADDON_PATH = Path(translatePath(Addon().getAddonInfo('path')))
CHANNELS_PATH = ADDON_PATH / 'channels.json'

def get_url(**kwargs):
    """Cria URL de retorno do plugin"""
    return f'{URL}?{urlencode(kwargs)}'

def get_channels():
    """Lê o arquivo JSON de canais"""
    with CHANNELS_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)["channels"]

def list_channels():
    """Lista os canais na interface do Kodi"""
    xbmcplugin.setPluginCategory(HANDLE, 'Minha Lista IPTV')
    xbmcplugin.setContent(HANDLE, 'videos')

    channels = get_channels()
    for ch in channels:
        list_item = xbmcgui.ListItem(label=ch['name'])
        list_item.setArt({
            'icon': ch['thumbnail'],
            'fanart': ch.get('fanart', '')
        })
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(ch['name'])
        info_tag.setPlot(ch.get('info', ''))

        list_item.setProperty('IsPlayable', 'true')
        url = get_url(action='play', video=ch['externallink'])

        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, isFolder=False)

    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(path):
    """Reproduz o link externo"""
    play_item = xbmcgui.ListItem(offscreen=True)
    play_item.setPath(path)
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)

def router(paramstring):
    """Roteador do plugin"""
    params = dict(parse_qsl(paramstring))
    if not params:
        list_channels()
    elif params.get('action') == 'play':
        play_video(params['video'])
    else:
        raise ValueError(f'Ação inválida: {paramstring}')

if __name__ == '__main__':
    router(sys.argv[2][1:])
