# Standard library imports
import os, sys, requests, ast 
from pathlib import Path
from time import time

# Third-party imports
import cv2
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numba as nb
import numpy as np
import torch
import math
import tifffile
import json
import piexif
import piexif.helper
from tqdm import tqdm
from numba.extending import overload, register_jitable
from skimage.measure import regionprops
from PIL import Image
from PIL.PngImagePlugin import PngInfo



def save_dictionary(filepath, new_data):
    filepath = Path(filepath).absolute()
    try:
        existing_metadata = load_dictionary(filepath)
    except KeyError:
        existing_metadata = {}

    if existing_metadata is None:
        existing_metadata = {}

    existing_metadata.update(new_data)

    metadata_json = json.dumps(existing_metadata)
    img = Image.open(filepath)

    if filepath.suffix == '.png':
        pnginfo = PngInfo()
        pnginfo.add_text("metadata", metadata_json)
        img.save(filepath.as_posix(), pnginfo=pnginfo)

    elif filepath.suffix in {'.tif', '.tiff'}:
        with tifffile.TiffFile(filepath.as_posix()) as tif:
            data = tif.asarray()
        with tifffile.TiffWriter(filepath.as_posix(), bigtiff=False) as tif_writer:
            tif_writer.write(data, description=metadata_json)

    elif filepath.suffix in {'.jpg', '.jpeg'}:
        exif_ifd = {piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(metadata_json)}
        exif_dict = {"Exif": exif_ifd}
        exif_bytes = piexif.dump(exif_dict)
        img.save(filepath.as_posix(), exif=exif_bytes)


def load_dictionary(filepath):
    filepath = Path(filepath).absolute()
    if filepath.suffix == '.png':
        img = Image.open(filepath.as_posix())

        metadata_json = img.info.get("metadata", None)
        if metadata_json is not None:
            metadata = json.loads(metadata_json)
            return metadata
        else:
            return None

    elif filepath.suffix in {'.tiff', '.tif'}:
        with tifffile.TiffFile(filepath.as_posix()) as tif:
            metadata = tif.pages[0].tags['ImageDescription'].value
            if type(metadata) == str:
                metadata = ast.literal_eval(metadata)
        return metadata

    elif filepath.suffix in {'.jpg', '.jpeg'}:
        im = piexif.load(filepath.as_posix())
        try:
            metadata = piexif.helper.UserComment.load(im["Exif"][piexif.ExifIFD.UserComment])
            if type(metadata) == str:
                metadata = ast.literal_eval(metadata)
            return metadata
        except:
            return None


def plot_images(filepaths):
    n = len(filepaths)
    columns = min(n, 3)
    rows = n // 3 + int(n % 3 != 0)

    fig, axes = plt.subplots(rows, columns, figsize=(5 * columns, 5 * rows))
    if n > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for ax, filepath in zip(axes, filepaths):
        img = mpimg.imread(filepath)
        ax.imshow(img, cmap='gray')
        ax.set_title(f"filepath = '{filepath}'", fontsize=8)
        ax.axis('off')

    if n > 3:
        for i in range(n, len(axes)):
            axes[i].axis('off')

    plt.tight_layout()
    plt.show()



def process_filepath(filepath):
    if type(filepath) == str:
        filepath = Path(filepath).absolute()

        if filepath.is_file():
            if filepath.suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}:
                list_of_images = [filepath.as_posix()]
            else:
                print('Error: File must be .png, .jpg, .jpeg, .tif or .tiff')
                return None
        elif filepath.is_dir():
            folder_content = [filepath / filename for filename in os.listdir(filepath)]
            list_of_images = [filename.as_posix() for filename in folder_content
                              if filename.suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}]
        else:
            print('Error: The string did not contain a path to a folder or an image.')

    elif type(filepath) == list:
        for filename in filepath:
            if not Path(filename).is_file():
                print(f'Error: Not all list entries are valid filenames. \nThe issue is: {Path(filename).as_posix()} \nINFO: Folder paths should be given as a string, not a list.')
                return None
        list_of_images = [Path(filename).absolute().as_posix() for filename in filepath
                          if Path(filename).suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}]
    else:
        print('Unexpected error')
        return None

    return list_of_images


def load_image(filepath):
    if Path(filepath).suffix in {'.tif', '.tiff'}:
        im = tifffile.imread(filepath)
        im_shift_to_zero = im - im.min()
        im_max = im_shift_to_zero.max()
        im_normalized = im_shift_to_zero / im_max
        im_max_255 = im_normalized * 255
        im_8bit = im_max_255.astype('uint8')
        im_RGB = np.dstack([im_8bit] * 3)
    elif Path(filepath).suffix in {'.png', '.jpg', '.jpeg',}:
        im = cv2.imread(filepath)
        im_RGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im_RGB


def make_randomized_cmap(cmap='viridis', seed=42):
    '''Genarates randomized colormap with the first color being black'''
    cmap = matplotlib.colormaps[cmap]
    cmap_colors = cmap(np.linspace(0, 1, 2000))
    black_color = np.array([0, 0, 0, 1])
    cmap_rest_colors = cmap_colors[1:, :]
    np.random.seed(seed)
    np.random.shuffle(cmap_rest_colors)
    randomized_cmap = matplotlib.colors.ListedColormap(np.vstack((np.expand_dims(black_color, 0), cmap_rest_colors)))
    return randomized_cmap


def preprocess(filepath, crop_and_enlarge=False, invert=False, double=False):
    image = load_image(filepath)
    files_folder = Path(filepath).parent / (Path(filepath).stem + '_files')
    filename = Path(filepath).stem
    if invert and crop_and_enlarge is False:
        image = cv2.bitwise_not(image)
        filename += '_inverted.png'
        if double:
            filenames = [(files_folder / filename).as_posix(), filepath]
            return filenames

    if crop_and_enlarge:
        imshapex = image.shape[0]
        imshapey = image.shape[1]

        crop1 = np.kron(image[:int((imshapex / 2) * 1.25), : int((imshapey / 2) * 1.25), :], np.ones((2, 2, 1)))
        crop2 = np.kron(image[math.ceil((imshapex / 2) * 0.75):, :int((imshapey / 2) * 1.25), :], np.ones((2, 2, 1)))
        crop3 = np.kron(image[:int((imshapex / 2) * 1.25), math.ceil((imshapey / 2) * 0.75):, :], np.ones((2, 2, 1)))
        crop4 = np.kron(image[math.ceil((imshapex / 2) * 0.75):, math.ceil((imshapey / 2) * 0.75):, :], np.ones((2, 2, 1)))
        images = [crop1, crop2, crop3, crop4]
        filenames = [filename + '_crop' + str(number) + '.png' for number in [1, 2, 3, 4]]
        if invert:
            image_ = cv2.bitwise_not(image)
            filename_ = filename + '_inverted.png'
            cv2.imwrite((files_folder / filename_).as_posix(), image_)
    else:
        filenames = [filename + '.png']
        images = [image]

    for image, filename in zip(images, filenames):
        cv2.imwrite((files_folder / filename).as_posix(), image)

    return [(files_folder / filename).as_posix() for filename in filenames]


def find_array_of_bboxes_and_rearrange_masks(filepath, image_filepaths, double):
    files_folder = Path(image_filepaths[0]).parent
    image = load_image(filepath)

    for image_filepath in image_filepaths:
        file_p = files_folder / (Path(image_filepath).stem + '_array_of_masks.npz')
        array_of_masks = np.load(file_p)['array']
        os.remove(file_p)
        list_of_bbox = []
        for mask in np.moveaxis(array_of_masks, -1, 0):
            if mask.sum() > 0:
                list_of_bbox.append(regionprops(mask.astype('uint16'))[0]['bbox'])
        imx = image.shape[0]
        imy = image.shape[1]
        dx = 2 * math.ceil(imx / 2 * 0.75)
        dy = 2 * math.ceil(imy / 2 * 0.75)

        list_of_bbox2 = []
        list_of_rearranged_masks = []
        for bbox, mask in zip(list_of_bbox, np.moveaxis(array_of_masks, -1, 0)):

            x_min = bbox[0]
            y_min = bbox[1]
            x_max = bbox[2]
            y_max = bbox[3]
            if image_filepath[-5] in {'2', '4'}:
                x_min += dx
                x_max += dx
            if image_filepath[-5] in {'3', '4'}:
                y_min += dy
                y_max += dy
            list_of_bbox2.append([x_min, y_min, x_max, y_max])

            new_mask = np.zeros((imx * 2, imy * 2))
            if image_filepath[-5] == '1':
                new_mask[:mask.shape[0], :mask.shape[1]] = mask
            if image_filepath[-5] == '2':
                new_mask[-mask.shape[0]:, :mask.shape[1]] = mask
            if image_filepath[-5] == '3':
                new_mask[:mask.shape[0], -mask.shape[1]:] = mask
            if image_filepath[-5] == '4':
                new_mask[-mask.shape[0]:, -mask.shape[1]:] = mask

            if double:
                list_of_rearranged_masks.append(mask)
            else:
                list_of_rearranged_masks.append(new_mask)

        array_of_masks = np.stack(list_of_rearranged_masks, axis=-1)
        file_p = files_folder / (Path(image_filepath).stem + '_array_of_masks_rearranged.npz')
        np.savez_compressed(file_p, array=array_of_masks)
        array_of_bbox = np.array(list_of_bbox2)
        file_p = files_folder / (Path(image_filepath).stem + '_array_of_bbox.npz')
        np.savez_compressed(file_p, array=array_of_bbox)



def bb_iou(boxA, boxB):
    xA = np.maximum(boxA[0], boxB[0])
    yA = np.maximum(boxA[1], boxB[1])
    xB = np.minimum(boxA[2], boxB[2])
    yB = np.minimum(boxA[3], boxB[3])

    interArea = np.maximum(0, xB - xA) * np.maximum(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / (boxAArea + boxBArea - interArea)
    return iou


def split_list(to_keep, split_conditions):
    start = 0
    result = []
    for split in split_conditions:
        while split not in to_keep:
            split += 1
        idx = to_keep.index(split)
        result.append(to_keep[start:idx])
        start = idx
    result.append(to_keep[start:])
    return result


def remove_overlapping_bb(image_filepaths, iou_threshold=0.9):
    files_folder = Path(image_filepaths[0]).parent
    all_bboxes = []
    all_masks = []

    # Load bounding boxes from .npz files
    for image_filepath in image_filepaths:
        bboxes = np.load(files_folder / (Path(image_filepath).stem + '_array_of_bbox.npz'))['array']
        all_bboxes.append(bboxes)
        array_of_masks = np.load(files_folder / (Path(image_filepath).stem + '_array_of_masks_rearranged.npz'))['array']
        for mask in np.moveaxis(array_of_masks, -1, 0):
            all_masks.append(mask)
        os.remove(files_folder / (Path(image_filepath).stem + '_array_of_bbox.npz'))
        os.remove(files_folder / (Path(image_filepath).stem + '_array_of_masks_rearranged.npz'))
 
    all_bboxes = np.vstack(all_bboxes)

    all_masks = np.stack(all_masks, axis=-1)

    # This will store the indices of the bboxes to keep
    to_keep = []
    for i, boxA in enumerate(all_bboxes):
        keep = True
        for j, boxB in enumerate(all_bboxes):
            if i != j:
                iou = bb_iou(boxA, boxB)
                if iou >= iou_threshold:
                    if i not in to_keep and j not in to_keep:
                        to_keep.append(i)
                    keep = False
                    break
        if keep:
            to_keep.append(i)

    unique_bboxes = all_bboxes[to_keep]
    unique_masks = all_masks[:, :, to_keep]

    print(f'{len(all_bboxes) - len(unique_bboxes)} masks have been removed because they were indentical.')
    return unique_masks


def bin_masks(filepath, unique_masks, binning=True):
    files_folder = Path(filepath).parent / (Path(filepath).stem + '_files')
    if binning:
        if unique_masks.shape[0] % 2 or unique_masks.shape[1] % 2:
            raise ValueError("The first and second dimensions of the array must be even for 2x2 binning.")

        # Define new shape and strides for the view that groups elements into 2x2 blocks
        new_shape = (unique_masks.shape[0] // 2, unique_masks.shape[1] // 2, 2, 2, unique_masks.shape[2])
        new_strides = (unique_masks.strides[0] * 2, unique_masks.strides[1] * 2) + unique_masks.strides

        # Create a strided array of 2x2 blocks
        strided = np.lib.stride_tricks.as_strided(unique_masks, shape=new_shape, strides=new_strides)

        # Perform logical OR on the blocks across the last two dimensions which are the original 2x2
        binned = np.logical_or.reduce(strided, axis=(2, 3))

        np.savez_compressed(files_folder / (Path(filepath).stem + '_array_of_masks.npz'), array=binned.astype(int))
        print(f'An array with shape {binned.astype(int).shape} has been saved.')

    else:
        np.savez_compressed(files_folder / (Path(filepath).stem + '_array_of_masks.npz'), array=unique_masks)
        print(f'An array with shape {unique_masks.shape} has been saved.')


def stitch_crops_together(filepath, image_filepaths_raw, iou_threshold=0.8, double=False):
    image_filepaths = []
    for image_filepath in image_filepaths_raw:
        if Path(image_filepath.replace('.png', '_array_of_masks.npz')).is_file() or double:
            image_filepaths.append(image_filepath)

    print('img1',image_filepaths)
    print('Finding bounding boxes and rearranging masks.', end=' ')
    find_array_of_bboxes_and_rearrange_masks(filepath, image_filepaths, double)
    print('Done.')
    print('Removing masks with identical bounding boxes.')
    unique_masks = remove_overlapping_bb(image_filepaths, iou_threshold=iou_threshold)
    print('Done.')
    print('Creating the final array of masks.')

    bin_masks(filepath, unique_masks, binning=not double)



def format_time(elapsed_time):
    minutes, seconds = divmod(elapsed_time, 60)
    time_string = ""
    if minutes >= 1:
        minute_label = "minute" if minutes == 1 else "minutes"
        time_string += f"{int(minutes)} {minute_label} and "
    second_label = "second" if seconds == 1 else "seconds"
    time_string += f"{round(seconds)} {second_label}"
    return time_string


def download_weights(model):
    weights = {
        'huge': ['https://osf.io/download/65b0d08399d01005546266f2/', 'sam_vit_h_4b8939.pth'],
        'large': ['https://osf.io/download/65b0d0624aa63c05c2df18f4/', 'sam_vit_l_0b3195.pth'],
        'base': ['https://osf.io/download/k6ce8/', 'sam_vit_b_01ec64.pth'],
        'fast': ['https://osf.io/download/p7kmb/', 'FastSAM.pt']
    }
    directory = os.path.dirname(__file__)

    if not os.path.exists(directory):
        print('NP-SAM is not correctly installed')
        return

    file_path = os.path.join(directory, weights.get(model)[1])
    try:
        response = requests.get(weights.get(model)[0], stream=True)
        response.raise_for_status()

        total_length = int(response.headers.get('content-length', 0))

        with open(file_path, 'wb') as file, tqdm(
                desc=weights.get(model)[1], total=total_length, unit='iB', unit_scale=True,
                unit_divisor=1024, file=sys.stdout, colour='GREEN', dynamic_ncols=True,
                smoothing=0.1) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        print(f"File downloaded successfully: {file_path}")
    except requests.RequestException as e:
        print(f"Failed to download {weights.get(model)[1]}: {e}")


def choose_SAM_model(SAM_model, device):
    model_mapping = {'a': 'auto',
                     'f': 'fast', 'fastsam': 'fast',
                     'b': 'base',
                     'l': 'large',
                     'h': 'huge'
                     }
    SAM_model = SAM_model.lower()
    SAM_model = model_mapping.get(SAM_model, SAM_model)

    directory = Path(os.path.dirname(__file__))
    available_SAM_models = [fname.name for fname in directory.glob('*.pt*') if fname.is_file()]

    model_info = {'fast': ['fast', 'FastSAM.pt', '144 MB'],
                   'base': ['vit_b', 'sam_vit_b_01ec64.pth', '366 MB'],
                   'large': ['vit_l', 'sam_vit_l_0b3195.pth', '1.2 GB'],
                   'huge': ['vit_h', 'sam_vit_h_4b8939.pth', '2.5 GB']}

    if SAM_model == 'auto':
        if device == 'cpu':
            model = 'fast'
        elif device == 'cuda':
            model = 'base'
            if torch.cuda.get_device_properties(0).total_memory / 1024 ** 3 > 4:
                model = 'huge'
    elif SAM_model in {'fast', 'base', 'large', 'huge'}:
        model = SAM_model
    else:
        print("Invalid input. Valid inputs are 'a' for auto, 'h' for huge, 'l' for large, 'b' for base and 'f' for fast.")
        return None

    if model_info.get(model)[1] in available_SAM_models:
        print(f'The {model} SAM weight ({model_info.get(model)[1]}) were chosen.')
        return directory / model_info.get(model)[1], model_info.get(model)[0], model
    else:
        ask_for_download = input(f'SAM weights were not found. This is probably because it is the first time running '
                                 f'NP-SAM with this option.\n\nDo you want to download the {model} weights file (size: {model_info.get(model)[2]})? y/n: ')
        if ask_for_download.lower() == 'y':
            download_weights(model)
            return directory / model_info.get(model)[1], model_info.get(model)[0], model
        else:
            print("NP-SAM can't run without the weights. Set the keyword argument SAM_model to either "
                  "'a' for auto, 'h' for huge, 'l' for large, 'b' for base or 'f' for fast.")
            return None


@overload(np.all)
def np_all(x, axis=None):
    # ndarray.all with axis arguments for 2D arrays.
    @register_jitable
    def _np_all_axis0(arr):
        out = np.logical_and(arr[0], arr[1])
        for v in iter(arr[2:]):
            for idx, v_2 in enumerate(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    @register_jitable
    def _np_all_axis1(arr):
        out = np.logical_and(arr[:, 0], arr[:, 1])
        for idx, v in enumerate(arr[:, 2:]):
            for v_2 in iter(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    def _np_all_impl(x, axis=None):
        if axis == 0:
            return _np_all_axis0(x)
        else:
            return _np_all_axis1(x)

    return _np_all_impl


@nb.njit(cache=True)
def nb_unique_caller(input_data):
    '''Numba compatible solution to numpy.unique() function'''

    data = input_data.copy()

    for i in range(data.shape[1] - 1, -1, -1):
        sorter = data[:, i].argsort(kind="mergesort")
        # mergesort to keep associations
        data = data[sorter]

    idx = [0]

    bool_idx = ~np.all((data[:-1] == data[1:]), axis=1)
    additional_uniques = np.nonzero(bool_idx)[0] + 1

    idx = np.append(idx, additional_uniques)

    return data[idx]
