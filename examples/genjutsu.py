"""Genjutsu Restyle example: restyle a source video with a style preset.

Genjutsu is Higgsfield's video-to-video model with three endpoints:
  higgsfield/genjutsu/restyle/v1.0          video_url + preset_id
  higgsfield/genjutsu/motion-transfer/v1.0  video_url + image_urls (1-8)
  higgsfield/genjutsu/object-swap/v1.0      video_url + image_urls (1-8)

Usage:
  export HF_KEY="your-api-key:your-api-secret"
  python examples/genjutsu.py --list-presets
  python examples/genjutsu.py [--video-url URL] [--preset NAME_OR_ID] [--resolution 480p]
"""

import argparse
import sys
import time
from datetime import datetime, timezone

import httpx

import higgsfield_client
from higgsfield_client.auth import get_credential_key

RESTYLE = 'higgsfield/genjutsu/restyle/v1.0'
PRESETS_URL = 'https://api.higgsfield.ai/models/higgsfield/genjutsu/restyle/v1.0/presets'
SAMPLE_VIDEO = (
    'https://d3snorpfx4xhv8.cloudfront.net/a4086dbb-d386-4bab-8efd-636d1f91e38e/'
    '59dac11e-bd99-4bc7-a627-2638e7ad9840.mp4'
)


def list_presets():
    """Presets can change, so fetch them instead of hardcoding ids."""
    response = httpx.get(
        PRESETS_URL,
        headers={'Authorization': f'Key {get_credential_key()}'},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()['items']  # [{'id', 'name', 'preview_url'}, ...]


def log(message):
    print(f'[{datetime.now(timezone.utc).isoformat(timespec="seconds")}] {message}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--list-presets', action='store_true', help='print restyle presets and exit')
    parser.add_argument('--video-url', default=SAMPLE_VIDEO, help='source video, at least 4 s (trimmed to 30 s)')
    parser.add_argument('--preset', default='Cel-Shaded CG Anime', help='preset name or id')
    parser.add_argument('--resolution', default='480p', choices=['480p', '720p', '1080p'])
    parser.add_argument('--prompt', default='Preserve the original movement and camera composition.')
    args = parser.parse_args()

    presets = list_presets()
    if args.list_presets:
        for preset in presets:
            print(f"{preset['id']}  {preset['name']}")
        return

    preset = next(p for p in presets if args.preset in (p['id'], p['name']))
    log(f"preset: {preset['name']} ({preset['id']})")

    started = time.monotonic()
    last_status = None

    def on_queue_update(status):
        nonlocal last_status
        name = type(status).__name__
        if name != last_status:
            last_status = name
            log(f'status: {name}')

    result = higgsfield_client.subscribe(
        RESTYLE,
        arguments={
            'video_url': args.video_url,
            'preset_id': preset['id'],
            'image_urls': [],  # optional character references (0-5); never None
            'prompt': args.prompt,
            'resolution': args.resolution,
        },
        on_enqueue=lambda request_id: log(f'request_id: {request_id}'),
        on_queue_update=on_queue_update,
    )

    log(f"status: {result['status']} after {time.monotonic() - started:.0f}s")
    if result.get('status') != 'completed':
        sys.exit(f'Genjutsu request did not complete: {result}')
    print(result['video']['url'])


if __name__ == '__main__':
    main()
