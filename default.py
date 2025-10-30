import sys
import os
import urllib.parse
# Biblioteca para requisições HTTP (URL)
import urllib.request
from xbmc import executebuiltin
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent
# Biblioteca para trabalhar com XML em memória
import xml.etree.ElementTree as ET

# --- Variáveis Iniciais ---
ADDON_NAME = "Take Room" 
BASE_URL = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
# URL do arquivo XML remoto
REMOTE_MENU_URL = 'https://raw.githubusercontent.com/Alefer1803/takeroom/refs/heads/main/menu-principal'


# --- Funções de Ajuda ---

def build_url(query):
    """Cria uma URL Kodi formatada."""
    return BASE_URL + '?' + urllib.parse.urlencode(query)

# --- Funções de Menu ---

def get_remote_xml(url):
    """Faz a requisição para a URL e retorna o conteúdo XML."""
    try:
        # Abre a URL e lê o conteúdo
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('utf-8')
        
        # Parseia o conteúdo XML lido da string
        root = ET.fromstring(xml_data)
        return root

    except urllib.error.URLError as e:
        print(f"ERRO: Falha ao acessar a URL {url}: {e.reason}")
        return None
    except ET.ParseError as e:
        print(f"ERRO: Falha ao parsear o XML: {e}")
        return None
    except Exception as e:
        print(f"ERRO Inesperado: {e}")
        return None

def main_menu():
    """Baixa o XML remoto e constrói o Menu Principal."""
    root = get_remote_xml(REMOTE_MENU_URL)
    
    if root is not None:
        # Itera sobre cada item do menu no XML
        for item in root.findall('item'):
            try:
                title = item.find('title').text
                mode = item.find('mode').text
                
                # Assume 'folder' é 'true' se o texto for 'true', caso contrário é 'false' (ou None)
                is_folder_str = item.find('folder').text.lower() if item.find('folder') is not None and item.find('folder').text is not None else 'true'
                is_folder = is_folder_str == 'true'

                # Cria o item no Kodi
                add_item(title, {'mode': mode}, is_folder=is_folder)
            
            except Exception as e:
                print(f"Aviso: Item XML mal-formatado ignorado: {e}")

    else:
        # Caso o XML não possa ser carregado
        add_item('⚠️ ERRO: Falha ao carregar o Menu Remoto', {}, is_folder=False)
        
    endOfDirectory(ADDON_HANDLE)


def filmes_categorias_menu():
    """Menu de Categorias de Filmes"""
    categorias = ['LANÇAMENTOS', 'AÇÃO', 'FICÇÃO', 'AVENTURA', 'TERROR', 'COMÉDIA', 'FANTASIA', 'NACIONAL']
    
    for categoria in categorias:
        add_item(categoria, {'mode': 'filmes_lista', 'categoria': categoria}, is_folder=True)

    endOfDirectory(ADDON_HANDLE)


def series_lista_menu():
    """Lista de Séries (Exemplo)"""
    series = [
        {'title': 'A Casa do Dragão', 'id': 'casa_dragao'},
        {'title': 'The Last of Us', 'id': 'last_of_us'},
        {'title': 'The Mandalorian', 'id': 'mandalorian'}
    ]

    for serie in series:
        add_item(serie['title'], {'mode': 'series_episodios', 'serie_id': serie['id']}, is_folder=True)
        
    setContent(ADDON_HANDLE, 'tvshows') 
    endOfDirectory(ADDON_HANDLE)

def series_episodios_menu(serie_id):
    """Lista de Episódios de uma Série (Exemplo)"""
    episodios = [
        {'title': f'S01E01 - Pilot', 'link': 'link_real_do_episodio_1.mp4'},
        {'title': f'S01E02 - The Next One', 'link': 'link_real_do_episodio_2.mp4'}
    ]
    
    for ep in episodios:
        add_item(ep['title'], {'mode': 'play_video', 'url': ep['link']}, is_folder=False, is_playable=True)

    setContent(ADDON_HANDLE, 'episodes')
    endOfDirectory(ADDON_HANDLE)

# --- Função de Adicionar Item (Auxiliar) ---

def add_item(name, url_params, is_folder=False, is_playable=False):
    """Adiciona um item à lista atual do Kodi."""
    url = build_url(url_params)
    li = ListItem(name)
    
    if is_playable:
        li.setInfo('video', {'title': name})
        li.setProperty('IsPlayable', 'true')
        addDirectoryItem(ADDON_HANDLE, url, li, is_folder=False)
    else:
        addDirectoryItem(ADDON_HANDLE, url, li, is_folder=is_folder)

# --- Função de Execução de Vídeo ---

def play_video(url):
    """Inicia a reprodução do vídeo."""
    play_item = ListItem(path=url)
    executebuiltin('PlayMedia(%s)' % url) 


# --- Roteador Principal ---
def router(paramstring):
    """Lida com as chamadas de URL do Kodi e direciona para a função correta."""
    params = dict(urllib.parse.parse_qsl(paramstring))
    mode = params.get('mode')

    if mode is None:
        main_menu() # Agora carrega o menu do XML Remoto
    elif mode == 'filmes_categorias':
        filmes_categorias_menu()
    elif mode == 'filmes_lista':
        # Esta é a próxima etapa para puxar filmes de uma URL remota
        add_item('Exemplo de Filme de ' + params.get('categoria'), {'mode': 'play_video', 'url': 'link_exemplo_filme.mp4'}, is_folder=False, is_playable=True)
        endOfDirectory(ADDON_HANDLE)
    elif mode == 'series_lista':
        series_lista_menu()
    elif mode == 'series_episodios':
        series_episodios_menu(params.get('serie_id'))
    elif mode == 'animes_lista':
        add_item('Lista de Animes - Em Desenvolvimento', {}, is_folder=False)
        endOfDirectory(ADDON_HANDLE)
    elif mode == 'tv_ao_vivo':
        play_video('link_real_da_tv_ao_vivo.m3u8')
    elif mode == 'play_video':
        play_video(params.get('url'))

# --- Início do Addon ---
if __name__ == '__main__':
    router(sys.argv[2][1:])