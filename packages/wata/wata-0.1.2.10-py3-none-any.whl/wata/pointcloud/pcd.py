from wata.pointcloud.utils.o3d_visualize_utils import open3d_draw_scenes, show_pcd_from_points_by_open3d
from wata.pointcloud.utils.qtopengl_visualize_utils import show_pcd_from_points_by_qtopengl
from wata.pointcloud.utils import utils


class PointCloudProcess:

    @staticmethod
    def cut_pcd(points, pcd_range):
        return utils.cut_pcd(points, pcd_range)

    @staticmethod
    def show_pcd(path, point_size=1, background_color=[0, 0, 0], pcd_range=None, bin_num_features=None, type='open3d'):
        points = PointCloudProcess.get_points(path, num_features=bin_num_features)[:, 0:3]
        if pcd_range:
            points = utils.cut_pcd(points, pcd_range)
        PointCloudProcess.show_pcd_from_points(points=points, point_size=point_size, background_color=background_color,
                                               type=type)

    @staticmethod
    def show_pcd_from_points(points, point_size=1, background_color=[0, 0, 0], type='open3d'):
        if type == 'open3d':
            show_pcd_from_points_by_open3d(points=points, point_size=point_size, background_color=background_color)
        elif type == 'qtopengl':
            show_pcd_from_points_by_qtopengl(points=points, point_size=point_size, background_color=background_color)
        elif type == 'mayavi':
            pass
        elif type == 'vispy':
            pass

    @staticmethod
    def get_points(path, num_features=3):
        return utils.get_points(path, num_features)

    @staticmethod
    def add_boxes(points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None, point_colors=None,
                  draw_origin=True, type='open3d'):
        if type == 'open3d':
            open3d_draw_scenes(
                points=points,
                gt_boxes=gt_boxes,
                ref_boxes=ref_boxes,
                ref_labels=ref_labels,
                ref_scores=ref_scores,
                point_colors=point_colors,
                draw_origin=draw_origin
            )
        elif type == 'qtopengl':
            pass
        elif type == 'mayavi':
            pass
        elif type == 'vispy':
            pass

    @staticmethod
    def pcd2bin(pcd_dir, bin_dir, num_features=4):
        utils.pcd2bin(pcd_dir, bin_dir, num_features)


if __name__ == '__main__':
    PointCloudProcess.show_pcd(path='data/example/example.pcd', type='qtopengl')
