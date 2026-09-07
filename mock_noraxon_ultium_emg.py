"""
Helper program to provide recorded EMG data from a file via Lab Streaming Layer (LSL)
File must have columns time_s and emg_raw_mV
"""

import asyncio
import csv
from pathlib import Path
import argparse

from pylsl import StreamInfo, StreamOutlet, cf_float32


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Program to read EMG data from file and stream it via LSL. Press CTRL+C to terminate program.")
    parser.add_argument("--emg_filename", help="EMG .csv file", default="emg_intend_to_move.csv")
    parser.add_argument("--sample_rate", type=float, help="Sample rate", default=1000.0)
    args = parser.parse_args()

    try:
        # create LSL stream
        info = StreamInfo(
            name="Forearm",
            type="EMG",
            channel_count=1,
            nominal_srate=args.sample_rate,
            channel_format=cf_float32
        )

        channels = info.desc().append_child("channels")
        channel = channels.append_child("channel")
        channel.append_child_value("label", "Digitorum")
        channel.append_child_value("unit", "mV")

        info.desc().append_child_value("noraxon_device", "Mock Ultium EMG")
        info.desc().append_child_value("noraxon_channel_type", "EMG")

        outlet = StreamOutlet(info)

        print(info)
        print("Mock-Noraxon-EMG running...")

        # read .csv file and loop over all lines until program is terminated by user
        csv_file_path = Path(__file__).with_name(args.emg_filename)

        with csv_file_path.open(mode="r", newline="", encoding="utf-8") as csv_file:

            while True:
                csv_file.seek(0)
                csv_reader = csv.DictReader(csv_file)

                for row in csv_reader:
                    emg_value = float(row['emg_raw_mV'])

                    outlet.push_sample([emg_value])
                    await asyncio.sleep(1.0 / args.sample_rate)

    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    asyncio.run(main())
