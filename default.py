import sys
import urllib.parse
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import urllib.request
import urllib.error
import traceback # Importa para depuração

# --- CONFIGURAÇÃO DE URL PRINCIPAL (RAIZ) ---
# A URL onde o script buscará o arquivo JSON do menu principal
MAIN_MENU_URL = 'https://raw.githubusercontent.com/Alefer1803/takeroom/refs/heads/main/menuprincipal'
# --------------------------------------------

# Objetos globais do Kodi
ADDON = xbmcaddon.Addon()
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# --- FUNÇÕES AUXILIARES ---

def build_url(query):
    """Cria uma URL interna para o nosso próprio script (essencial para o Kodi)."""
    return BASE_URL + '?' + urllib.parse.urlencode(query)

def fetch_json_url(url):
    """Faz a requisição HTTP e retorna o conteúdo como um objeto Python (JSON)."""
    try:
        # Define um cabeçalho User-Agent para evitar bloqueios do GitHub
        req = urllib.request.Request(url, headers={'User-Agent': 'Kodi Addon'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            # Tenta decodificar o JSON
            return json.loads(data)
    except urllib.error.URLError as e:
        # Erro de conexão ou URL
        xbmcgui.Dialog().ok("ERRO DE CONEXÃO", f"Não foi possível carregar o menu de:\n{url}\nMotivo: {e.reason}")
        return None
    except json.JSONDecodeError:
        # Erro de formato JSON
        xbmcgui.Dialog().ok("ERRO DE JSON", "O arquivo de menu do GitHub não está em um formato JSON válido.")
        return None
    except Exception as e:
        # Outros erros (útil para depuração)
        xbmcgui.Dialog().ok("ERRO DESCONHECIDO", f"Ocorreu um erro ao carregar o menu: {e}\n{traceback.format_exc()}")
        return None

def add_directory_item(name, url, is_folder=True, is_playable=False):
    """Adiciona um item ao diretório do Kodi."""
    list_item = xbmcgui.ListItem(label=name)
    
    if is_playable:
        list_item.setProperty('IsPlayable', 'true')
        
    xbmcplugin.addDirectoryItem(
        handle=ADDON_HANDLE,
        url=url,
        listitem=list_item,
        isFolder=is_folder
    )

# --- FUNÇÕES PRINCIPAIS DE NAVEGAÇÃO ---

def main_menu():
    """
    Carrega o menu principal a partir da URL do GitHub (MAIN_MENU_URL) e cria os itens.
    """
    xbmcplugin.setContent(ADDON_HANDLE, 'movies') # Define o tipo de conteúdo na raiz

    # 1. Busca e processa o JSON do link raiz
    menu_data = fetch_json_url(MAIN_MENU_URL)

    if not menu_data:
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return

    # 2. Cria os itens do menu com base no JSON
    for item in menu_data:
        name = item.get('name', 'Item Sem Nome')
        mode = item.get('mode') 
        url_conteudo = item.get('url_conteudo') 
        is_folder = item.get('is_folder', True) 

        if mode == 'list_content' and url_conteudo:
            # Item que leva a uma sub-lista (outra URL do GitHub)
            internal_url = build_url({
                'mode': 'list_content',
                'category': name,
                'github_url': url_conteudo # URL da sub-lista no GitHub
            })
            add_directory_item(name, internal_url, is_folder=is_folder)
        
        elif mode == 'play' and url_conteudo:
             # Item que leva à reprodução direta de uma mídia
            internal_url = build_url({
                'mode': 'play_media',
                'media_url': url_conteudo
            })
            add_directory_item(name, internal_url, is_folder=False, is_playable=True)
            
        else:
            add_directory_item(f"[ERRO] {name}: Item Inválido", "", is_folder=False)
            
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_content(category, github_url):
    """
    Carrega o conteúdo de um sub-menu (como 'FILMES') a partir de outra URL do GitHub.
    """
    xbmcplugin.setContent(ADDON_HANDLE, 'videos')
    xbmcplugin.setPluginCategory(ADDON_HANDLE, f'Conteúdo: {category}')
    
    # 1. Busca e processa o JSON da sub-lista
    content_data = fetch_json_url(github_url)

    if not content_data:
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
        
    # 2. Cria os itens de conteúdo (podem ser vídeos ou mais sub-listas)
    for item in content_data:
        name = item.get('name', 'Item Sem Nome')
        mode = item.get('mode') 
        url_conteudo = item.get('url_conteudo') 
        is_folder = item.get('is_folder', True)

        if mode == 'list_content' and url_conteudo:
            # Item é uma sub-pasta dentro do menu atual
            internal_url = build_url({
                'mode': 'list_content',
                'category': name,
                'github_url': url_conteudo
            })
            add_directory_item(name, internal_url, is_folder=True)

        elif mode == 'play' and url_conteudo:
            # Item é um vídeo para reprodução final
            internal_url = build_url({
                'mode': 'play_media',
                'media_url': url_conteudo
            })
            add_directory_item(name, internal_url, is_folder=False, is_playable=True)
        
        else:
            add_directory_item(f"[ERRO] {name}: Item Inválido", "", is_folder=False)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def play_media(media_url):
    """
    Tenta reproduzir uma URL de mídia.
    """
    list_item = xbmcgui.ListItem(path=media_url)
    list_item.setProperty('IsPlayable', 'true')

    # Resolve o item para o player do Kodi
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, succeeded=True, listitem=list_item)


# --- ROTEADOR ---

def router(url_params):
    """
    Direciona a execução para a função correta com base no parâmetro 'mode'.
    """
    # url_params é um dicionário onde todos os valores são listas (parse_qsl retorna listas)
    mode = url_params.get('mode', [None])[0]

    if mode is None:
        # Início do addon (sem parâmetros)
        main_menu()
    elif mode == 'list_content':
        # Próxima lista de conteúdo do GitHub
        category = url_params.get('category', [''])[0]
        github_url = url_params.get('github_url', [''])[0]
        list_content(category, github_url)
    elif mode == 'play_media':
        # Reprodução de mídia final
        media_url = url_params.get('media_url', [''])[0]
        play_media(media_url)
    
    # A função endOfDirectory é chamada no final de main_menu/list_content

if __name__ == '__main__':
    # Analisa os parâmetros da URL passada pelo Kodi (sys.argv[2])
    try:
        url_params = dict(urllib.parse.parse_qsl(sys.argv[2].replace('?', '')))
    except:
        url_params = {}

    router(url_params)
