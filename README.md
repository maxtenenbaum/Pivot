# Pivot

Pivot is a control system for a rotary switching mechanism. This repository contains both the Python control software and the Arduino firmware.

## Structure

- `pivot/` – Python package
- `arduino/` – Arduino firmware
- `examples/` – Example usage scripts
- `tests/` – Python tests
- `docs/` – Documentation

## Python Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # On Windows
source .venv/bin/activate   # On Mac/Linux

pip install -r requirements.txt
