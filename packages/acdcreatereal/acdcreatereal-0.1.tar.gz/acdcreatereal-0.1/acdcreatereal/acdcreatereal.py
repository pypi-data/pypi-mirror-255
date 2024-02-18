import os
import random
import string
from colorama import Fore, Style

class Creator:
    def __init__(self):
        self.disk = ''

    def set_disk(self, disk_path):
        self.disk = disk_path

    def _generate_random_color(self):
        colors = [Fore.GREEN, Fore.YELLOW, Fore.RED, Fore.BLUE, Fore.WHITE]
        return random.choice(colors)

    def create_file(self, file_number, size_mb):
        file_name = f'anycorp.dev.create.{file_number}.txt'
        file_path = os.path.join(self.disk, file_name)

        while os.path.exists(file_path):
            file_number += 1
            file_name = f'anycorp.dev.create.{file_number}.txt'
            file_path = os.path.join(self.disk, file_name)

        data = b'\0' * (size_mb * 1024 * 1024)
        with open(file_path, 'wb') as f:
            f.write(data)
        color = self._generate_random_color()
        print(f"[{Fore.RED}CREATE{Style.RESET_ALL}] {color}Создан файл {file_name} с размером {size_mb} Мб. по пути {file_path}{Style.RESET_ALL}")

    def create(self, num_files, size_mb):
        num_files = int(num_files)
        size_mb = int(size_mb)
        files_created = 0
        for i in range(1, num_files + 1):
            self.create_file(i, size_mb)
            files_created += 1
        print(f"\n[{Fore.RED}CREATE{Style.RESET_ALL}] Всего создано функцией: {files_created} файлов. Путь к директории: {self.disk}{Style.RESET_ALL}")

    def delete_files(self):
        files_to_delete = [f for f in os.listdir(self.disk) if f.startswith('anycorp.dev.create.') and f.endswith('.txt')]
        num_files = len(files_to_delete)
        print(f"[{Fore.RED}CLEAR{Style.RESET_ALL}] {Fore.GREEN}Найдено: {num_files} файлов. Удалить их? Y / N{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'y':
            for file in files_to_delete:
                os.remove(os.path.join(self.disk, file))
            print(f"{num_files} файлов удалено.")
        else:
            input("Нажмите Enter для закрытия... \n\n")
