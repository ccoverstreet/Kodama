#!/usr/bin/env python
# Code stitched together from Websockets documentation example

import asyncio
from websockets.asyncio.server import serve
import json

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)


zero_offset = 0.05
left_offset = 0.04
right_offset = 0.05

def clamp(val, lower, upper):
    return min([max([val, lower]), upper])

async def echo(websocket):
    async for message in websocket:
        data = json.loads(message)
        print(data)

        kit.continuous_servo[12].throttle = clamp(
            left_offset + 1 * data["throttleMult"] * 0.5 * data["leftThrottle"],
            -1, 1)
        kit.continuous_servo[13].throttle = clamp(
            right_offset + -1 * data["throttleMult"] * 0.5 * data["rightThrottle"],
            -1, 1)

        kit.servo[14].angle = clamp(data["cameraTiltAngle"], 0, 180)
        kit._pca.channels[15].duty_cycle = 0xFFFF if data["lightOn"] else 0

        await websocket.send(message)


async def main():
    async with serve(echo, "", 30304) as server:
        await server.serve_forever()

asyncio.run(main())
