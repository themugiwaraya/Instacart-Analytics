# step1_open3d.py
# Python 3.8+; Open3D (pip install open3d)

import open3d as o3d
import sys
import os

def describe_mesh(mesh):
    print("=== Описание меша ===")
    print("Количество вершин:", len(mesh.vertices))
    print("Количество треугольников:", len(mesh.triangles))
    print("Наличие нормалей (vertex normals):", mesh.has_vertex_normals())
    print("Наличие цветов (vertex colors):", mesh.has_vertex_colors())
    print("=====================\n")

def describe_pointcloud(pcd):
    print("=== Описание point cloud ===")
    print("Количество точек:", len(pcd.points))
    # Треугольников у облака нет
    print("Количество треугольников: N/A (это PointCloud)")
    print("Наличие нормалей:", pcd.has_normals())
    print("Наличие цветов:", pcd.has_colors())
    print("===========================\n")

def load_and_describe(path):
    ext = os.path.splitext(path)[1].lower()
    # Популярные форматы мешей: .ply, .obj, .stl, .off
    # PointCloud: .ply может быть и меш, и pointcloud -> попробуем читать как mesh сначала
    if ext in ['.obj', '.stl', '.off'] or ext in ['.ply']:
        # Сначала пытаемся загрузить как TriangleMesh
        try:
            mesh = o3d.io.read_triangle_mesh(path)
        except Exception as e:
            print("Ошибка чтения как mesh:", e)
            mesh = None

        # Если mesh прочитан и содержит вершины
        if mesh is not None and len(mesh.vertices) > 0 and len(mesh.triangles) > 0:
            print("Файл распознан как TriangleMesh.")
            describe_mesh(mesh)
            print("Открываю окно визуализации (mesh). Закройте окно, чтобы продолжить.")
            o3d.visualization.draw_geometries([mesh], window_name="Step 1 - Original Mesh")
            # После закрытия окна - краткое понимание
            print("Что я понял: это треугольная сетка. Проверьте, есть ли артефакты или незаполненные участки.")
            return

        # Если mesh пустой или не содержит треугольников, пробуем читать как point cloud
        try:
            pcd = o3d.io.read_point_cloud(path)
        except Exception as e:
            print("Ошибка чтения как point cloud:", e)
            pcd = None

        if pcd is not None and len(pcd.points) > 0:
            print("Файл распознан как PointCloud.")
            describe_pointcloud(pcd)
            print("Открываю окно визуализации (point cloud). Закройте окно, чтобы продолжить.")
            o3d.visualization.draw_geometries([pcd], window_name="Step 1 - Original PointCloud")
            print("Что я понял: это облако точек. Осмотрите плотные/редкие области, наличие шумов.")
            return

        # Если ни mesh, ни pcd не подошли
        print("Не удалось прочитать содержимое как mesh или point cloud (или файл пуст).")
        return
    else:
        # Для прочих расширений попробуем оба варианта
        print("Неизвестное расширение, пытаюсь загрузить и как mesh, и как point cloud.")
        # Попытка как mesh
        mesh = o3d.io.read_triangle_mesh(path)
        if mesh is not None and len(mesh.vertices) > 0:
            describe_mesh(mesh)
            o3d.visualization.draw_geometries([mesh], window_name="Step 1 - Original Mesh (unknown ext)")
            print("Что я понял: загружено как mesh.")
            return
        pcd = o3d.io.read_point_cloud(path)
        if pcd is not None and len(pcd.points) > 0:
            describe_pointcloud(pcd)
            o3d.visualization.draw_geometries([pcd], window_name="Step 1 - Original PointCloud (unknown ext)")
            print("Что я понял: загружено как point cloud.")
            return
        print("Не удалось загрузить файл.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python step1_open3d.py path/to/your_model.<ply|obj|stl|off|...>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print("Файл не найден:", path)
        sys.exit(1)
    load_and_describe(path)
