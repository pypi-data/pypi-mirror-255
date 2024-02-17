import base64
import io
import json
from pathlib import Path
from typing import Iterable, List, Tuple

import cv2
import uvicorn
from cv2.typing import MatLike
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw
from pydantic import BaseModel

from dms_annotator.tools import read_frames

annotation_path = Path()
frames = []
marks = []
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        'http://localhost:5173'
    ],
)


class Mark(BaseModel):
    frame_id: int
    good: bool


def save_results():
    verified_path = f'{annotation_path}.verified.json'
    with open(verified_path, 'w') as f:
        json.dump(marks, f)

    print(f'Results were saved to {verified_path}')


@app.post("/mark")
async def mark_frame(mark: Mark):
    frame_id = mark.frame_id
    marks[frame_id] = mark.good
    last_frame_id = len(frames) - 1

    print('Marked', frame_id, mark.good)

    if frame_id < last_frame_id:
        return

    save_results()


@app.get("/frame/{frame_id}")
async def get_frame(frame_id: int):
    if frame_id >= len(frames):
        return None

    if frame_id == len(frames) - 1:
        save_results()

    return dict(
        total=len(frames),
        mark=marks[frame_id],
        base64=frames[frame_id])


app.mount(
    "/",
    name="static",
    app=StaticFiles(
        packages=[('dms_annotator', 'dist')],
        html=True))

BBox = Tuple[int, int, int, int]
Frame = MatLike


def load_frames(*, frms: Iterable[Frame], frame_count: int, bboxs: List[BBox]):

    from tqdm import tqdm

    bar = tqdm(
        desc='Loading frames',
        total=frame_count)

    for i, frame in enumerate(frms):
        bar.update()
        bar.refresh()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)

        bbox = bboxs[i]
        if bbox is not None:
            draw = ImageDraw.Draw(img)
            draw.rectangle(bboxs[i], outline='red', width=3)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')

        frames.append(base64.b64encode(buffer.getbuffer()).decode('utf-8'))
        marks.append(None)

    bar.close()


def load_frames_from_mp4(path_mp4: Path, bboxs: List[BBox]):
    cap = cv2.VideoCapture(str(path_mp4))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    load_frames(
        frms=read_frames(cap),
        frame_count=frame_count,
        bboxs=bboxs)


def load_frames_from_dir(path: Path, bboxs: List[BBox]):
    jpgs = sorted(list(path.glob('*.jpg')))
    load_frames(
        frms=(cv2.imread(str(jpg)) for jpg in jpgs),
        frame_count=len(jpgs),
        bboxs=bboxs)


def fire(path: str | Path, bbox_json: str):
    global annotation_path
    annotation_path = Path(bbox_json)

    with open(bbox_json) as f:
        bboxs = json.load(f)

    path = Path(path)
    assert path.exists(), f'Path {path} does not exist'

    if path.is_dir():
        load_frames_from_dir(path, bboxs)

    else:
        assert path.suffix == '.mp4', f'path must point to a mp4 file or a folder of jpgs found {path}'
        load_frames_from_mp4(path, bboxs)

    assert len(bboxs) == len(frames), \
        f'Expected bboxs count to be equal to frame count found {len(frames)} frames and {len(bboxs)} bboxs'

    print('Running on http://localhost:8000')

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning")


def main():
    from fire import Fire
    Fire(fire)
