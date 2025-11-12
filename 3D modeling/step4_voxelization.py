import open3d as o3d
import sys

# === 1. Чтение аргумента ===
if len(sys.argv) < 2:
    print("Использование: python step4_voxelization.py <путь_к_PLY_или_PCD>")
    sys.exit(1)

file_path = sys.argv[1]

# === 2. Загружаем облако точек ===
pcd = o3d.io.read_point_cloud(file_path)

if len(pcd.points) == 0:
    print("Ошибка: облако точек пустое или нечитабельное.")
    sys.exit(1)

print("=== Исходное облако точек ===")
print(f"Количество точек: {len(pcd.points)}")
print(f"Наличие цвета: {pcd.has_colors()}")
print("=============================")

# === 3. Преобразуем в воксельную сетку ===
voxel_size = 0.05  # ← можешь менять (0.02, 0.05, 0.1 и т.д.)
print(f"Создаю воксельную сетку (voxel_size = {voxel_size})...")

voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=voxel_size)

print("Вокселизация завершена.")

# === 4. Проверяем характеристики ===
print("=== Описание воксельной модели ===")
print(f"Количество вокселей: {len(voxel_grid.get_voxels())}")
print(f"Есть ли цвет: {'Да' if voxel_grid.has_colors() else 'Нет'}")
print("===================================")

# === 5. Визуализация ===
print("Открываю окно визуализации...")
o3d.visualization.draw_geometries([voxel_grid], window_name="Воксельная модель")

print("Закрой окно, чтобы завершить выполнение.")
