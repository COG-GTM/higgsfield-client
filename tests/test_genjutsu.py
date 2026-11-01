import json
import unittest
from functools import partial
from unittest.mock import patch

import httpx

from higgsfield_client.http.client import SyncClient

RESTYLE_ENDPOINT = 'higgsfield/genjutsu/restyle/v1.0'
RESTYLE_ARGUMENTS = {
    'video_url': 'https://example.com/input.mp4',
    'preset_id': 'c2143317-f28d-4c3c-a0b8-39bd547e08a7',
    'image_urls': [],
    'prompt': 'Preserve the original movement and camera composition.',
    'resolution': '720p',
}
MOTION_TRANSFER_ENDPOINT = 'higgsfield/genjutsu/motion-transfer/v1.0'
MOTION_TRANSFER_ARGUMENTS = {
    'video_url': 'https://example.com/dance.mp4',
    'image_urls': ['https://example.com/character.png'],
}


class GenjutsuSubscribeTest(unittest.TestCase):
    def subscribe(self, endpoint, arguments):
        calls = []
        request_id = 'f0b6c4f2-3c1e-4bd3-9d4f-2b5c1a8e9d10'
        status_url = f'https://api.higgsfield.ai/requests/{request_id}/status'
        video_url = 'https://cdn.example/output.mp4'

        def handle(request):
            calls.append(request)
            self.assertEqual(request.headers['Authorization'], 'Key test:secret')
            if request.method == 'POST':
                self.assertEqual(request.url.path, f'/{endpoint}')
                self.assertEqual(json.loads(request.content), arguments)
                return httpx.Response(200, json={
                    'status': 'queued',
                    'request_id': request_id,
                    'status_url': status_url,
                    'cancel_url': f'https://api.higgsfield.ai/requests/{request_id}/cancel',
                })

            self.assertEqual(str(request.url), status_url)
            return httpx.Response(200, json={
                'status': 'completed',
                'request_id': request_id,
                'video': {'url': video_url},
            })

        factory = partial(httpx.Client, transport=httpx.MockTransport(handle))
        with patch('higgsfield_client.http.client.httpx.Client', factory):
            client = SyncClient(api_key='test:secret')
            try:
                result = client.subscribe(endpoint, arguments=arguments)
            finally:
                client._client.close()

        self.assertEqual(result['video']['url'], video_url)
        self.assertEqual(calls[0].method, 'POST')
        self.assertEqual(str(calls[0].url), f'https://api.higgsfield.ai/{endpoint}')

    def test_restyle(self):
        self.subscribe(RESTYLE_ENDPOINT, RESTYLE_ARGUMENTS)

    def test_motion_transfer(self):
        self.subscribe(MOTION_TRANSFER_ENDPOINT, MOTION_TRANSFER_ARGUMENTS)

    def test_object_swap(self):
        self.subscribe('higgsfield/genjutsu/object-swap/v1.0', MOTION_TRANSFER_ARGUMENTS)
