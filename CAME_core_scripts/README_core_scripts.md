# CAME core scripts

Minimal public-facing implementation of the CAME core pipeline.

## Workflow

```bash
python scripts/run_minimal_demo.py \
  --input-dir examples/minimal_csv \
  --output-dir outputs/minimal_demo \
  --config configs/came_minimal.yaml \
  --fps 1.0
```

## Expected input CSV columns

Recommended columns:

```text
FrameNumber, group_id, box, mask, kps0_det, kps1_det, posture, zone_label, pred_ds_label
```

The visual front-end is model-agnostic. Users may generate these CSV files using SAM3, YOLO, DeepLabCut, or other visual models.

## Core files

- `came/extract_visual_features.py`
- `came/extract_stationary_bouts.py`
- `came/run_came_dynamics.py`
- `came/utils.py`
