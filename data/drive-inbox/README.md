# Entrada de links do Google Drive

- `links-drive.txt`: arquivo bruto original. O normalizador nunca o altera.
- `links-drive.normalized.json`: catálogo de candidatos gerado pelo motor.
- Títulos são associados quando aparecem em linha anterior ao link, ignorando linhas vazias.
- Duplicatas são identificadas pelo ID do Drive. A URL original completa é preservada, inclusive `resourcekey`.
- `availability: not_checked` significa que permissão e disponibilidade ainda não foram testadas.
- Este processo não baixa mídia, não contorna autenticação, DRM ou restrições de acesso.

Execute na raiz do repositório:

```bash
python engine/normalize_drive_inbox.py
```
