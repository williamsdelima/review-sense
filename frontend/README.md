## Atualização 07/09

# Frontend Flask e Migração para o Render

Interface web server-side do Review Sense. Esta aplicação será implantada como
um serviço separado da API FastAPI e se comunicará com ela por HTTP privado no
Render.

## Organização

- `app.py`: ponto de entrada e fábrica da aplicação Flask.
- `config.py`: configuração do frontend por variáveis de ambiente.
- `routes/`: controllers HTTP, separados por área da interface.
- `services/`: cliente HTTP que encapsula o contrato com a API FastAPI.
- `templates/`: páginas Jinja e componentes reutilizáveis.
- `static/`: estilos, JavaScript e imagens servidos pelo Flask.
- `tests/`: testes específicos da interface.

Nenhuma lógica de resumo, Gemini ou persistência deve ser duplicada aqui. O
frontend apenas coleta dados, chama a API e apresenta a resposta.
