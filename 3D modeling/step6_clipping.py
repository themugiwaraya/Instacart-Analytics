import open3d as o3d
import numpy as np
import sys

# === 1. Получаем путь к файлу ===
if len(sys.argv) < 2:
    print("Использование: python step6_clipping.py <путь_к_PLY_или_OBJ>")
    sys.exit(1)

file_path = sys.argv[1]

# === 2. Загружаем меш ===
mesh = o3d.io.read_triangle_mesh(file_path)
if mesh.is_empty():
    print("❌ Ошибка: не удалось прочитать mesh.")
    sys.exit(1)

mesh.compute_vertex_normals()
print("✅ Модель загружена")

# === 3. Определим центр модели (через bounding box) ===
bbox = mesh.get_axis_aligned_bounding_box()
center = bbox.get_center()
print(f"Центр модели: {center}")

# === 4. Создаём плоскость, проходящую через центр ===
plane = o3d.geometry.TriangleMesh.create_box(width=5, height=0.01, depth=5)
plane.translate(center - np.array([2.5, 0.005, 2.5]))
plane.paint_uniform_color([0.2, 0.8, 1.0])

# === 5. Клиппинг: удаляем вершины выше плоскости ===
# В Open3D проще работать с вершинами напрямую
vertices = np.asarray(mesh.vertices)
triangles = np.asarray(mesh.triangles)

# Плоскость горизонтальная → сравним по оси Y (вторая координата)
y_center = center[1]

mask = vertices[:, 1] <= y_center  # оставляем всё, что ниже (или на) плоскости

# Создаём новый массив индексов для оставшихся вершин
new_vertices = vertices[mask]

# Нужно обновить треугольники, чтобы использовать только оставшиеся вершины
# Для этого создаём отображение старых индексов → новые
index_map = -np.ones(len(vertices), dtype=int)
index_map[mask] = np.arange(len(new_vertices))

# Оставляем только треугольники, все 3 вершины которых остались после клиппинга
new_triangles = []
for tri in triangles:
    if all(index_map[v] != -1 for v in tri):
        new_triangles.append(index_map[tri])
new_triangles = np.array(new_triangles)

# === 6. Создаём новый меш ===
clipped_mesh = o3d.geometry.TriangleMesh()
clipped_mesh.vertices = o3d.utility.Vector3dVector(new_vertices)
clipped_mesh.triangles = o3d.utility.Vector3iVector(new_triangles)
clipped_mesh.compute_vertex_normals()
clipped_mesh.paint_uniform_color([0.9, 0.6, 0.3])

# === 7. Выводим статистику ===
print("\n=== После обрезки ===")
print("Количество вершин:", len(clipped_mesh.vertices))
print("Количество треугольников:", len(clipped_mesh.triangles))
print("Наличие нормалей:", clipped_mesh.has_vertex_normals())
print("Наличие цветов:", clipped_mesh.has_vertex_colors())
print("=====================\n")

# === 8. Визуализация ===
o3d.visualization.draw_geometries(
    [clipped_mesh, plane],
    window_name="Обрезанная модель (клиппинг по плоскости)",
    width=1000,
    height=700
)
