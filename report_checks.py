# -*- coding: utf-8 -*-
"""Числа отчёта, которых photolab.py не печатает: сверка с эталонами кадров курса и HSV против RGB.

Запуск (после команд из REPORT.md, раздел 4):  python report_checks.py <путь к lectures репозитория курса>
"""
import os
import sys

import cv2
import numpy as np

import photolab as pl

BALL = (190, 560, 58)            # эталон мяча на ball-day / ball-lamp: центр и радиус (sample_data/README.md)
SAMPLE = (160, 530, 60, 60)      # прямоугольник на мяче, кадр ball-day
OBJ_SAMPLE = (820, 480, 420, 200)  # прямоугольник на хурме, data/object.jpg


def recall_precision(mask, gt):
    tp = float((mask & gt).sum())
    return round(100 * tp / gt.sum(), 1), round(100 * tp / max(mask.sum(), 1), 1)


def bgr_box_mask(img, pixels, margin=10, open_k=5, close_k=9):
    """То же, что hsv_box_from + color_mask, но ящик в BGR: процентили 1–99 ± margin по всем трём каналам."""
    lo = np.clip(np.floor(np.percentile(pixels, 1, axis=0) - margin), 0, 255)
    hi = np.clip(np.ceil(np.percentile(pixels, 99, axis=0) + margin), 0, 255)
    m = cv2.inRange(img, lo, hi)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_k, open_k)))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_k, close_k)))


def main(lectures):
    l3, l4 = os.path.join(lectures, "L03-color-histograms", "demo"), os.path.join(lectures, "L04-geometry", "demo")
    day, lamp = pl.imread(os.path.join(l3, "ball-day.jpg")), pl.imread(os.path.join(l3, "ball-lamp.jpg"))
    yy, xx = np.mgrid[:lamp.shape[0], :lamp.shape[1]]
    gt = (xx - BALL[0]) ** 2 + (yy - BALL[1]) ** 2 <= BALL[2] ** 2

    mask = pl.imread("out/course/ball_mask.png")[..., 0] > 0
    print("ball-lamp, out/course/ball_mask.png: recall %.1f %%, precision %.1f %%" % recall_precision(mask, gt))

    ink = lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) < 128   # noqa: E731
    front, ref = pl.imread("out/course/poster_front640.png"), pl.imread(os.path.join(l4, "poster-gt.png"))
    print("poster-angle → poster-gt.png: совпало %.1f %% пикселей" % (100 * (ink(front) == ink(ref)).mean()))

    # границы снимаем днём, применяем под лампой: что переживает смену света — HSV или BGR
    x, y, w, h = SAMPLE
    px = day[y:y + h, x:x + w].reshape(-1, 3)
    lo, hi = pl.hsv_box_from(px)
    for name, im in (("ball-day", day), ("ball-lamp", lamp)):
        lc = pl.largest_component(pl.color_mask(im, lo, hi))
        print("%s, HSV-ящик с ball-day: recall %.1f %%, precision %.1f %%" % ((name,) + recall_precision(lc[0] > 0, gt)))
        print("%s, BGR-ящик с ball-day: recall %.1f %%, precision %.1f %%" % ((name,) + recall_precision(bgr_box_mask(im, px) > 0, gt)))

    obj = pl.imread("data/object.jpg")
    x, y, w, h = OBJ_SAMPLE
    hsv_mask = pl.imread("out/object_mask.png")[..., 0] > 0
    lc = pl.largest_component(bgr_box_mask(obj, obj[y:y + h, x:x + w].reshape(-1, 3)))
    rgb_mask = lc[0] > 0
    print("data/object.jpg: площадь HSV %d px, BGR %d px, BGR покрывает %.1f %% маски HSV"
          % (hsv_mask.sum(), rgb_mask.sum(), 100.0 * (rgb_mask & hsv_mask).sum() / hsv_mask.sum()))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
    if len(sys.argv) != 2:
        raise SystemExit("usage: python report_checks.py <путь к lectures репозитория курса>")
    main(sys.argv[1])
