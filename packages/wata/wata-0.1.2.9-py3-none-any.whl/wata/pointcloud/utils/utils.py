import numpy as np
from pathlib import Path
import os
from wata.pointcloud.utils.load_pcd import get_points_from_pcd_file
import tqdm
import glob
from wata.file.utils import utils as file

def cut_pcd(points, pcd_range):
    x_range = [pcd_range[0], pcd_range[3]]
    y_range = [pcd_range[1], pcd_range[4]]
    z_range = [pcd_range[2], pcd_range[5]]
    mask = (x_range[0] <= points[:, 0]) & (points[:, 0] <= x_range[1]) & (y_range[0] < points[:, 1]) & (
            points[:, 1] <= y_range[1]) & (z_range[0] < points[:, 2]) & (points[:, 2] <= z_range[1])
    points = points[mask]
    return points


def get_points(path, num_features):
    pcd_ext = Path(path).suffix
    if pcd_ext == '.bin':
        num_features = 4 if num_features is None else num_features
        points = np.fromfile(path, dtype=np.float32).reshape(-1, num_features)
    elif pcd_ext == ".npy":
        points = np.load(path)
    elif pcd_ext == ".pcd":
        num_features = 3 if num_features is None else num_features
        points = get_points_from_pcd_file(path, num_features=num_features)
    else:
        raise NameError("Unable to handle {} formatted files".format(pcd_ext))
    return points[:, 0:num_features]

def pcd2bin(pcd_dir, bin_dir, num_features=4):
    file.mkdir_if_not_exist(bin_dir)
    pcd_list = glob.glob(pcd_dir + "./*.pcd")
    for pcd_path in tqdm.tqdm(pcd_list):
        filename, _ = os.path.splitext(pcd_path)
        filename = filename.split("\\")[-1]
        points = get_points_from_pcd_file(pcd_path, num_features=num_features)
        points = points[:, 0:num_features].astype(np.float32)
        bin_file = os.path.join(bin_dir, filename) + '.bin'
        points.tofile(bin_file)
    print("==> The bin file has been saved in \"{}\"".format(bin_dir))
