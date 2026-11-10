# MEDEIA Web — Biblioteca inicial

Esta interface é independente do aplicativo Android e fica isolada na pasta `web/`.

## Arquivos

- `index.html`: estrutura da interface.
- `style.css`: visual responsivo.
- `app.js`: identificação inicial de links, leitura de texto M3U, cards e armazenamento local.

## Como testar

Abra `index.html` em um navegador moderno. Para testar no GitHub Pages, publique o conteúdo da pasta `web/` como site estático.

## Funcionalidades desta primeira versão

- Aceita um endereço HTTP/HTTPS individual.
- Reconhece links compartilhados do Google Drive.
- Identifica extensões M3U, M3U8/HLS e formatos comuns de mídia.
- Aceita texto M3U colado e cria um card por endereço HTTP/HTTPS encontrado.
- Guarda cards no `localStorage` do navegador.
- Permite pesquisar, filtrar, excluir, exportar e importar o catálogo JSON.

## Limites conhecidos

Esta versão não consulta automaticamente URLs externas. Navegadores podem bloquear essas leituras por CORS, autenticação ou políticas do provedor. Por isso, links ficam com estado `not_checked` e não são anunciados como reproduzíveis.

O link do Drive é reconhecido e seu ID pode ser extraído, mas nome real, capa, permissão e reprodução exigem uma etapa de integração com API/serviço autorizado.

A próxima evolução é separar o motor Python e definir a API/contrato de dados. Não colocar credenciais, cookies, tokens ou URLs temporárias assinadas no catálogo.
