# Example how to use Noraxon Ultium EMG sensor and P24 stimulator with ScienceMode4 python lib together

## Introduction

Provides an example how to use Noraxon Ultium EMG sensor (https://www.noraxon.com/our-products/ultium-emg) in combination with HASOMED´s P24 ScienceMode library https://github.com/nextroundwinner/ScienceMode4Python.

This example uses data from a Noraxon Ultium EMG sensor to adjust stimulation parameters of P24. Communication between these two devices uses Lab Streaming Layer (LSL).

For P24 device:

- Connect to device
- Initialize mid level mode
- Update stimulation parameters according current emg value
- Stop stimulation
- Disconnect

This examples expects EMG data of an intend of movement from the hand.

## Hints

- Example
  - Reads EMG data from LSL stream and changes stimulation
  - Run `python .\example.py`
  - Adjust command line parameter for P24 com port
- Example data from file
  - Reads EMG data from a file and send it via LSL stream
  - Can be used if no physical device is available
  - Run `python .\mock_noraxon_ultium_emg.py`
  - Adjust command line parameters for a different file or sample rate
