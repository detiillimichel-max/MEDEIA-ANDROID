# Pesquisa Google Drive — MEDEIA

O motor `engine/search_google_drive.py` pesquisa resultados públicos indexados usando `site:drive.google.com` pela API Firecrawl v2. A consulta restringe os resultados ao domínio `drive.google.com` e lê somente os campos de resultado do índice (URL, título e descrição), sem fazer scraping profundo de cada página.

## Execução local

Requer Python 3.10+ e a variável de ambiente `FIRECRAWL_API_KEY`:

```bash
export FIRECRAWL_API_KEY="sua-chave"
python engine/search_google_drive.py --query "A fábrica de chocolate" --limit 10
```

No GitHub Actions, configure `FIRECRAWL_API_KEY` em Settings → Secrets and variables → Actions → New repository secret.

## Catálogo

A saída padrão é `data/drive-search/catalog.json`. Guarda ID, URL original, título e descrição retornados pela pesquisa, consulta, categoria pendente e estados explícitos de acesso não verificado.

## Limites

- A pesquisa encontra somente páginas indexadas pelo provedor; não enumera todo o Google Drive.
- Título/descrição do índice não substituem metadados confirmados pela API oficial do Drive.
- Resultado encontrado não significa que o arquivo está público ou acessível.
- Não baixa mídia, não contorna login, permissões, resourcekey, DRM ou telas de confirmação.
- Não testa reprodução nesta etapa.
- O arquivo bruto `data/drive-inbox/links-drive.txt` e o catálogo normalizado anterior não são modificados.
