# Input format

CAME starts from structured visual-observation CSV files.

Each row represents one object-centred observation at one frame or second. The recommended columns are:

- FrameNumber
- group_id
- box
- mask
- kps0_det
- kps1_det
- posture
- zone_label
- pred_ds_label

## Required columns

FrameNumber: frame index or second index.
group_id: anonymous local object identifier within a short tubelet.
box: bounding-box polygon or corner coordinates.
mask: instance contour coordinates.
kps0_det: head keypoint.
kps1_det: tail keypoint.
posture: coarse posture label.
zone_label: functional-zone label.
pred_ds_label: stationary or dynamic label.

## Notes

The group_id does not represent long-term animal identity. It only indicates a local anonymous object assignment within a short tubelet.