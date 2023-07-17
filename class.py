import datetime
import re
import time

from bs4 import BeautifulSoup

import instancia_scraping


class MainScraper:
    def __init__(self, site):
        self.HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
        self.site = site
        self.paginas_lidas = {}
        self.erros = 0
        self.pagina_atual = 1
        self.data_product = {}
        self.data_secao = datetime.datetime.now()
        self.inicio_secao = time.time()
        # chave e o numero da pagina a se revisitado e o valor dela e o numero de visitas na mesma
        self.paginas_a_ser_revisitadas = []
        self.log_resumo = {}

    def executar_busca(self):
        raise NotImplementedError('implemente o metodo executar busca')

    def reexecutar_nova_busca(self):
        """Funcao designada para reexecutar uma nova busca na pagina caso a mesma apresente erro
        seja por numero de produtos encontrados seja inferior ao esperado ou erro na requisicao.
        as paginas com erro seram revisitadas ate 4 veses"""
        for n_pagina in self.paginas_a_ser_revisitadas:
            for i in range(4):
                # visitando novamente a pagina com logs desativados, apenas logs dessa mesma funcao estao habilitados
                total_produtos = self.executar_busca(n_pagina, logs=False)
                pagina = f"{self.site['link'][0]}{self.site['incicador_numero_pagina']}{n_pagina}{self.site['link'][1]}"

                if total_produtos >= 100:
                    self.log(pagina, 'sucess', total_produtos,
                             f'foi obtido o numero de produtos necessarios ({i+1} visitas)', None)
                    break
                else:
                    self.log(pagina, 'warning', total_produtos,
                             f'visita n{i+1} retornou apenas {total_produtos}', None)
                    time.sleep(5)

                if i + 1 == 4:
                    self.log(pagina, 'critical', total_produtos,
                             '[error:02] 4 execucoes concluidas, todas com numero de produtos insatisfatorio', None)
                    break

    def log(self, url_pagina: str, tipo: str, total_prdutos: int, text: str, tempo: str):
        """Funcao log designada para logar todas as execucoes da secao"""
        msg = {'link': url_pagina, 'tipo': tipo,
               'total_produtos': total_prdutos, 'text_log': text, 'tempo_execucao': tempo}

        print(msg)

        try:
            self.paginas_lidas[self.pagina_atual]['logs'].append(msg)
        except KeyError:
            self.paginas_lidas[self.pagina_atual] = {'logs':
                                                     [msg]}

    def log_final(self):
        produtos = 0
        for pagina in self.data_product.values():
            for produto in pagina['produtos']:
                produtos += 1

        msg = {'loja': self.loja,
               'numero_visitas': self.pagina_atual,
               'erros': self.erros,
               'tempo_execucao': time.time() - self.inicio_secao,
               'total_produtos': produtos}

        self.log_resumo = msg
        print(self.log_resumo)

    def iniciar_busca(self):
        def template_log(texto_log, tipo_erro='error'):
            self.log(None, tipo_erro, self.total_produtos_lidos, texto_log, None)
            self.erros += 1

        while True:
            if self.erros >= 4:
                self.log(None, 'critical', self.total_produtos_lidos,
                         '[error:01]: os erros excederam o limite', None)
                self.log_final()
                break

            try:
                if self.executar_busca() == 'exc_finalizada':
                    self.reexecutar_nova_busca()
                    self.log_final()
                    break
                else:
                    self.pagina_atual += 1

            except ValueError as erro:
                template_log(f'[error:02]:{erro}')

            except PermissionError as erro:
                template_log(f'[error:02]:{erro}')

            # except Exception as erro:
            #     template_log(f'[error:03]: {erro}', 'critical')


class KabumScraper(MainScraper):
    def __init__(self, categoria):
        site = {'link': (f'https://www.kabum.com.br/{categoria}', '&page_size=100'),
                'incicador_numero_pagina': '?page_number='}
        self.loja = 'kabum'
        self.secao_scraper = instancia_scraping.nova_instancia_requests()

        super().__init__(site)

    def ler_html(self, html):
        html = html.find_all('div', class_=re.compile('productCard'))
        produtos = []
        for produto in html:
            marca = produto.find('span', class_=re.compile(
                'nameCard')).get_text()
            preco = produto.find('span', class_=re.compile(
                'priceCard')).get_text()

            if '---' in preco:
                produtos.append(None)
                break

            produtos.append((marca, preco))

        return produtos

    def executar_busca(self, n_pagina=False, logs=True):
        pagina_atual = self.pagina_atual if not n_pagina else n_pagina

        inicio_execucao = time.time()
        # verificando se o site e um dicionario, se for o desempacotamento personalizado do mesmo ira comecar
        # funcionando da seguinte forma {link principal}/{indicador_numero_de_pagina}{pagina atual}/{restante do url do site}
        if isinstance(self.site, str):
            url_pag = f'{self.link}{pagina_atual}'
        elif isinstance(self.site, dict):
            url_pag = f"{self.site['link'][0]}{self.site['incicador_numero_pagina']}{pagina_atual}{self.site['link'][1]}"

        # fazendo a coneccao com o site
        try:
            site = self.secao_scraper.get(url_pag, headers=self.HEADERS)
        except Exception as erro:
            raise ConnectionError(f'proxie_connection_error: {erro}')

        # verificando se o status code nao foi 404 ou derivados
        if site.status_code != 200:
            raise PermissionError(f'status_code_returned={site.status_code}')

        # lendo e interpretando o codigo html
        html = BeautifulSoup(site.content, 'html.parser')
        produtos = self.ler_html(html)
        tempo_execucao = time.time() - inicio_execucao

        if produtos:
            # adicionando dados obtidos do html no dicionario principal
            self.data_product[f'pagina_{pagina_atual}'] = {
                'produtos': produtos, 'data': datetime.datetime.now()}

            # verificando se o ultimo indice da lista de produtos for none, caso verdadeiro o loop finalizara e sera removido o none da lista
            if not produtos[-1]:
                produtos.pop()
                if logs:
                    self.log(url_pag, 'success', len(produtos),
                             'varredura concluida', tempo_execucao)
                return 'exc_finalizada'
        else:
            raise ValueError('noDataReceived')

        # topico PAGINA COM NUMERO DE PRODUTOS MENOR QUE A PAGINA SEGUINTE
        # pode acontecer que ao inves de 100 produtos serem enviados seja enviados 20, entao para tratar esse erro 'e feito
        # a condicao que verifica se a pagina atual teve mais produtos que a anterior, se verdadeiro o script varrera a pagina anterior novamente
        # se caso persistir o erro na mesma pagina o script continuara sua varredura nas outras paginas ignorando a pagina com problema afim de nao criar um loop
        total_produtos = len(produtos)
        if logs:
            try:
                pagina_aterior = pagina_atual - 1

                if len(self.data_product[f'pagina_{pagina_aterior}']['produtos']) < total_produtos:
                    self.log(url_pag, 'warning', total_produtos,
                             f'detectado que a pagina anterior ({pagina_aterior}), teve um total de produtos menor que a atual: error:04',
                             tempo_execucao)
                    self.paginas_a_ser_revisitadas.append(pagina_aterior)
                    return
            except KeyError:
                pass

        if logs:
            self.log(url_pag, 'success', len(produtos),
                     'varredura concluida', tempo_execucao)

        return total_produtos


scraper = KabumScraper('hardware')
scraper.iniciar_busca()
