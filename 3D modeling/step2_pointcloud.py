import open3d as o3d
import sys

# === Чтение пути к файлу из аргументов командной строки ===
if len(sys.argv) < 2:
    print("Использование: python step2_pointcloud.py <путь_к_файлу>")
    sys.exit(1)

file_path = sys.argv[1]

# === Читаем модель как облако точек ===
pcd = o3d.io.read_point_cloud(file_path)

# === Проверяем, удалось ли прочитать ===
if len(pcd.points) == 0:
    print("Ошибка: облако точек не было загружено. Возможно, формат файла не подходит.")
    sys.exit(1)

# === Выводим характеристики ===
print("=== Описание облака точек ===")
print(f"Количество точек: {len(pcd.points)}")
print(f"Наличие цвета (has_colors): {pcd.has_colors()}")
print("==============================")

# === Визуализация ===
o3d.visualization.draw_geometries([pcd], window_name="Point Cloud")

print("Открой визуализацию и закрой окно, чтобы продолжить.")
