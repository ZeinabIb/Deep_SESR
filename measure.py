"""
# > Script for measuring quantitative performances in terms of
#    - Structural Similarity Metric (SSIM) 
#    - Peak Signal to Noise Ratio (PSNR)
#    - Underwater Image Quality Measure (UIQM)
# Maintainer: Jahid (email: islam034@umn.edu)
# Interactive Robotics and Vision Lab (http://irvlab.cs.umn.edu/)
"""

## python libs
import os
import numpy as np
from glob import glob
from os.path import join
from ntpath import basename
from PIL import Image

## local libs
from utils.uiqm_utils import getUIQM
from utils.ssm_psnr_utils import getSSIM, getPSNR


# measurement in a common dimension
im_w, im_h = 320, 240

## data paths

# UFO
# REAL_im_dir = "data/sample_test_ufo/lrd/"  # real/input im-dir with {f.ext}
# # GEN_im_dir = "data/output/keras_out/"  # generated im-dir with {f_SESR/EN.ext}
# GTr_im_dir = "data/sample_test_ufo/hr/"  # ground truth im-dir with {f.ext}
# GEN_im_dir = "data/output/tf_out/"

# USR
REAL_im_dir = "data_usr/sample_test_usr/lrd/"  # real/input im-dir with {f.ext}
# GEN_im_dir = "data/output/keras_out/"  # generated im-dir with {f_SESR/EN.ext}
GTr_im_dir = "data_usr/sample_test_usr/hr/"  # ground truth im-dir with {f.ext}
GEN_im_dir = "data_usr/output/tf_out/"


## mesures uqim for all images in a directory
def measure_UIQMs(dir_name, file_ext=None):
    """
    # measured in RGB
    Assumes:
      * dir_name contain generated imagesa
      * to evaluate on all images: file_ext = None
      * to evaluate images that ends with "_SESR.png" or "_En.png"
          * use file_ext = "_SESR.png" or "_En.png"
    """
    paths = sorted(glob(join(dir_name, "*.*")))
    if file_ext:
        paths = [p for p in paths if p.endswith(file_ext)]
    uqims = []
    for img_path in paths:
        im = Image.open(img_path).resize((im_w, im_h))

        uqims.append(getUIQM(np.array(im)))
    return np.array(uqims)


def measure_SSIM(gtr_dir, gen_dir):
    """
    # measured in RGB
    Assumes:
      * gtr_dir contains ground-truths {filename.ext}
      * gen_dir contains generated images {filename_SESR.png}
    """
    gtr_paths = sorted(glob(join(gtr_dir, "*.*")))
    gen_paths = sorted(glob(join(gen_dir, "*.*")))
    # Normalize gen_paths
    gen_paths = [os.path.normpath(p) for p in gen_paths]

    ssims = []
    for gtr_path in gtr_paths:
        fname = basename(gtr_path).split(".")[0]

        # Dynamically generate the gen_path based on fname
        gen_path = os.path.normpath(join(gen_dir, fname + "_En.png"))

        # print(f"Generated gen_path: {gen_path}")
        # print(f"Available gen_paths: {gen_paths}")

        if gen_path in gen_paths:

            r_im = Image.open(gtr_path).resize((im_w, im_h))
            g_im = Image.open(gen_path).resize((im_w, im_h))
            # get SSIM on RGB channels (SOTA norm)
            ssim = getSSIM(np.array(r_im), np.array(g_im))

            ssims.append(ssim)
            # print(f"SSIMs inside if : {ssims}")

    return np.array(ssims)


def measure_PSNR(gtr_dir, gen_dir):
    """
    Measured in lightness channel.
    Assumes:
      * gtr_dir contains ground-truths {filename.ext}
      * gen_dir contains generated images {filename_SESR.png}
    """
    gtr_paths = sorted(glob(join(gtr_dir, "*.*")))
    gen_paths = sorted(glob(join(gen_dir, "*.*")))

    # Normalize and convert to absolute paths
    gen_paths = [os.path.abspath(os.path.normpath(p)) for p in gen_paths]

    psnrs = []
    for gtr_path in gtr_paths:
        fname = basename(gtr_path).split(".")[0]
        gen_path = os.path.abspath(
            os.path.normpath(join(gen_dir, fname + "_SESR.png"))
        )  # Normalize and make absolute

        # Print the expected paths for debugging
        # print(f"Ground Truth Path: {gtr_path}, Generated Path: {gen_path}")

        if gen_path in gen_paths:
            r_im = Image.open(gtr_path).resize((im_w, im_h))
            g_im = Image.open(gen_path).resize((im_w, im_h))

            # Get PSNR on the L channel (SOTA norm)
            r_im = r_im.convert("L")
            g_im = g_im.convert("L")
            psnr = getPSNR(np.array(r_im), np.array(g_im))
            psnrs.append(psnr)
        else:
            print(f"Generated image not found for {fname}")

    return np.array(psnrs)


### compute SSIM and PSNR
SSIM_measures = measure_SSIM(GTr_im_dir, GEN_im_dir)
if SSIM_measures.size > 0:
    print(f"SSIM_measures : {SSIM_measures}")
    print(
        "SSIM >> Mean: {0} std: {1}".format(
            np.mean(SSIM_measures), np.std(SSIM_measures)
        )
    )
else:
    print("SSIM measures are empty. Cannot compute mean and std.")

PSNR_measures = measure_PSNR(GTr_im_dir, GEN_im_dir)
if PSNR_measures.size > 0:
    print(
        "PSNR >> Mean: {0} std: {1}".format(
            np.mean(PSNR_measures), np.std(PSNR_measures)
        )
    )
else:
    print("PSNR measures are empty. Cannot compute mean and std.")

### compute and compare UIQMs
gen_uqims = measure_UIQMs(GEN_im_dir, file_ext="_En.png")  # or file_ext="_SESR.png"
if gen_uqims.size > 0:
    print(
        "Generated UQIM >> Mean: {0} std: {1}".format(
            np.mean(gen_uqims), np.std(gen_uqims)
        )
    )
else:
    print("UQIM measures are empty. Cannot compute mean and std.")
