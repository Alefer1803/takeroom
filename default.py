# -*- coding: utf-8 -*-
"""
Take Room - plugin robusto para carregar menu remoto via XML.
Coloque este arquivo como default.py no seu addon.
"""

import sys
import xbmc, xbmcgui, xbmcplugin
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import socket

HANDLE = int(sys.argv[1])

# URL do menu remoto
URL_MENU = "https://raw.githubusercontent.com/Alefer1803/takeroom/refs/heads/main/menuprincipal"
# timeout em segundos para conexões HTTP
HTTP_TIMEOUT = 15

def log(msg, level=xbmc.LOGINFO):
    xbmc.log(f"[plugin.video.takeroom] {msg}", level)

def fetch_text(url):
    """Busca texto remoto com user-agent, timeout e tratamento de erros."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            data = resp.read()
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1')
    except urllib.error.HTTPError as e:
        log(f"HTTPError ao buscar {url}: {e.code} {e.reason}", xbmc.LOGERROR)
        raise
    except urllib.error.URLError as e:
        log(f"URLError ao buscar {url}: {e}", xbmc.LOGERROR)
        raise
    except socket.timeout:
        log(f"Timeout ao buscar {url}", xbmc.LOGERROR)
        raise
    except Exception as e:
        log(f"Erro desconhecido ao buscar {url}: {e}", xbmc.LOGERROR)
        raise

def safe_parse_xml(text):
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        log(f"ParseError XML: {e}", xbmc.LOGERROR)
        raise

def show_error(title, message):
    xbmcgui.Dialog().ok(title, message)

# --- Menu local de fallback (caso o remoto falhe) ---
def menu_local():
    xbmcplugin.setPluginCategory(HANDLE, "Take Room")
    xbmcplugin.setContent(HANDLE, "videos")
    # adicionar Filmes (aponta para remoto de filmes.xml)
    adicionar_item("🎬 Filmes", f"{sys.argv[0]}?action=listar&url=https://raw.githubusercontent.com/Alefer1803/takeroom/main/filmes.xml", True)
    adicionar_item("🔁 Teste (local)", "", True)
    xbmcplugin.endOfDirectory(HANDLE)

def adicionar_item(nome, url, isFolder=True, thumb=None):
    li = xbmcgui.ListItem(label=nome)
    if thumb:
        try: li.setArt({'thumb': thumb, 'icon': thumb})
        except: pass
    xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=isFolder)

# --- Carrega e monta o menu remoto ---
def listar_menu_remoto():
    xbmcplugin.setPluginCategory(HANDLE, "Take Room")
    xbmcplugin.setContent(HANDLE, "videos")
    try:
        text = fetch_text(URL_MENU)
        root = safe_parse_xml(text)
        items = root.findall('.//item')
        if not items:
            # tenta buscar como canais/channel se seu menu for estruturado assim
            items = root.findall('.//channel')
        if not items:
            log("XML remoto carregado mas não contém <item> nem <channel>.", xbmc.LOGWARNING)
            show_error("Take Room", "XML carregado mas sem itens válidos. Usando menu local.")
            menu_local()
