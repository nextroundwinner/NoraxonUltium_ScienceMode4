"""
Provides an example how to use Noraxon Ultium EMG sensor (https://www.noraxon.com/our-products/ultium-emg)
in combination with a HASOMED Science P24 (https://github.com/ScienceMode/ScienceMode4_P24)

It uses Lab Streaming Layer (LSL) to read data from EMG sensor and adjust stimulation accordingly.
"""

import asyncio
from enum import IntEnum
import argparse

from pylsl import resolve_byprop, StreamInlet
import science_mode_4 as sm4


class Muscles(IntEnum):
    """Muscles, each one is attached to a channel"""
    FLEXOR_DIGITORUM = 0
    EXTENSOR_DIGITORUM = 1


class Stimulator:
    """Represents a P24 device"""

    def __init__(self, com_port: str, inlet: StreamInlet):
        self.com_port = com_port

        self.inlet = inlet
        self.current = 50
        self.last_active_muscles: set[Muscles] = {}


    async def handle_communication(self):
        """Handles communication with P24 device"""
        try:
            # disable ScienceMode logging
            sm4.logger().disabled = True
            # create serial port connection
            connection = None
            # if no com port was passed, auto detect a ScienceMode device
            if self.com_port is None:
                port = sm4.SerialPortConnection.list_science_mode_device_ports()[0]
                connection = sm4.SerialPortConnection(port.device)
            else:
                connection = sm4.SerialPortConnection(self.com_port)
            # open connection, now we can read and write data
            connection.open()

            # create science mode device
            device = sm4.DeviceP24(connection)
            # call initialize to get basic information (serial, versions) and stop any
            # active stimulation/measurement to have a defined state
            await device.initialize()

            # get mid level layer to call mid level commands
            mid_level = device.get_layer_mid_level()
            # call init mid level, we want to stop on all stimulation errors
            await mid_level.init(True)
            # start stimulation
            await self.update(mid_level, 0)

            last_emg_value = 0
            last_get_current_data_timestamp = None
            while True:

                # get new sample from LSL stream
                sample, timestamp = self.inlet.pull_sample()

                # simple moving average filter of emg signal
                new_emg_value = sample[0]
                new_emg_value = abs(new_emg_value)
                new_emg_value = 0.8 * last_emg_value + 0.2 * new_emg_value
                last_emg_value = new_emg_value

                # update stimulation channels
                await self.update(mid_level, new_emg_value)

                # we must call this every 1.5s to keep stimulation ongoing
                if last_get_current_data_timestamp is None or timestamp - last_get_current_data_timestamp >= 1:
                    await mid_level.get_current_data()
                    last_get_current_data_timestamp = timestamp

        except asyncio.CancelledError:
            print('Stopping stimulating')
            # call stop mid level
            await mid_level.stop()

            # close serial port connection
            connection.close()


    async def update(self, mid_level: sm4.LayerMidLevel, emg_value: float):
        """Update active stimulation channels based on emg value"""

        active_muscles: set[Muscles] = []
        # use static threshold to activate stimulation
        if emg_value >= 0.024:
            active_muscles = [Muscles.FLEXOR_DIGITORUM] 

        # update stimulation only if muscles have changed
        if active_muscles != self.last_active_muscles:
            self.last_active_muscles = active_muscles

            cc = [None] * 8
            for x in active_muscles:
                cc[x] = (sm4.MidLevelChannelConfiguration(True, 1, 20,
                                                           [sm4.ChannelPoint(200, self.current),
                                                            sm4.ChannelPoint(100, 0),
                                                            sm4.ChannelPoint(200, -self.current)]))
            await mid_level.update(cc)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Example for combining Noraxon Ultium EMG device and HASOMED Science P24 stimulator.')
    parser.add_argument('--sciencemode_device', help='ScienceMode device name ("COM*")', default=None)
    args = parser.parse_args()

    # find LSL stream and open it
    streams = resolve_byprop(
        "type",
        "EMG",
        minimum=1,
        timeout=5
    )

    if not streams:
        raise RuntimeError("No EMG stream found")

    stream = streams[0]
    print("Stream found:", stream.name())

    inlet = StreamInlet(stream)
    stimulator = Stimulator(args.sciencemode_device, inlet)

    try:
        await stimulator.handle_communication()

    except asyncio.CancelledError:
        # Expected behavior during shutdown
        print('cancelled.')


if __name__ == '__main__':
    asyncio.run(main())
