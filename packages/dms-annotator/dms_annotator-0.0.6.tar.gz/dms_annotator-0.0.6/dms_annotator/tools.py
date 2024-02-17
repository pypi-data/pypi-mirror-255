import json

import cv2
from cv2 import VideoCapture
from tqdm import tqdm
from ultralight import UltraLightDetector


def read_frames(cap: VideoCapture):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        yield frame


def annotate(path_mp4):
    detector = UltraLightDetector()
    cap = cv2.VideoCapture(path_mp4)
    bar = tqdm(
        desc='Loading video',
        total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))

    frames = []
    for frame in read_frames(cap):
        boxes, _ = detector.detect_one(frame)
        bar.update()
        bar.refresh()
        frames.append(None if len(boxes) == 0 else boxes[0].tolist())

    bar.close()
    with open(f'{path_mp4}.face.json', 'w') as f:
        json.dump(frames, f)


def main():
    from fire import Fire
    Fire(annotate)
