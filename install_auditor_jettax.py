import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=== Instalador do AuditorJettax ===")
    
    # Definir diretório de instalação
    default_install_dir = os.path.join(os.path.expanduser("~"), "AuditorJettax")
    install_dir = input(f"Diretório de instalação [{default_install_dir}]: ").strip()
    if not install_dir:
        install_dir = default_install_dir
    
    install_path = Path(install_dir)
    
    # Criar diretório de instalação
    print(f"\nInstalando AuditorJettax em {install_path}...")
    install_path.mkdir(parents=True, exist_ok=True)
    
    # Copiar arquivos necessários
    current_dir = Path(__file__).parent.absolute()
    
    files_to_copy = [
        "app_full.py", "app_pdf.py", "logo.webp",
        "requirements.txt", ".env"
    ]
    
    folders_to_copy = ["relatorios", "transcricoes", "scripts"]
    
    for file in files_to_copy:
        source = current_dir / file
        target = install_path / file
        try:
            if source.exists():
                shutil.copy2(source, target)
                print(f"Copiado: {file}")
            else:
                print(f"Aviso: Arquivo não encontrado: {file}")
        except Exception as e:
            print(f"Erro ao copiar {file}: {str(e)}")
    
    for folder in folders_to_copy:
        source = current_dir / folder
        target = install_path / folder
        try:
            if source.exists():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(source, target)
                print(f"Copiada pasta: {folder}")
            else:
                print(f"Criando pasta: {folder}")
                target.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Erro ao copiar pasta {folder}: {str(e)}")
    
    # Criar arquivo .env se não existir
    env_file = install_path / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("GOOGLE_API_KEY=\n")
        print("Criado arquivo .env para configuração da API")
    
    # Criar ambiente virtual
    venv_dir = install_path / "venv"
    print("\nCriando ambiente virtual Python...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    except Exception as e:
        print(f"Erro ao criar ambiente virtual: {str(e)}")
        return
    
    # Instalar dependências
    pip_path = venv_dir / "Scripts" / "pip.exe"
    print("\nInstalando dependências. Isso pode levar alguns minutos...")
    try:
        subprocess.run([str(pip_path), "install", "-r", str(install_path / "requirements.txt")], check=True)
    except Exception as e:
        print(f"Erro ao instalar dependências: {str(e)}")
        return
    
    # Criar atalhos no desktop e menu iniciar
    try:
        create_shortcuts(install_path, venv_dir)
    except Exception as e:
        print(f"Erro ao criar atalhos: {str(e)}")
    
    print("\n=== Instalação concluída com sucesso! ===")
    print(f"O AuditorJettax foi instalado em: {install_path}")
    
    # Perguntar se deseja executar o aplicativo
    if input("\nDeseja executar o AuditorJettax agora? (s/n): ").lower().startswith('s'):
        try:
            subprocess.Popen([str(venv_dir / "Scripts" / "python.exe"), str(install_path / "app_full.py")])
        except Exception as e:
            print(f"Erro ao iniciar o aplicativo: {str(e)}")
            print(f"Você pode iniciar manualmente executando: {install_path / 'app_full.py'}")
    else:
        print("\nVocê pode iniciar o aplicativo pelo atalho criado ou executando o arquivo app_full.py")

def create_shortcuts(install_path, venv_path):
    """Cria atalhos para o aplicativo no desktop e menu iniciar"""
    try:
        import win32com.client
        
        # Caminho para o Python do ambiente virtual
        python_exe = venv_path / "Scripts" / "python.exe"
        
        # Script para criar atalho
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Atalho no Desktop
        desktop = shell.SpecialFolders("Desktop")
        shortcut = shell.CreateShortCut(os.path.join(desktop, "AuditorJettax.lnk"))
        shortcut.TargetPath = str(python_exe)
        shortcut.Arguments = f'"{install_path / "app_full.py"}"'
        shortcut.WorkingDirectory = str(install_path)
        shortcut.IconLocation = str(install_path / "logo.webp")
        shortcut.Description = "AuditorJettax - Auditoria Inteligente de Reuniões"
        shortcut.Save()
        print("Criado atalho no Desktop")
        
        # Atalho no Menu Iniciar
        start_menu = shell.SpecialFolders("StartMenu")
        programs = os.path.join(start_menu, "Programs")
        
        jettax_folder = os.path.join(programs, "AuditorJettax")
        os.makedirs(jettax_folder, exist_ok=True)
        
        shortcut = shell.CreateShortCut(os.path.join(jettax_folder, "AuditorJettax.lnk"))
        shortcut.TargetPath = str(python_exe)
        shortcut.Arguments = f'"{install_path / "app_full.py"}"'
        shortcut.WorkingDirectory = str(install_path)
        shortcut.IconLocation = str(install_path / "logo.webp")
        shortcut.Description = "AuditorJettax - Auditoria Inteligente de Reuniões"
        shortcut.Save()
        print("Criado atalho no Menu Iniciar")
        
    except Exception as e:
        print(f"Erro ao criar atalhos: {str(e)}")
        print("Você pode iniciar o aplicativo manualmente.")

if __name__ == "__main__":
    main()