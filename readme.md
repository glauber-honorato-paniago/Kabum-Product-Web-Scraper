# Kabum Product WebScraper

# Visão Geral
Esse bot em Python, o Kabum Product WebScraper, é uma poderosa ferramenta de web scraping projetada especificamente para a loja online Kabum. Ele realiza uma varredura abrangente em qualquer categoria de produto desejada, coletando todos os dados relevantes dos produtos, como nome e preço. O scraper inclui um robusto sistema de log e oferece saída de dados facilmente integrável para integração em bancos de dados.

# Recursos
**Varredura de Categoria:** O bot é capaz de escanear toda a categoria de produtos desejada na Kabum, garantindo acesso a todos os produtos dentro dessa categoria.

**Detalhes dos Produtos:** O scraper coleta informações essenciais dos produtos, incluindo nome e preço, permitindo que você obtenha rapidamente as informações necessárias.

**Sistema de Logs:** O bot possui um sistema sofisticado de log, acompanhando cada execução e fornecendo insights valiosos sobre o processo de scraping.

**Resiliência e Tratamento de Erros:** Em caso de erros durante o processo de scraping, o bot é projetado para reexecutar a busca em páginas problemáticas para garantir a completude dos dados.

**Integração Flexível:** O scraper gera os dados coletados em um formato facilmente adaptável para integração em um banco de dados ou para processamento adicional.

# Observações
Modifique a variável categoria na linha scraper = KabumScraper('hardware') do arquivo main.py para a categoria desejada no site da Kabum.

O bot realizará o processo de web scraping, e você encontrará os dados dos produtos nos logs e na saída do programa. Você pode facilmente integrar esses dados em um **banco de dados** de sua preferência ou utilizá-los para análises adicionais.

# Contribuições e Problemas
Contribuições e feedback são bem-vindos! Se você encontrar problemas ou tiver ideias para melhorar esse web scraper, por favor, crie um problema (issue) no repositório do GitHub. Se desejar contribuir para o projeto, sinta-se à vontade para enviar um pull request.