# Gerar o ViolinMentor para Windows

O projeto oferece duas opções de empacotamento. O script `build_exe.py` gera um único executável, que pode ser aberto com duplo clique. O script `build_windows.ps1` mantém a opção `onedir` e cria um atalho na Área de Trabalho.

## Executável único

1. Instale o Python 64-bit e abra o PowerShell na pasta do projeto.
2. Crie e ative um ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Execute o empacotador:

   ```powershell
   python build_exe.py
   ```

   O script instala o PyInstaller se necessário e gera `dist\ViolinMentor\ViolinMentor.exe` com ícone, assets e dados de pacote não pessoais. Não é necessário manter uma pasta `_internal` para esse modo.

Para regenerar o ícone moderno de violino em 16, 32, 64 e 256 px, execute `python generate_icon.py` antes do build. O ícone fica em `assets\violino.ico` e é usado pelo executável e pela janela do aplicativo.

## Pacote com atalho

Para gerar a alternativa `onedir` e criar ou atualizar o atalho na Área de Trabalho, execute:

```powershell
   .\build_windows.ps1
```

O script instala as dependências de `requirements-build.txt`, inclui o ícone no executável e configura o atalho para apontar diretamente ao arquivo `.ico`. Se o PowerShell bloquear scripts, permita a execução apenas na janela atual com `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e tente novamente.

## Arquivos gerados e dados

- Executável (ambos os modos): `dist\ViolinMentor\ViolinMentor.exe`
- Atalho: `ViolinMentor.lnk` na Área de Trabalho.
- No modo `onedir`, mantenha toda a pasta `dist\ViolinMentor`, incluindo `_internal`. No modo `onefile`, basta o executável.
- No build instalado, histórico, WAVs e logs são gravados em `%LOCALAPPDATA%\ViolinMentor\data`. Em execução pelo código-fonte, continuam em `data\`.
- O ícone e os arquivos em `assets\` são incluídos no pacote. Imagens opcionais ausentes continuam mostrando o espaço reservado na aba de técnica.

O build deve ser feito no Windows. Para testar no código-fonte, use `python main.py`; esse comando continua disponível para desenvolvimento, mas não é necessário para abrir o executável ou seu atalho.
