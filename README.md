# MEDEIA-ANDROID

Aplicativo Android independente de mídia, com player integrado e catálogo organizado.

## Estado do projeto

**Etapa 1 — fundação Android:** estrutura Kotlin/Jetpack Compose e compilação APK Debug via GitHub Actions.

Os motores Media3 e LibVLC entram como dependências desde a fundação. A integração visual completa, o roteador de fallback e os testes de reprodução serão implementados em etapas posteriores.

## Arquitetura planejada

- **Interface:** Kotlin + Jetpack Compose.
- **Motor principal:** AndroidX Media3 / ExoPlayer.
- **Motor alternativo:** LibVLC Android.
- **Orquestração:** Playback Maestro, com seleção por capacidade e erro técnico.
- **Catálogo:** M3U/M3U8 e JSON.
- **EPG:** XMLTV, em etapa futura.
- **Build:** GitHub Actions, gerando APK Debug.

## Comparação dos motores

| Recurso | Media3 | LibVLC |
|---|---|---|
| HLS | Suporte nativo via módulo HLS | Suportado |
| DASH | Módulo específico | Suportado |
| MP4 | Conforme codecs do dispositivo | Amplo suporte |
| MKV | Conforme extratores/codecs disponíveis | Amplo suporte |
| RTSP | Extensão RTSP | Suportado |
| Integração Android | APIs AndroidX modernas | Biblioteca nativa VLC |
| Tamanho | Geralmente menor | Geralmente maior |

A compatibilidade final depende do codec, dispositivo, servidor, DRM, autenticação e condições da transmissão. Nenhum motor garante reprodução de todo endereço.

## Requisitos

- Android mínimo: API 23 (Android 6.0).
- Compilação: JDK 17 + Gradle 8.13.
- Android SDK: API 36.

## Gerar APK

1. Abra a aba **Actions** no GitHub.
2. Selecione **Android Debug APK**.
3. Toque em **Run workflow**.
4. Aguarde o job terminar.
5. Baixe o artefato `medeia-debug-apk` na execução concluída.

## Política de fontes

O aplicativo deve reproduzir apenas conteúdos que o usuário tenha direito de acessar. O catálogo não deve contornar DRM, autenticação, bloqueios geográficos ou restrições de transmissão.

## Licenças

Media3 é distribuído sob Apache License 2.0. LibVLC Android usa LGPL para a biblioteca, mas a distribuição e o empacotamento exigem revisão das obrigações de licenciamento, avisos e componentes incluídos antes de publicar o APK.
