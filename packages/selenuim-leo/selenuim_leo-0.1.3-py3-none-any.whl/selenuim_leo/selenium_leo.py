# import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions, Chrome
from auto_download_undetected_chromedriver import download_undetected_chromedriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from time import sleep
from random import uniform
from os import path, remove
from  pyperclip import copy, paste


class SeleniumLeo:
    def __init__(self):
        self.navegador_iniciado = False

    def Tempo(self, a=0.5, b=1.0):
        tempo_aleatorio = round(uniform(a, b), 1)
        sleep(tempo_aleatorio)

    def Aguardar(self, local):
        # -> lista for vazia -> que o elemento não existe ainda
        cont = 0
        while len(self.navegador.find_elements(By.XPATH, local)) == 0:
            sleep(0.3)
            print(f'tentando localizar ({cont})')
            cont+=1
            
        self.Tempo(0.2,0.4)

    def Clicar2(self, local):
        self.Aguardar(local)
        self.navegador.find_element(By.XPATH, local).click()

    def Inserir(self, xpatch, arquivo):
        self.Aguardar(xpatch)
        self.navegador.find_element(By.XPATH, xpatch).send_keys(arquivo)

    def Enter(self, xpatch):
        self.Aguardar(xpatch)
        self.navegador.find_element(By.XPATH, xpatch).send_keys(Keys.ENTER)

    def Ctrl_letra(self, xpatch, letra):
        self.Aguardar(xpatch)
        self.navegador.find_element(
            By.XPATH, xpatch).send_keys(Keys.CONTROL, letra)
    
    def Tab(self, xpatch):
        self.Aguardar(xpatch)
        self.navegador.find_element(By.XPATH, xpatch).send_keys(Keys.TAB)
        
    def Colar(self, xpatch):
        self.Aguardar(xpatch)
        self.navegador.find_element(
            By.XPATH, xpatch).send_keys(Keys.CONTROL + "v")

    def Juntar(self, a, b):
        return path.join(a, b)

    def DefinirTamenhoPosicao(self, largura_monitor=2560, altura_monitor=1080):
        # Definir o tamanho da janela pela metade da largura do monitor
        # Substitua pelo tamanho do seu monitor em largura
        # Substitua pelo tamanho do seu monitor em altura
        # tamanho_janela = f"--window-size={largura_monitor//8},{altura_monitor}"
        self.navegador.set_window_size(largura_monitor//2, altura_monitor-58)
        self.navegador.set_window_position(largura_monitor//2, 25)

    @property
    def Iniciar(self):
        if not self.navegador_iniciado:

            options = ChromeOptions()
            options.add_argument(
                '--user-data-dir=C:\\Users\leani\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1')

            # options.add_argument(tamanho_janela)
            # options.add_argument(f"--window-position={largura_monitor//2},0")

            def DeletarArquivo(caminho_arquivo):
                if path.exists(caminho_arquivo):
                    remove(caminho_arquivo)

            if not path.exists(caminho := 'C:\\Users\\leani\\TabelaMandados\\selenium\\chromedriver.exe'):
                folder_path = r"C:\Users\leani\TabelaMandados\selenium"
                chromedriver_path = download_undetected_chromedriver(
                    folder_path, undetected=True, arm=False, force_update=True)
                self.navegador = Chrome(options=options,
                                        driver_executable_path=chromedriver_path,
                                        headless=False, use_subprocess=True
                                        )
            else:
                try:
                    self.navegador = Chrome(options=options,
                                            headless=False, use_subprocess=True
                                            )
                except:
                    DeletarArquivo(caminho)
                    folder_path = r"C:\Users\leani\TabelaMandados\selenium"
                    chromedriver_path = download_undetected_chromedriver(
                        folder_path, undetected=True, arm=False, force_update=True)
                    self.navegador = Chrome(options=options,
                                            driver_executable_path=chromedriver_path,
                                            headless=False, use_subprocess=True
                                            )
            self.navegador_iniciado = True
        else:
            print(f'O navegador já está iniciado')

        self.DefinirTamenhoPosicao()

    @property
    def FecharNavegador(self):
        if self.navegador_iniciado:
            # self.navegador.quit()
            self.navegador.close()
            self.navegador_iniciado = False


    def Abrir_site(self, link):
        if not self.navegador_iniciado:
            self.Iniciar
        if self.navegador_iniciado:
            self.navegador.get(link)