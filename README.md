# Example how to use Noraxon Ultium EMG sensor and P24 stimulator with ScienceMode4 python lib together

## Introduction

Provides an example how to use Noraxon Ultium EMG sensor (https://www.noraxon.com/our-products/ultium-emg) in combination with HASOMED´s P24 ScienceMode library https://github.com/nextroundwinner/ScienceMode4Python.

This example uses data from a Noraxon Ultium EMG sensor to adjust stimulation parameters of P24. Communication between these two devices uses Lab Streaming Layer (LSL).

## Setup

- myoRESEARCH 4
  - Enable HTTP streaming
  - Start measurement with EMG device
- Noraxon-LSL (https://github.com/Noraxon/Noraxon-LSL)
  - Connect to HTTP streaming server from MR4
  - Ensure that data from MR4 contain timestamp information
- Run example
  - Reads EMG data from LSL stream and changes stimulation
  - Run `python .\example.py`
  - Adjust command line parameter for P24 com port


## Setup (Mock)
- Example data from file
  - Reads EMG data from a file and send it via LSL stream
  - Can be used if no physical device is available
  - Run `python .\mock_noraxon_ultium_emg.py`
  - Adjust command line parameters for a different file or sample rate
