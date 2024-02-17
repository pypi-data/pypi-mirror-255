import base64
import io
import json
from pathlib import Path

import uvicorn
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


def fire(path_mp4: str, bbox_json: str):
    import cv2
    from tqdm import tqdm
    global annotation_path
    annotation_path = Path(bbox_json)

    with open(bbox_json) as f:
        bboxs = json.load(f)

    cap = cv2.VideoCapture(path_mp4)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    assert len(bboxs) == frame_count, \
        f'Expected bboxs count to be equal to frame count found {frame_count} frames and {len(bboxs)} bboxs'

    bar = tqdm(
        desc='Loading video',
        total=frame_count)

    for i, frame in enumerate(read_frames(cap)):
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

    print('Running on http://localhost:8000')

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning")


def main():
    from fire import Fire
    Fire(fire)
