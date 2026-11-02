"""Genjutsu video-to-video example: motion transfer, object swap, restyle.

Docs: https://docs.higgsfield.ai/docs/models/genjutsu
Source videos must be 4+ seconds; anything past 30 seconds is trimmed.
"""

import httpx

import higgsfield_client
from higgsfield_client.auth import get_credential_key

SOURCE_VIDEO = "https://example.com/source.mp4"

# Motion transfer: animate the referenced character(s) with the source motion.
motion = higgsfield_client.subscribe(
    "higgsfield/genjutsu/motion-transfer/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,
        "image_urls": ["https://example.com/character.png"],  # 1-8 images
        "prompt": "Keep the camera locked off",
        "resolution": "720p",  # 480p | 720p (default) | 1080p
    },
)
print(motion)

# Object swap: replace an object (source needs >= 409,600 px per frame).
swap = higgsfield_client.subscribe(
    "higgsfield/genjutsu/object-swap/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,
        "image_urls": ["https://example.com/new-object.png"],  # 1-8 images
        "prompt": "Replace the mug with the red sneaker",
    },
)
print(swap)

# Restyle: preset_id must come from the live catalog. Never submit a preset
# name, index, preview URL, or a UUID copied from an example.
presets = (
    httpx.get(
        "https://api.higgsfield.ai/models/higgsfield/genjutsu/restyle/v1.0/presets",
        headers={"Authorization": f"Key {get_credential_key()}"},
    )
    .raise_for_status()
    .json()
)
for preset in presets["items"]:
    print(preset["id"], preset["name"])
preset_id = presets["items"][0]["id"]

restyle = higgsfield_client.subscribe(
    "higgsfield/genjutsu/restyle/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,  # <= 200 MiB, source audio is kept
        "preset_id": preset_id,
        "image_urls": [],  # optional, up to 5 character references
        "resolution": "1080p",
    },
)
print(restyle)
