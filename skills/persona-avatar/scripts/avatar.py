#!/usr/bin/env python3
"""
avatar.py — generate a persona's profile photo and a short talking-head intro video
through OpenRouter. Standard library only.

  image  --prompt "<description>" --out avatar.png [--reference frame.jpg]
  video  --image avatar.png --line "<what they say>" --speaker "<who they are>" --out intro.mp4

Needs OPENROUTER_API_KEY (env var, or a .env file in the working directory).
Models default to a cheap image model and a cheap image-to-video model with audio;
override with --model. Video jobs take a minute or two and cost roughly $0.30 for 6s.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://openrouter.ai/api/v1"
IMAGE_MODEL = "google/gemini-2.5-flash-image"
VIDEO_MODEL = "google/veo-3.1-lite"
PHOTO_STYLE = (
    "The photo should be framed like a Zoom call or video conference - showing the person from "
    "shoulders up, looking at the camera in a conversational pose, centered, with natural lighting, "
    "as if they're on a video call. Photorealistic style. Just the camera image, full frame: no "
    "on-screen interface, buttons, borders or text."
)


def load_api_key() -> str:
    """The project's .env wins over the shell, so the key saved for this project is the one used."""
    key = os.environ.get("OPENROUTER_API_KEY")
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "OPENROUTER_API_KEY": key = value.strip().strip("\"'")
    if not key: sys.exit("OPENROUTER_API_KEY not set. Get one at https://openrouter.ai/keys and put it in .env")
    return key


def request(method: str, path: str, key: str, body: dict | None = None) -> bytes:
    req = urllib.request.Request(f"{API}{path}", method=method, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, data=json.dumps(body).encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp: return resp.read()
    except urllib.error.HTTPError as err:
        sys.exit(f"OpenRouter {err.code}: {err.read().decode(errors='replace')[:800]}")


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def make_image(args, key: str) -> None:
    content = [{"type": "text", "text": f"A professional webcam or video call profile photo showing: {args.prompt}\n\n{PHOTO_STYLE}"}]
    if args.reference: content.append({"type": "image_url", "image_url": {"url": data_url(Path(args.reference))}})
    body = {"model": args.model or IMAGE_MODEL, "modalities": ["image", "text"], "messages": [{"role": "user", "content": content}], "image_config": {"aspect_ratio": "16:9"}}
    message = json.loads(request("POST", "/chat/completions", key, body))["choices"][0]["message"]
    images = message.get("images") or []
    if not images: sys.exit(f"No image returned. Model said: {message.get('content')!r}")
    _, _, encoded = images[0]["image_url"]["url"].partition("base64,")
    Path(args.out).write_bytes(base64.b64decode(encoded))
    print(args.out)


def make_video(args, key: str) -> None:
    prompt = f'{args.speaker} says this to the camera with an appropriate accent and natural mannerisms: "{args.line}"'
    body = {
        "model": args.model or VIDEO_MODEL, "prompt": prompt,
        "duration": args.duration, "resolution": "720p", "aspect_ratio": "16:9", "generate_audio": True,
        "frame_images": [{"type": "image_url", "image_url": {"url": data_url(Path(args.image))}, "frame_type": "first_frame"}],
    }
    job = json.loads(request("POST", "/videos", key, body))
    print(f"video job {job['id']} submitted", file=sys.stderr)
    deadline = time.time() + 15 * 60
    while job["status"] not in ("completed", "failed", "cancelled", "expired"):
        if time.time() > deadline: sys.exit(f"Timed out; job {job['id']} is still {job['status']}")
        time.sleep(15)
        job = json.loads(request("GET", f"/videos/{job['id']}", key))
        print(f"  {job['status']}", file=sys.stderr)
    if job["status"] != "completed": sys.exit(f"Video job {job['status']}: {json.dumps(job)[:800]}")
    Path(args.out).write_bytes(request("GET", f"/videos/{job['id']}/content?index=0", key))
    cost = (job.get("usage") or {}).get("cost")
    print(args.out + (f"  (cost ${cost})" if cost is not None else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    image = sub.add_parser("image", help="generate a profile photo")
    image.add_argument("--prompt", required=True, help="physical description of the person and their setting")
    image.add_argument("--reference", help="optional photo or video frame to base the likeness on")
    image.add_argument("--out", required=True)
    image.add_argument("--model")
    video = sub.add_parser("video", help="animate a profile photo into a short talking-head clip")
    video.add_argument("--image", required=True)
    video.add_argument("--line", required=True, help="what they say, ~10-15 words")
    video.add_argument("--speaker", required=True, help='e.g. "A 34-year-old man from Vancouver, Canada"')
    video.add_argument("--duration", type=int, default=6)
    video.add_argument("--out", required=True)
    video.add_argument("--model")
    args = parser.parse_args()
    key = load_api_key()
    make_image(args, key) if args.command == "image" else make_video(args, key)


if __name__ == "__main__":
    main()
