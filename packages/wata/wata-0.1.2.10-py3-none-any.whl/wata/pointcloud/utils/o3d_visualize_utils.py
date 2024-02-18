"""
Open3d visualization tool box
Written by Jihan YANG
All rights preserved from 2021 - present.
"""
import matplotlib
import numpy as np
import open3d

box_colormap = [
    [1, 1, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 1, 0],
]


def create_mesh_plane(grid_width=10.0, plane_width=200.0, z_position=-5, color=[0.2, 0.2, 0.2]):
    lines = []
    line_points = []
    grid_nums = plane_width / grid_width / 2
    for j in range(int(-1 * grid_nums), int(grid_nums + 1)):
        line_points.extend([[plane_width / 2, -j * grid_width, z_position],
                            [-1 * plane_width / 2, -j * grid_width, z_position]])
        # print("-----------------")
        # for j in range(int(-1 * grid_nums), int(grid_nums + 1)):
        line_points.extend([[j * grid_width, plane_width / 2, z_position],
                            [j * grid_width, -1 * plane_width / 2, z_position]])
    for i in range(int(len(line_points) / 2)):
        lines.append([2 * i, 2 * i + 1])
    line_set = open3d.geometry.LineSet()
    line_set.points = open3d.utility.Vector3dVector(line_points)
    line_set.lines = open3d.utility.Vector2iVector(lines)
    line_set.colors = open3d.utility.Vector3dVector([color for i in range(len(lines))])  # 设置颜色为红色
    # o3d.visualization.draw_geometries([line_set])
    return line_set


def get_coor_colors(obj_labels):
    """
    Args:
        obj_labels: 1 is ground, labels > 1 indicates different instance cluster

    Returns:
        rgb: [N, 3]. color for each point.
    """
    colors = matplotlib.colors.XKCD_COLORS.values()
    max_color_num = obj_labels.max()

    color_list = list(colors)[: max_color_num + 1]
    colors_rgba = [matplotlib.colors.to_rgba_array(color) for color in color_list]
    label_rgba = np.array(colors_rgba)[obj_labels]
    label_rgba = label_rgba.squeeze()[:, :3]

    return label_rgba


def open3d_draw_scenes(points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None, ref_plane=True,
                       point_colors=None, draw_origin=True):
    vis = open3d.visualization.Visualizer()
    vis.create_window()

    vis.get_render_option().point_size = 1.0
    vis.get_render_option().background_color = np.zeros(3)

    if ref_plane:
        plane = create_mesh_plane()
        vis.add_geometry(plane)

    # draw origin
    if draw_origin:
        axis_pcd = open3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0, origin=[0, 0, 0])
        vis.add_geometry(axis_pcd)

    pts = open3d.geometry.PointCloud()
    pts.points = open3d.utility.Vector3dVector(points[:, :3])

    vis.add_geometry(pts)
    if point_colors is None:
        pts.colors = open3d.utility.Vector3dVector(np.ones((points.shape[0], 3)))
    else:
        pts.colors = open3d.utility.Vector3dVector(point_colors)

    if gt_boxes is not None:
        vis = draw_box(vis, gt_boxes, (0, 0, 1))

    if ref_boxes is not None:
        vis = draw_box(vis, ref_boxes, (0, 1, 0), ref_labels, ref_scores)

    vis.run()
    vis.destroy_window()


def translate_boxes_to_open3d_instance(gt_boxes):
    """
       4-------- 6
     /|         /|
    5 -------- 3 .
    | |        | |
    . 7 -------- 1
    |/         |/
    2 -------- 0
    """
    center = gt_boxes[0:3]
    lwh = gt_boxes[3:6]
    axis_angles = np.array([0, 0, gt_boxes[6] + 1e-10])
    rot = open3d.geometry.get_rotation_matrix_from_axis_angle(axis_angles)
    box3d = open3d.geometry.OrientedBoundingBox(center, rot, lwh)

    line_set = open3d.geometry.LineSet.create_from_oriented_bounding_box(box3d)

    # import ipdb; ipdb.set_trace(context=20)
    lines = np.asarray(line_set.lines)
    lines = np.concatenate([lines, np.array([[1, 4], [7, 6]])], axis=0)

    line_set.lines = open3d.utility.Vector2iVector(lines)

    return line_set, box3d


def draw_box(vis, gt_boxes, color=(0, 1, 0), ref_labels=None, score=None):
    for i in range(gt_boxes.shape[0]):
        line_set, box3d = translate_boxes_to_open3d_instance(gt_boxes[i])
        if ref_labels is None:
            line_set.paint_uniform_color(color)
        else:
            line_set.paint_uniform_color(box_colormap[ref_labels[i]])

        vis.add_geometry(line_set)

        # if score is not None:
        #     corners = box3d.get_box_points()
        #     vis.add_3d_label(corners[5], '%.2f' % score[i])
    return vis


def show_pcd_from_points_by_open3d(points, point_size=1, background_color=[0, 0, 0]):
    coordinate = open3d.geometry.TriangleMesh.create_coordinate_frame(size=5)
    plane = create_mesh_plane()

    pcd = open3d.geometry.PointCloud()
    pcd.points = open3d.utility.Vector3dVector(points)
    vis = open3d.visualization.Visualizer()
    vis.create_window(window_name='show_pcd_by_open3d', width=1200, height=800)

    opt = vis.get_render_option()
    opt.point_size = point_size
    opt.background_color = np.asarray(background_color)

    vis.add_geometry(pcd)
    vis.add_geometry(coordinate)
    vis.add_geometry(plane)

    vis.run()
    vis.clear_geometries()
    vis.destroy_window()
