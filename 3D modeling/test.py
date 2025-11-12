import open3d as o3d
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Использование: python step7_color_extremes.py <путь_к_файлу>")
    sys.exit(1)

file_path = sys.argv[1]

# 1. Загружаем меш
mesh = o3d.io.read_triangle_mesh(file_path)
if not mesh.has_vertex_normals():
    mesh.compute_vertex_normals()

# 2. Сбрасываем цвета
mesh.vertex_colors = o3d.utility.Vector3dVector(
    np.zeros((np.asarray(mesh.vertices).shape[0], 3))
)

# 3. Создаём градиент по оси Z
vertices = np.asarray(mesh.vertices)
z = vertices[:, 2]
z_normalized = (z - z.min()) / (z.max() - z.min())
colors = np.zeros((vertices.shape[0], 3))
colors[:, 0] = z_normalized
colors[:, 2] = 1 - z_normalized
mesh.vertex_colors = o3d.utility.Vector3dVector(colors)

# 4. Находим экстремумы
min_idx = np.argmin(z)
max_idx = np.argmax(z)
min_point = vertices[min_idx]
max_point = vertices[max_idx]

print("\n=== Экстремальные точки по оси Z ===")
print(f"Минимум Z: {min_point}")
print(f"Максимум Z: {max_point}")

# 5. Сферы для выделения
sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
sphere_min.translate(min_point)
sphere_min.paint_uniform_color([0, 1, 0])

sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
sphere_max.translate(max_point)
sphere_max.paint_uniform_color([1, 0, 0])

# 6. Добавляем оси
axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)

# 7. Визуализация
o3d.visualization.draw_geometries([mesh, sphere_min, sphere_max, axes])
