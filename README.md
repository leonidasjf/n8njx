# AuditorJettax

Aplicativo de auditoria inteligente de reuniões para a Jettax. Permite analisar arquivos de áudio e vídeo de reuniões, gerando transcrições e relatórios automatizados com insights de IA.

## Requisitos

- Python 3.9+ 
- Windows (para o instalador)
- Chave de API do Google Gemini

## Como criar o instalador

1. Certifique-se de que todos os arquivos do projeto estão presentes
2. Execute o script para criar o instalador:

```shell
python build_installer.py
```

3. O instalador será gerado na pasta `dist` como `AuditorJettax_Setup.exe`

## Instalação

O instalador configura automaticamente:
- Copia os arquivos necessários para a pasta escolhida
- Cria um ambiente virtual Python
- Instala todas as dependências
- Cria atalhos no desktop e menu iniciar

## Como usar

1. Execute o instalador `AuditorJettax_Setup.exe`
2. Siga as instruções na tela
3. Defina sua chave de API do Google Gemini no arquivo `.env`
4. Execute o aplicativo através do atalho criado

## Principais recursos

- Transcrição de arquivos de áudio/vídeo para texto
- Análise de sentimento e conteúdo de reuniões
- Geração de relatórios formatados em HTML
- Sistema de perguntas e respostas sobre as reuniões analisadas