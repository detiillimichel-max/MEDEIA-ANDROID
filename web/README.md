# MEDEIA Web — Biblioteca inicial

Esta interface é independente do aplicativo Android e fica isolada na pasta `web/`.

## Arquivos

- `index.html`: estrutura da interface.
- `style.css`: visual responsivo.
- `app.js`: identificação inicial de links, leitura de texto M3U, cards e armazenamento local.

## Como testar no GitHub Pages

1. Abra a aba **Actions** do repositório.
2. Selecione **MEDEIA Web - publicar teste**.
3. Toque em **Run workflow** e escolha a branch `medeia/google-drive-search-engine`.
4. Aguarde a publicação e abra a URL informada pelo job.

O workflow copia `data/drive-search/catalog.json` para dentro do artefato publicado e publica somente a pasta `web/`. É necessário habilitar GitHub Pages com a origem **GitHub Actions** em Settings → Pages. A publicação é manual e usa a branch selecionada; não altera `main`.

## Funcionalidades desta primeira versão

- Aceita um endereço HTTP/HTTPS individual.
- Reconhece links compartilhados do Google Drive.
- Identifica extensões M3U, M3U8/HLS e formatos comuns de mídia.
- Aceita texto M3U colado e cria um card por endereço HTTP/HTTPS encontrado.
- Carrega automaticamente o catálogo `data/drive-search/catalog.json` (404 registros nesta versão), quando publicado pelo workflow.
- Guarda os itens adicionados localmente no `localStorage` do navegador.
- Permite pesquisar, filtrar, excluir, exportar e importar o catálogo JSON.

## Limites conhecidos

Esta versão não consulta automaticamente URLs externas. Navegadores podem bloquear essas leituras por CORS, autenticação ou políticas do provedor. Por isso, links ficam com estado `not_checked` e não são anunciados como reproduzíveis.

O catálogo do Drive exibe os títulos e links registrados, preservando os `resourcekey` presentes nas URLs. Nome real, capa, permissão e reprodução não são verificados nesta etapa.

A próxima evolução é separar o motor Python e definir a API/contrato de dados. Não colocar credenciais, cookies, tokens ou URLs temporárias assinadas no catálogo.
