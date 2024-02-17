# acd_create lib by anycorp.dev team.
import os
import random
import string
from colorama import Fore, Style

class acd_create:
    def __init__(self):
        self.disk = ''

    def setdisk(self, disk_path):
        self.disk = disk_path

    def _generate_random_color(self):
        colors = [Fore.GREEN, Fore.YELLOW, Fore.RED, Fore.BLUE, Fore.WHITE]
        return random.choice(colors)

    def _generate_random_text(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(10))

    def _create_file(self, file_number, size_mb):
        file_name = f'anycorp.dev.create.{file_number}.txt'
        file_path = os.path.join(self.disk, file_name)
        with open(file_path, 'wb') as f:
            f.seek(size_mb * 1024 * 1024 - 1)
            f.write(b'\0')

        color = self._generate_random_color()
        print(f"[ {color}CREATE{Style.RESET_ALL} ] {color}Создан файл {file_name} с размером {size_mb} мб. по пути {file_path}{Style.RESET_ALL}")

    def __call__(self, num_files, size_mb):
        num_files = int(num_files)
        size_mb = int(size_mb)
        for i in range(1, num_files + 1):
            self._create_file(i, size_mb)
        print(f"\n[ {Fore.RED}CREATE{Style.RESET_ALL} ] {Fore.GREEN}Всего создано: {num_files} файлов. Путь к диску: {self.disk}{Style.RESET_ALL}")

class acd_clean:
    def __init__(self):
        self.disk = ''

    def setdisk(self, disk_path):
        self.disk = disk_path

    def _find_and_delete_files(self):
        files_to_delete = [f for f in os.listdir(self.disk) if f.startswith('anycorp.dev.create.') and f.endswith('.txt')]
        num_files = len(files_to_delete)
        print(f"[ {Fore.RED}CLEAR{Style.RESET_ALL} ] {Fore.GREEN}Найдено: {num_files} файлов. Удалить их? Y / N{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'y':
            for file in files_to_delete:
                os.remove(os.path.join(self.disk, file))
        else:
            input("Нажмите Enter для закрытия... \n\n")

    def __call__(self):
        self._find_and_delete_files()
