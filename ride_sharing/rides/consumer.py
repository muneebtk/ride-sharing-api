from channels.generic.websocket import AsyncWebsocketConsumer
import json


class RideTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.ride_group_name = f"ride_{self.ride_id}"

        # Join ride group
        await self.channel_layer.group_add(self.ride_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave ride group
        await self.channel_layer.group_discard(self.ride_group_name, self.channel_name)

    async def send_location_update(self, event):
        # Send location update to WebSocket
        location = event["location"]
        await self.send(text_data=json.dumps(location))
