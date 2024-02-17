"""Setup Script. Run before deploy"""
import subprocess
from os import getcwd, path, remove


def execute_command(command):
    """Excecute CMD commands"""
    cmd = " ".join(command) if isinstance(command, list) else command
    print(f"Executing command: {cmd}")
    result = subprocess.run(command if isinstance(
        command, list) else f"{command}", check=False)
    print(
        f"Command result code: {result.returncode}. {
            'Excecuted successfully' if result.returncode == 0 else 'Error: '+str(result.stderr)}."
    )


def install_requirements(requirements_path):
    """Install requirements from txt file"""
    if path.isfile(requirements_path) and path.exists(requirements_path):
        requirements_bat = path.join(WD, "install_requirements.bat")
        with open(requirements_bat, "w+", encoding="utf-8") as setup_bat_script:
            setup_bat_script.write(
                f"""@echo off
        set original_dir=%CD%
        set venv_root_dir="{VENV_DIR}"
        set app_root_dir="{WD}"
        call %venv_root_dir%\\Scripts\\activate.bat
        cd %app_root_dir%
        pip install --upgrade -r "{requirements_path}"
        if %errorlevel% == 0 (
           call :rollback_setting
           echo 'Requirementes installed successfully.'
           exit /b 0
        ) else (
           call :rollback_setting
           echo 'Requirementes installation failed.'
           exit /b 1
        )
        :rollback_setting
                call %venv_root_dir%\\Scripts\\deactivate.bat
                cd %original_dir%
                exit /b 0
              """
            )
        setup_bat_script.close()
        execute_command(requirements_bat)
        remove(requirements_bat)


WD = getcwd()
VENV_DIR = path.join(WD, "my_venv")
print(f"Current working directory: {WD}")
print(f"Current virtual enviroment directory: {VENV_DIR}")
print()

if not path.exists(VENV_DIR):
    execute_command(["python", "-m", "venv", VENV_DIR])

install_requirements(path.join(WD, "requirements_for_build.txt"))
execute_command(["py", "-m", "build"])
execute_command(["py", "-m", "twine", "upload",
                "--repository", "pypi", "dist/*"])

install_requirements(path.join(WD, "requirements_for_test.txt"))
