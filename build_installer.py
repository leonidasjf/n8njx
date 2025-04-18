import os
import subprocess
import sys
from pathlib import Path

def main():
    """
    Script para criar o instalador do AuditorJettax usando PyInstaller
    """
    print("=== Gerando instalador do AuditorJettax ===")
    
    # Verifica se PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado.")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller", "pywin32"], check=True)
    
    # Instalar pywin32 se ainda não estiver instalado
    try:
        import win32com
    except ImportError:
        print("Instalando pywin32...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
    
    # Cria o arquivo spec para o PyInstaller
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['install_auditor_jettax.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('logo.webp', '.'),
                ('requirements.txt', '.'),
                ('app_full.py', '.'),
                ('app_pdf.py', '.'),
                ('relatorios', 'relatorios'),
                ('transcricoes', 'transcricoes'),
                ('scripts', 'scripts')
             ],
             hiddenimports=['win32com'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AuditorJettax_Setup',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='logo.webp')
"""
    
    with open("auditor_jettax.spec", "w") as f:
        f.write(spec_content)
    
    print("Arquivo de configuração 'auditor_jettax.spec' criado.")
    
    # Crie as pastas necessárias se não existirem
    Path("relatorios").mkdir(exist_ok=True)
    Path("transcricoes").mkdir(exist_ok=True)
    Path("scripts").mkdir(exist_ok=True)
    
    # Executa o PyInstaller
    print("\nCompilando instalador. Isso pode levar alguns minutos...")
    subprocess.run([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "auditor_jettax.spec",
        "--clean"
    ], check=True)
    
    # Caminhos do executável gerado
    dist_path = Path("dist")
    exe_path = dist_path / "AuditorJettax_Setup.exe"
    
    if exe_path.exists():
        print(f"\n✓ Instalador gerado com sucesso: {exe_path}")
        print("Você pode distribuir este executável para instalar o AuditorJettax em outros computadores.")
    else:
        print("\n⚠ Erro ao gerar instalador. Verifique os logs acima.")

if __name__ == "__main__":
    main()