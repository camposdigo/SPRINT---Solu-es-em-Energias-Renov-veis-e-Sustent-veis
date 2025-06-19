# SPRINT---Solu-es-em-Energias-Renov-veis-e-Sustent-veis
# GoodWe Smart Solar Home - API de Simulação

Este projeto consiste em um backend (API) desenvolvido em Python com o framework Flask. Ele simula o ecossistema de uma casa inteligente com geração de energia solar, armazenamento em bateria e consumo de dispositivos, oferecendo endpoints para monitorização e controlo, além de uma integração com IA para fornecer recomendações de eficiência energética.

# Funcionalidades Principais

  * **Simulação de Fluxo de Energia:** Um processo em background simula continuamente a geração de energia solar (baseada na hora do dia), o consumo dos aparelhos, o carregamento/descarregamento da bateria e a interação (compra/venda) com a rede elétrica.
  * **Gerenciamento de Dispositivos:** A API permite adicionar, remover, ligar e desligar dispositivos remotamente, recalculando o consumo total da casa em tempo real.
  * **Recomendações com IA:** Um endpoint conecta-se à API do Google Gemini para analisar o estado atual do sistema e fornecer recomendações inteligentes e amigáveis para o utilizador sobre como otimizar o consumo de energia.
  * **Frontend Integrado:** O servidor Flask também é responsável por servir a página `index.html`, que consome os dados desta API, simplificando a implementação e evitando problemas de CORS.

# Tecnologias Utilizadas

**Linguagem:** Python 3
**Framework Web:** Flask
**Biblioteca de CORS:** Flask-CORS
**Comunicação com IA:** Google Gemini API (via `requests`)
**Multithreading:** Para executar a simulação de energia sem bloquear a API.

# Estrutura do Projeto

Para que o código funcione corretamente, a estrutura de pastas e ficheiros deve ser a seguinte:

```
/GoodweSERS
|-- api.py         
|-- templates/
|   |-- index.html
```

# Guia de Instalação e Execução

Siga os passos abaixo para configurar e executar o servidor localmente.

# 1. Pré-requisitos

  * Python 3.6 ou superior
  * `pip` (gestor de pacotes do Python)

# 2. Instalação

**a. Clone o Repositório (ou crie a estrutura de pastas):**
Crie a estrutura de pastas como descrito acima и coloque o código Python no ficheiro `api.py`.

**b. Crie e Ative um Ambiente Virtual:**
É uma boa prática isolar as dependências do projeto.

```bash
 No Windows
python -m venv venv
.\venv\Scripts\activate

 No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**c. Instale as Dependências:**
Execute o comando abaixo para instalar as bibliotecas necessárias diretamente.

```bash
pip install Flask Flask-CORS requests
```

# 3. Configuração da API do Google Gemini

O projeto utiliza a API do Gemini para gerar recomendações.

# 4. Executando o Servidor

Com tudo configurado, execute o servidor Flask com o seguinte comando no seu terminal (na pasta onde o `api.py` está localizado):

```bash
python api.py
```

Você verá uma saída a indicar que o servidor está a rodar, geralmente em `http://127.0.0.1:5000/`.

  * Para aceder à interface, abra `http://127.0.0.1:5000/` no seu navegador.
  * A simulação de energia começará a rodar em background automaticamente.
  * Os logs das requisições e da simulação aparecerão no terminal.

# Endpoints da API

A interface (`index.html`) já deve interagir com estes endpoints, mas eles podem ser testados com ferramentas como Postman ou Insomnia. O endereço base é `http://127.0.0.1:5000`.

| Método | Endpoint | Descrição | Corpo da Requisição (Exemplo) |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serve a página web principal (`index.html`). | - |
| `GET` | `/api/status` | Retorna um objeto JSON com o estado atual de todo o sistema (geração, bateria, consumo, rede, etc.). | - |
| `POST` | `/api/devices` | Adiciona um novo dispositivo à simulação. O dispositivo é adicionado no estado "desligado". | `{"name": "Ar Condicionado", "consumption_kw": 1.5}` |
| `DELETE` | `/api/devices/<device_id>` | Remove um dispositivo da simulação usando o seu ID. | - |
| `POST` | `/api/devices/<device_id>/<action>` | Controla um dispositivo. `action` pode ser `turn_on` ou `turn_off`. | - |
| `GET` | `/api/recommendation` | Solicita uma recomendação de eficiência energética à IA do Google Gemini com base nos dados atuais. | - |
