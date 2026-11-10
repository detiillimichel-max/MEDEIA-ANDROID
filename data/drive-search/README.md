# MEDEIA — Catálogo Google Drive

## Fontes
1. `data/drive-inbox/links-drive.txt`: links já coletados. O leitor extrai ID, rótulo e `resourcekey`, remove duplicações e preserva a URL original.
2. SearXNG: busca adicional de páginas indexadas com `site:drive.google.com <título>`. Não exige chave de API, mas depende de uma instância pública que habilite JSON.

## Gerar catálogo apenas com os links existentes
```bash
python -m engine.build_drive_catalog
```

## Adicionar uma busca SearXNG
Configure `SEARXNG_BASE_URL` com a URL HTTPS da instância escolhida, sem `/search`:
```bash
SEARXNG_BASE_URL="https://sua-instancia.example" python -m engine.build_drive_catalog --query "nome do filme" --limit 10
```
O motor chama `/search?q=...&format=json`. A instância precisa habilitar JSON; muitas instâncias públicas desativam esse formato ou aplicam limites. Não há rotação para contornar bloqueios ou limites.

## Segurança
- Não altera `links-drive.txt`.
- Não abre links individuais nem baixa mídia nesta fase.
- Preserva URLs originais e `resourcekey`.
- Deduplica por ID do arquivo.
- Marca acesso e reprodução como não verificados.
- A abertura final fica a cargo do Android/Google Drive, usando a conta e permissões do próprio usuário.
- Nenhum e-mail, cookie, senha ou token Google é necessário no GitHub Actions.
