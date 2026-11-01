"""Genjutsu example: restyle a video, then transfer its motion to a character.

Docs: https://docs.higgsfield.ai/docs/models/genjutsu
Reads HF_KEY or HF_API_KEY + HF_API_SECRET from the environment.
"""

import higgsfield_client

SOURCE_VIDEO = "https://example.com/input.mp4"  # 4-30 s; longer clips are trimmed to 30 s
CHARACTER_IMAGE = "https://example.com/character.png"

# Restyle keeps the source motion, composition and audio and changes the look.
# preset_id is a style UUID from
# GET https://api.higgsfield.ai/models/higgsfield/genjutsu/restyle/v1.0/presets
# ("Cel-Shaded CG Anime" below); fetch the catalog for the current list.
restyled = higgsfield_client.subscribe(
    "higgsfield/genjutsu/restyle/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,
        "preset_id": "c2143317-f28d-4c3c-a0b8-39bd547e08a7",
        "image_urls": [],  # optional character references, max 5
        "prompt": "Preserve the original movement and camera composition.",
        "resolution": "720p",  # 480p | 720p | 1080p
    },
    on_queue_update=lambda status: print(f"restyle: {status}"),
)
print("restyled video:", restyled["video"]["url"])

# Motion transfer drives the referenced character(s) with the source video's motion.
transferred = higgsfield_client.subscribe(
    "higgsfield/genjutsu/motion-transfer/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,
        "image_urls": [CHARACTER_IMAGE],  # 1-8 references
    },
)
print("motion-transferred video:", transferred["video"]["url"])

# Object swap replaces an object/character in the video with the referenced one.
swapped = higgsfield_client.subscribe(
    "higgsfield/genjutsu/object-swap/v1.0",
    arguments={
        "video_url": SOURCE_VIDEO,
        "image_urls": [CHARACTER_IMAGE],
        "prompt": "Swap the main subject for the referenced character.",
    },
)
print("object-swapped video:", swapped["video"]["url"])
