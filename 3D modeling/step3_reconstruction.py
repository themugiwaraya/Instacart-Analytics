import open3d as o3d
import sys

# === 1. Чтение аргумента ===
if len(sys.argv) < 2:
    print("Использование: python step3_reconstruction.py <путь_к_PLY_или_PCD>")
    sys.exit(1)

file_path = sys.argv[1]

# === 2. Загружаем облако точек ===
pcd = o3d.io.read_point_cloud(file_path)

if len(pcd.points) == 0:
    print("Ошибка: облако точек пустое или нечитабельное.")
    sys.exit(1)

print("=== Облако точек ===")
print(f"Количество точек: {len(pcd.points)}")
print(f"Наличие цвета: {pcd.has_colors()}")
print("=====================")

# === 3. Реконструкция поверхности (метод Пуассона) ===
print("Выполняется реконструкция поверхности (Poisson)...")
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)
print("Реконструкция завершена.")

# === 4. Удаляем артефакты по плотности ===
print("Удаляем артефакты...")
# Вычисляем границы облака точек (bounding box)
bbox = pcd.get_axis_aligned_bounding_box()
bbox.color = (1, 0, 0)  # красный контур, для проверки

# Обрезаем всё за пределами границ исходного облака
mesh_crop = mesh.crop(bbox)

# === 5. Проверка данных ===
print("=== Описание реконструированного mesh ===")
print(f"Количество вершин: {len(mesh_crop.vertices)}")
print(f"Количество треугольников: {len(mesh_crop.triangles)}")
print(f"Наличие цвета (vertex colors): {mesh_crop.has_vertex_colors()}")
print("=========================================")

# === 6. Визуализация ===
print("Открываю окно визуализации...")
o3d.visualization.draw_geometries([mesh_crop], window_name="Реконструированный Mesh")

print("Закрой окно, чтобы завершить выполнение.")
