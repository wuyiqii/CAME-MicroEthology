
# CAME-MicroEthology

Context-Anchored Micro-Ethology (CAME) is an unsupervised computational framework for resolving micro-dynamic organisation within context-anchored stationary animal behaviour.

This repository is associated with the manuscript:

**A Context-Anchored Micro-Ethological Computational Framework for Behavioural Analysis of Pigs in Stationary Bouts**

The repository is under active organisation. At this stage, it provides essential scripts and documentation for organising structured visual observations into anonymous tubelets and assessing visual-observation completeness.

## Scope

CAME operates after visual observations have been generated. Each object-level observation may include:

- bounding boxes;
- instance contours or masks;
- anatomical head-tail keypoints;
- coarse posture labels;
- functional-zone labels;
- frame numbers;
- anonymous local object identifiers.

CAME does not require long-term identity-preserved tracking. Instead, it organises detections into anonymous short-term tubelets for downstream micro-dynamic feature construction.

## Visual front-end

In our study, visual observations were generated using a SAM3-based segmentation workflow, a YOLO-based posture classification model, and a DeepLabCut ResNet-based head-tail keypoint estimator.

The data organisation follows the semi-automated workflow proposed in our Accelerated-Data-Engine project, where model-generated candidate outputs are manually reviewed, corrected or filtered before downstream analysis.

CAME itself is model-agnostic with respect to the upstream visual front-end. Users may replace SAM3, YOLO or DeepLabCut with other state-of-the-art models if the final outputs follow the CAME input schema.

This repository does not redistribute SAM3, YOLO, DeepLabCut, or their model weights.

## Minimal workflow

```bash
python scripts/json_to_csv.py
python scripts/tracklet_cleaner.py
python scripts/crop_and_split_tubelets.py
python scripts/detection_completeness.py