import subprocess
import random
import string
import shutil
import sys
import os

def get_dir_path():
    executable = os.path.abspath(os.sys.argv[0])
    return os.path.dirname(executable)

def random_name():
    upper_letters = string.ascii_uppercase
    lower_letters = string.ascii_lowercase
    numbers = string.digits
    
    password = ''
    password += random.choice(upper_letters)
    password += random.choice(lower_letters)
    password += random.choice(upper_letters)
    password += random.choice(lower_letters)
    password += random.choice(numbers)
    password += random.choice(upper_letters)
    password += random.choice(lower_letters)
    
    return password

def find_and_move_pyd(directory, target_dir, source_name):
    for filename in os.listdir(directory):
        if filename.startswith(f'{source_name}.') and filename.endswith('.pyd'):
            source_path = os.path.join(directory, filename)
            current_path = os.path.join(target_dir, f'{source_name}.pyd')
            
            try:
                os.rename(source_path, current_path)
            except FileExistsError:
                os.remove(current_path)
                os.rename(source_path, current_path)

def main():
    os.system('cls || clear')

    if len(sys.argv) != 2:
        print('Используйте: pydbuilder <путь_к_файлу>')
    else:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='UTF-8') as file:
                    main_code = file.read()
            except Exception as er:
                print(f'Ошибка при чтении файла: {er}')
                raise SystemExit(0)

            os.system(f'title Cythonizing "{os.path.basename(file_path)}"...')
            source_name = os.path.basename(file_path.split('.')[0])
            source_path = os.path.dirname(file_path)
            dir_path = os.path.join('C:\\Windows\\Temp', random_name())
            os.mkdir(dir_path)

            with open(os.path.join(dir_path, f'{source_name}.pyx'), 'w', encoding='UTF-8') as file:
                file.write(main_code)

            setup_code = f'from setuptools import setup\nfrom Cython.Build import cythonize\n\nsetup(\n    ext_modules=cythonize(\'{source_name}.pyx\', compiler_directives={{\'language_level\': \'3\'}})\n)'

            with open(os.path.join(dir_path, 'setup.py'), 'w', encoding='UTF-8') as file:
                file.write(setup_code)

            try:
                subprocess.run('python setup.py build_ext --inplace', cwd=dir_path, check=True, stdout=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                os.system('cls || clear')
                print(f'Ошибка при выполнении команды: {e}')
                raise SystemExit(0)

            try:
                find_and_move_pyd(dir_path, source_path, source_name)
                print(f'Файл "{source_name}.pyd" успешно создан!')
            except Exception as er:
                os.system('cls || clear')
                print(f'Ошибка при перемещении файла: {er}')
                raise SystemExit(0)

            shutil.rmtree(dir_path)
        else:
            print(f'Ошибка: Путь не найден')

if __name__ == '__main__':
    main()