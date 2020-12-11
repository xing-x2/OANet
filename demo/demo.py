#!/usr/bin/env python3
import os
import cv2
import numpy as np
from learnedmatcher import LearnedMatcher
from extract_sift import ExtractSIFT
from compare import find_ground_truth
import argparse
from match import show_matches

def draw_match(img1_path, img2_path, corr1, corr2):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    corr1 = [cv2.KeyPoint(corr1[i, 0], corr1[i, 1], 1) for i in range(corr1.shape[0])]
    corr2 = [cv2.KeyPoint(corr2[i, 0], corr2[i, 1], 1) for i in range(corr2.shape[0])]

    assert len(corr1) == len(corr2)

    draw_matches = [cv2.DMatch(i, i, 0) for i in range(len(corr1))]

    display = cv2.drawMatches(img1, corr1, img2, corr2, draw_matches, None,
                              matchColor=(0, 255, 0),
                              singlePointColor=(0, 0, 255),
                              flags=4
                              )
    return display


def main():
    """The main function."""
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--im2", required=True)
    opt = p.parse_args()
    if opt.name == "boat":
        ext = "pgm"
    else:
        ext = "ppm"
    path1 = "GT_pics/"+opt.name+"/imgs/img1."+ext
    path2 = "GT_pics/"+opt.name+"/imgs/img"+opt.im2+"."+ext
    gt_path = "ground_truth/"+opt.name+"/"+opt.name+"_1_"+opt.im2+"_TP.txt"
    print(path1, path2)


    model_path = os.path.join('../model', 'gl3d/sift-4000/model_best.pth')
    img1_name, img2_name = path1, path2

    detector = ExtractSIFT(8000, contrastThreshold=1e-5)
    lm = LearnedMatcher(model_path, inlier_threshold=1, use_ratio=0, use_mutual=0)
    kpt1, desc1 = detector.run(img1_name)
    kpt2, desc2 = detector.run(img2_name)
    _, corr1, corr2 = lm.infer([kpt1, kpt2], [desc1, desc2])
    K1 = [(corr1[i, 0], corr1[i, 1]) for i in range(corr1.shape[0])]
    K2 = [(corr2[i, 0], corr2[i, 1]) for i in range(corr2.shape[0])]
    k1 = np.array(K1)
    k2 = np.array(K2)
    print(k1.shape, k2.shape)
    true_pos, false_pos = find_ground_truth(k1, k2, gt_path)

    display = draw_match(img1_name, img2_name, corr1, corr2)
    cv2.imwrite(img1_name+"-"+img2_name+".png", display)

    cv2.imshow("display", display)
    cv2.waitKey()


if __name__ == "__main__":
    main()
