import datetime, json, higgsfield_client
def log(*a): print(datetime.datetime.utcnow().isoformat() + 'Z', *a, flush=True)
log('submitting via higgsfield_client.subscribe')
last = [None]
def upd(s):
    n = type(s).__name__
    if n != last[0]: log('status', n); last[0] = n
r = higgsfield_client.subscribe('higgsfield/genjutsu/restyle/v1.0', arguments={
  'video_url': 'https://d3snorpfx4xhv8.cloudfront.net/a4086dbb-d386-4bab-8efd-636d1f91e38e/59dac11e-bd99-4bc7-a627-2638e7ad9840.mp4',
  'preset_id': 'c2143317-f28d-4c3c-a0b8-39bd547e08a7', 'image_urls': [],
  'prompt': 'Preserve the original movement and camera composition.', 'resolution': '480p'},
  on_enqueue=lambda rid: log('request_id', rid), on_queue_update=upd)
log('result', json.dumps(r))
