import os
import subprocess

dir = "D:\KDRR (mp3)"

print(f"Сканируем папки в {dir}:")
for item in os.listdir(dir):
    full_path = os.path.join(dir, item)
    if os.path.isdir(full_path):
        print(f"Найдена папка: {full_path}")

print("Запускаем foobar...")
subprocess.run(["C:\Program Files (x86)\\foobar2000"])
