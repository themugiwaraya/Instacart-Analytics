import open3d as o3d
import sys
import numpy as np

# === 1. Чтение аргумента ===
if len(sys.argv) < 2:
    print("Использование: python step5_plane_through_object.py <путь_к_PLY_или_OBJ>")
    sys.exit(1)

file_path = sys.argv[1]

# === 2. Загружаем 3D модель ===
mesh = o3d.io.read_triangle_mesh(file_path)
if mesh.is_empty():
    print("Ошибка: не удалось прочитать mesh.")
    sys.exit(1)

mesh.compute_vertex_normals()

# === 3. Центр модели (чтобы знать где середина) ===
center = mesh.get_center()
print(f"Центр модели: {center}")

# === 4. Создаём плоскость ===
# Плоскость — очень тонкая коробка, чтобы она выглядела как "разрез"
plane = o3d.geometry.TriangleMesh.create_box(width=5, height=0.01, depth=5)

# === 5. Сдвигаем плоскость в центр модели ===
# (Чтобы она делила бургер пополам)
plane.translate(center - np.array([2.5, 0.005, 2.5]))

# === 6. Добавим цвет ===
mesh.paint_uniform_color([0.9, 0.6, 0.3])   # бургер — светло-коричневый
plane.paint_uniform_color([0.2, 0.8, 1.0])  # плоскость — голубая

# === 7. Визуализация ===
print("Открываю окно визуализации (плоскость проходит через середину модели)...")
o3d.visualization.draw_geometries(
    [mesh, plane],
    window_name="Бургер и плоскость через центр",
    width=1000,
    height=700
)
