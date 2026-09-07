# Review Sense

API para extrair conteúdo textual de páginas web, gerar resumos estruturados com IA e armazenar os resultados em cache local. O projeto resolve o problema de transformar artigos ou páginas longas em uma resposta objetiva com título, resumo, principais insights e tempo estimado de leitura, evitando chamadas repetidas ao modelo para URLs já processadas.

## Funcionalidades

- Extração assíncrona de conteúdo a partir de uma URL informada.
- Limpeza básica do HTML, removendo elementos como `script`, `style`, `nav`, `header`, `aside` e `form`.
- Priorização de conteúdo dentro das tags `article`, `main` ou, como fallback, `body`.
- Geração de resumo com Google Gemini, retornando uma estrutura validada com título, resumo, insights principais e tempo estimado de leitura.
- Cache de resumos em SQLite para evitar reprocessamento da mesma URL.
- Tradução de resumos já armazenados em cache para um idioma-alvo.
- API HTTP com FastAPI e documentação automática via OpenAPI/Swagger.
- Inicialização automática das tabelas do banco durante o ciclo de vida da aplicação.
- Configuração de CORS para `http://localhost:3000` e `https://delimadev.vercel.app`.
- Containerização com Docker.

## Tecnologias Utilizadas

### Linguagem

- **Python 3.14+**: linguagem principal da aplicação, definida em `pyproject.toml` e na imagem Docker.

### Frameworks e bibliotecas

- **FastAPI**: framework usado para expor os endpoints HTTP, validar payloads e gerar documentação automática.
- **Uvicorn**: servidor ASGI utilizado para executar a aplicação FastAPI.
- **Pydantic**: validação dos modelos de entrada e saída da API.
- **pydantic-settings**: leitura de variáveis de ambiente a partir do arquivo `.env`.
- **SQLAlchemy Async**: camada de acesso ao banco com sessões assíncronas e definição declarativa do modelo persistido.
- **aiosqlite**: driver assíncrono usado pelo SQLAlchemy para comunicação com SQLite.
- **httpx**: cliente HTTP assíncrono usado para buscar o conteúdo das URLs.
- **Beautiful Soup 4**: parser HTML usado para remover elementos não relevantes e extrair texto legível.
- **google-genai**: SDK usado para chamar o modelo Gemini e gerar resumos em JSON estruturado.
- **deep-translator**: biblioteca usada para traduzir resumos já salvos no cache.

### Banco de dados

- **SQLite**: persistência local dos resumos na tabela `saved_summaries`.
- O caminho configurado no código é `sqlite+aiosqlite:////data/database.db`.

### Ferramentas

- **uv**: gerenciador de dependências e ambiente Python, indicado pela presença de `uv.lock` e pelo uso no Dockerfile.
- **Docker**: empacotamento da aplicação em imagem baseada em Python Alpine.
- **Ruff**: configuração presente em `pyproject.toml` para lint e formatação, embora não esteja listado como dependência do projeto.

### Serviços externos

- **Google Gemini**: serviço externo usado para geração dos resumos.
- **Google Translate via deep-translator**: usado pela rota de tradução.

### Gerenciador de pacotes

- **uv**: gerencia instalação e lockfile das dependências.

## Arquitetura

O projeto segue uma organização simples em camadas:

- `src/main.py`: ponto de entrada da aplicação FastAPI, configuração de CORS, ciclo de vida da aplicação e inclusão das rotas.
- `src/api/endpoints.py`: definição dos contratos HTTP e orquestração dos fluxos de resumo e tradução.
- `src/services/scraper.py`: serviço responsável por buscar a página e extrair texto limpo do HTML.
- `src/services/gemini.py`: serviço responsável por montar o prompt, chamar o Gemini e validar a resposta estruturada.
- `src/services/translator.py`: serviço auxiliar para tradução assíncrona usando executor de threads.
- `src/database.py`: configuração do engine assíncrono, sessão e base declarativa do SQLAlchemy.
- `src/models.py`: modelo persistido `SavedSummary`.
- `src/config/settings.py`: leitura de configurações via variáveis de ambiente.

### Fluxo da aplicação

1. O cliente envia uma URL para `POST /api/v1/summarize`.
2. A API verifica se a URL já existe na tabela `saved_summaries`.
3. Se existir cache, o resumo salvo é retornado imediatamente.
4. Se não existir cache, a aplicação busca a página com `httpx`.
5. O HTML é processado com Beautiful Soup e convertido em texto limpo.
6. O texto extraído é enviado ao Gemini.
7. A resposta do Gemini é validada pelo modelo `SummaryResponse`.
8. O resultado é salvo em SQLite.
9. A resposta estruturada é retornada ao cliente.

Para tradução:

1. O cliente envia URL e idioma-alvo para `POST /api/v1/translate`.
2. A API procura a URL no cache.
3. Se não existir resumo salvo, retorna `404`.
4. Se existir, traduz título, resumo e cada item de `key_takeaways`.
5. Retorna a versão traduzida sem alterar o registro original no banco.

### Comunicação entre frontend e backend

O repositório contém apenas o backend. A comunicação é feita por HTTP/JSON. Há CORS liberado para:

- `http://localhost:3000`
- `https://delimadev.vercel.app`

Não foi identificado frontend dentro deste projeto.

### Consumo de APIs externas

- O scraper consome páginas públicas usando `httpx.AsyncClient`.
- O serviço de IA consome a API Gemini usando `google-genai`.
- A tradução usa `deep-translator`, que delega a tradução ao serviço configurado pela biblioteca.

### Persistência de dados

A persistência é feita em SQLite por meio do SQLAlchemy assíncrono. A tabela `saved_summaries` usa a URL como chave primária e armazena:

- `url`
- `title`
- `summary`
- `key_takeaways`
- `estimated_reading_time`

As tabelas são criadas automaticamente no `lifespan` da aplicação com `Base.metadata.create_all`.

## Decisões Técnicas

- **Uso de FastAPI com modelos Pydantic**: fornece validação automática de entrada e saída, documentação OpenAPI e respostas tipadas.
- **Pipeline assíncrono para scraping e banco**: `httpx`, SQLAlchemy async e `aiosqlite` reduzem bloqueios durante operações de I/O.
- **Cache por URL no SQLite**: evita chamadas repetidas ao Gemini para conteúdos já resumidos, reduzindo latência e custo de API.
- **Resposta estruturada do Gemini**: o uso de `response_schema=SummaryResponse` e validação com Pydantic reduz a chance de respostas fora do contrato esperado.
- **Separação por serviços**: scraping, geração com IA e tradução ficam isolados em módulos próprios, facilitando manutenção e testes futuros.
- **Tradução em executor de threads**: a biblioteca de tradução é síncrona; o uso de `ThreadPoolExecutor` evita bloquear diretamente o loop assíncrono da aplicação.
- **Docker multi-stage**: a imagem usa `uv` na etapa de build para instalar dependências e copia a `.venv` para uma imagem final baseada em Alpine.

## Como executar

### Clonar o repositório

```bash
git clone <url-do-repositorio>
cd review-sense
```

### Instalar dependências

Com `uv` instalado:

```bash
uv sync
```

### Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com a chave usada pelo serviço Gemini:

```env
GEMINI_API_KEY=sua-chave-do-gemini
```

Observação: o código lê a configuração `gemini_api_key` via `pydantic-settings`, que aceita a variável `GEMINI_API_KEY`.

### Executar em desenvolvimento

```bash
uv run uvicorn src.main:app --reload
```

A API ficará disponível em:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

O volume montado em `/data` preserva o arquivo SQLite entre execuções do container.

## Endpoints

### `GET /`

Verifica se a API está online.

### `POST /api/v1/summarize`

Extrai e resume o conteúdo de uma URL.

Payload:

```json
{
  "url": "https://exemplo.com/artigo"
}
```

Resposta:

```json
{
  "title": "Título do artigo",
  "summary": "Resumo em 2 a 3 parágrafos.",
  "key_takeaways": ["Insight 1", "Insight 2"],
  "estimated_reading_time": "5 min read"
}
```

### `POST /api/v1/translate`

Traduz um resumo já salvo em cache.

Payload:

```json
{
  "url": "https://exemplo.com/artigo",
  "target_language": "pt"
}
```

Observação: a URL precisa ter sido processada antes por `/api/v1/summarize`.

## Estrutura do Projeto

```text
review-sense/
├── src/
│   ├── api/
│   │   └── endpoints.py
│   ├── config/
│   │   └── settings.py
│   ├── services/
│   │   ├── gemini.py
│   │   ├── scraper.py
│   │   └── translator.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

- `src/api/`: rotas HTTP e contratos de entrada.
- `src/config/`: leitura de configurações e variáveis de ambiente.
- `src/services/`: integrações e regras operacionais para scraping, IA e tradução.
- `src/database.py`: conexão e sessões assíncronas do banco.
- `src/models.py`: entidades persistidas.
- `src/main.py`: criação da aplicação FastAPI.
- `Dockerfile`: build e execução em container.
- `pyproject.toml`: metadados, dependências e configuração de ferramentas Python.
- `uv.lock`: lockfile das dependências gerenciado pelo `uv`.

## Melhorias Futuras

- Adicionar testes automatizados para endpoints, serviços de scraping e cache.
- Incluir migrações de banco com ferramenta própria, como Alembic, caso o modelo de dados evolua.
- Tornar o caminho do banco configurável por variável de ambiente.
- Centralizar a tradução usando o módulo `src/services/translator.py`, evitando duplicação de lógica em `endpoints.py`.
- Adicionar autenticação ou rate limiting caso a API seja exposta publicamente.
- Melhorar observabilidade com logs estruturados e tratamento padronizado de erros.
- Documentar exemplos reais de chamadas com `curl` ou coleção HTTP.
- Configurar pipeline de CI para lint, testes e build Docker.
- Definir uma estratégia para lidar com páginas protegidas, conteúdo dinâmico ou extração parcial.
