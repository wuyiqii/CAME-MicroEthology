# Output files

The minimal CAME pipeline generates the following outputs.

## Feature extraction outputs

`*_features.csv`

This file contains the original visual observations and derived feature columns.

## Stationary-bout outputs

`*_bout_index.csv`

Summary table of extracted stationary bouts.

`*_bout_frames.csv`

Frame-level table containing all rows belonging to valid context-anchored stationary bouts.

## CAME dynamics outputs

`*_frame_states.csv`

Frame-level dynamic indices and phase labels.

Main columns:

- I_t
- B_t
- R_t
- E_t
- phase_code
- phase_label

`*_phase_segments.csv`

Run-length summary of continuous SP/IIP/HIP phase segments.

`*_bout_descriptors.csv`

Bout-level descriptors, including:

- SP occupancy
- IIP occupancy
- HIP occupancy
- IIP + HIP ratio
- transition count
- transition density
- longest SP fraction
- mean and maximum I_t
- mean B_t
- mean R_t
- mean E_t

`*_thresholds.json`

Thresholds and feature weights used for phase decoding.