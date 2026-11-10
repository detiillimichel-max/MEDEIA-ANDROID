# MEDEIA — Arquitetura Oficial

**Documento:** Parte 1 — Projeto e referência oficial  
**Status:** Especificação inicial para orientar os sete pilares  
**Repositório:** `detiillimichel-max/MEDEIA-ANDROID`

## 1. Missão

O MEDEIA é um sistema de descoberta, organização e reprodução de conteúdos audiovisuais em Android. Seu motor de pesquisa identifica conteúdos e fontes públicas ou autorizadas; o validador organiza e verifica os resultados; o catálogo JSON entrega os dados à biblioteca Android; e o LibVLC realiza a reprodução de fontes compatíveis e acessíveis.

O sistema pode organizar filmes, séries, desenhos, documentários e canais de TV ao vivo. A inclusão de um conteúdo no catálogo não significa, por si só, que ele tenha autorização de distribuição ou que sua reprodução esteja garantida.

## 2. Os sete pilares

### Pilar 1 — MEDEIA: projeto e referência oficial
Define a missão, a arquitetura, os contratos de dados, as regras de segurança, os limites de cada componente e os critérios de conclusão. Este documento é a referência inicial para os demais pilares.

### Pilar 2 — Python: motor inteligente
Responsável por:
- Pesquisar conteúdos por nome e metadados.
- Descobrir repositórios públicos que disponibilizem playlists M3U/M3U8.
- Ler fontes de dados públicas ou autorizadas.
- Interpretar playlists e encaminhar registros ao validador.
- Deduplicar resultados e registrar a origem de cada descoberta.

O Python pesquisa e processa dados; não é o motor de reprodução.

### Pilar 3 — Validador e organizador
Responsável por identificar e normalizar:
- Nome e identificador do conteúdo.
- Tipo: filme, série, episódio, desenho, documentário ou canal de TV.
- Capa e metadados, quando disponíveis.
- Categoria e formato.
- Origem e endereço da fonte.
- Disponibilidade observada, compatibilidade provável e data da última verificação.
- Situação de autorização, quando conhecida.

Uma resposta HTTP bem-sucedida não comprova, sozinha, que o conteúdo possa ser reproduzido. A validação deve distinguir descoberta, acessibilidade e teste real de reprodução.

### Pilar 4 — Catálogo JSON
Armazena registros normalizados, identificadores estáveis, metadados, capas, categorias e uma ou mais fontes por conteúdo. O catálogo deve ter versão de esquema, data de geração e estados explícitos para dados desconhecidos ou ainda não testados.

### Pilar 5 — GitHub Actions: automação
Executa o motor Python de acordo com os gatilhos configurados, valida a saída, gera o catálogo e publica a versão aprovada. Falhas de pesquisa ou validação não devem substituir um catálogo válido por um arquivo vazio ou incompleto. Segredos e tokens devem ficar em GitHub Secrets ou em serviços próprios de segredos, nunca no repositório.

### Pilar 6 — MEDEIA Android: biblioteca
Consome o catálogo publicado e apresenta pesquisa, capas, categorias, detalhes e estados das fontes. O aplicativo não deve precisar repetir toda a pesquisa do motor Python para exibir a biblioteca. Deve tratar catálogo indisponível, desatualizado ou inválido sem perder a última versão local válida, quando houver cache implementado.

### Pilar 7 — LibVLC: reprodução
Recebe do aplicativo uma fonte selecionada e validada para tentativa de reprodução. É responsável pela reprodução no Android, pelos eventos de estado e pela comunicação de erros. Não pesquisa filmes por nome, não descobre repositórios e não gera o catálogo.

## 3. Fluxo integrado

1. Python pesquisa conteúdos e fontes públicas ou autorizadas.
2. Python interpreta os resultados e envia registros ao validador.
3. O validador normaliza metadados, verifica acessibilidade e classifica o estado das fontes.
4. O gerador produz um catálogo JSON versionado.
5. GitHub Actions executa testes e publica somente uma saída aprovada.
6. O MEDEIA Android obtém o catálogo e apresenta a biblioteca.
7. Quando o usuário seleciona um item, o aplicativo entrega uma fonte ao LibVLC.
8. O aplicativo registra o resultado da tentativa de reprodução sem confundir falha temporária com remoção definitiva da fonte.

## 4. Descoberta de playlists e fontes

O motor Python poderá pesquisar repositórios públicos do GitHub e localizar arquivos como `.m3u` e `.m3u8`. A pesquisa poderá usar a API oficial do GitHub e os arquivos públicos disponibilizados pelos próprios repositórios.

O parser deverá reconhecer, quando presentes:
- `#EXTINF` e atributos como `tvg-id`, `tvg-name`, `tvg-logo` e `group-title`.
- URLs HTTP e HTTPS.
- Playlists M3U comuns e playlists HLS usadas na reprodução.
- Metadados que permitam distinguir canais, filmes, séries ou outras categorias.

Uma playlist M3U pode listar muitos itens; uma M3U8 também pode ser uma playlist HLS de segmentos. O sistema deve distinguir o arquivo de índice da mídia final e não tratar toda URL terminada em M3U8 como um canal independente.

A descoberta de um repositório ou endereço não comprova autorização, estabilidade ou funcionamento. Só devem ser catalogadas fontes cujo uso seja público ou autorizado. Não contornar autenticação, DRM, bloqueios geográficos, paywalls, tokens, limites de acesso ou mecanismos antiabuso. Não armazenar credenciais ou URLs temporárias assinadas no catálogo.

## 5. Contrato inicial de dados

O contrato detalhado será mantido em `docs/DATA-CONTRACTS.md`. Como princípio, cada item deverá conter:

- `id`: identificador estável.
- `title`: título normalizado.
- `type`: tipo de conteúdo.
- `category`: categoria, quando conhecida.
- `poster`: imagem de capa ou null.
- `metadata`: dados complementares disponíveis.
- `sources[]`: lista de fontes associadas.
- `source.url`: endereço da fonte, apenas quando apropriado e seguro para publicação.
- `source.format`: formato identificado.
- `source.protocol`: HTTP ou HTTPS.
- `source.availability`: estado de acessibilidade observado.
- `source.playback_status`: estado do teste de reprodução.
- `source.authorization`: estado de autorização conhecido.
- `source.checked_at`: data da última verificação.

Estados desconhecidos devem ser representados explicitamente como `unknown`, `not_checked` ou null conforme o campo; não devem ser convertidos em aprovação.

## 6. Regras de segurança e preservação

1. MEDEIA-ANDROID permanece um projeto independente.
2. Não misturar código, catálogos, credenciais ou infraestrutura de outros projetos sem decisão explícita.
3. Não apagar, substituir ou migrar componentes funcionais sem auditoria, backup e autorização.
4. Não publicar segredos, tokens, cookies, credenciais ou URLs assinadas.
5. Não contornar DRM, autenticação, restrições geográficas ou controles de acesso.
6. Respeitar direitos autorais, licenças, termos das fontes e permissões de distribuição.
7. Usar HTTPS sempre que disponível. Não habilitar HTTP globalmente no Android apenas para fazer uma fonte funcionar.
8. Limitar frequência de consultas, tamanho de downloads, concorrência e tentativas; respeitar limites das APIs.
9. Registrar origem, horário e resultado das verificações.
10. Não remover uma fonte definitivamente por uma única falha temporária.

## 7. Regras de desenvolvimento

- Trabalhar em um pilar por vez.
- Definir entradas, saídas e testes antes de integrar um pilar.
- Preservar a última versão funcional do aplicativo e do catálogo.
- Validar JSON e executar testes antes da publicação.
- Fazer alterações pequenas, rastreáveis e com mensagens de commit descritivas.
- Não considerar uma dependência instalada como funcionalidade integrada.
- Não declarar uma fonte reproduzível sem teste real no dispositivo ou em ambiente equivalente.
- Registrar decisões arquiteturais que alterem responsabilidades ou contratos.

## 8. Critérios de conclusão da Parte 1

A Parte 1 será considerada concluída quando:
- Os sete pilares e seus limites estiverem aprovados.
- O fluxo de ponta a ponta estiver documentado.
- O contrato JSON estiver definido em documento próprio.
- Os estados de validação e reprodução estiverem definidos.
- As regras de segurança, publicação e preservação estiverem documentadas.
- Os critérios de teste e aceite dos pilares seguintes estiverem estabelecidos.

## 9. Estado atual conhecido

Esta documentação registra a arquitetura pretendida; não afirma que todos os componentes já estejam implementados. A auditoria inicial identificou uma base Android e dependências de reprodução declaradas, mas o motor Python, o validador, o gerador de catálogo e a integração efetiva do LibVLC ainda precisam ser desenvolvidos e testados.

A presença de Media3 no projeto atual deve ser preservada até uma decisão técnica específica sobre seu papel. Este documento não autoriza remover dependências nem alterar o player existente.

---

**Princípio central:** Python pesquisa e organiza; o validador verifica; JSON transporta o catálogo; GitHub Actions automatiza e publica; MEDEIA Android apresenta; LibVLC reproduz.
