<p align="center">
  <img src="docs/figures/title.png" alt="CAME workflow" width="800">
</p>

---

 Context-Anchored Micro-Ethology (CAME) is an unsupervised computational framework for resolving micro-dynamic organisation within context-anchored stationary animal behaviour.

<p align="center">
  <img src="docs/figures/came_conceptual_design.png" alt="CAME workflow" width="800">
</p>

<p align="center">
  <em>Overview of the Context-Anchored Micro-Ethology conceptual design.</em>
</p>

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
- anonymous local object identifiers.

<table>
  <tr>
    <td align="center">
      <img src="docs/figures/drink.gif" alt="Functional-zone visual observation" height="180"><br>
      <sub>Functional-zone visual observation</sub>
    </td>
    <td align="center">
      <img src="docs/figures/run.gif" alt="Locomotion-aware visual observation" height="180"><br>
      <sub>Locomotion-aware visual observation</sub>
    </td>
    <td align="center">
      <img src="docs/figures/sitting.gif" alt="Posture-associated representation" height="180"><br>
      <sub>Posture-associated representation</sub>
    </td>
    <td align="center">
      <img src="docs/figures/keypoints_lying.gif" alt="Stationary bout visual observation" height="180"><br>
      <sub>Stationary bout visual observation</sub>
    </td>
    <td align="center">
      <img src="docs/figures/keypoints_sleep.gif" alt="Low-motion micro-dynamic observation" height="180"><br>
      <sub>Low-motion micro-dynamic observation</sub>
    </td>
  </tr>
</table>

CAME does not require long-term identity-preserved tracking. Instead, it organises detections into anonymous short-term tubelets for downstream micro-dynamic feature construction.

CAME-MicroEthology assumes that structured visual observations have already been generated. The repository does not require a specific upstream detector or annotation format. The core CAME workflow begins from cleaned visual-observation CSV files.

Example CSV files are provided in [`examples/minimal_csv`](examples/minimal_csv). These files illustrate the expected input schema, including frame index, anonymous local object ID, bounding box, instance contour, head-tail keypoints, posture label, functional-zone label. They are anonymised short tubelets for demonstrating the minimal CAME workflow, not the full dataset used in the manuscript.

## Visual front-end

CAME is model-agnostic with respect to upstream visual perception. In our study, visual observations were generated using a SAM3-based segmentation workflow, a YOLO-based posture classification model and a DeepLabCut ResNet-based head-tail keypoint estimator.

These models are optional upstream tools. CAME starts from cleaned visual-observation CSV files and does not redistribute SAM3, YOLO, DeepLabCut or their model weights.

See [Visual front-end](docs/visual_frontend.md) for optional installation notes and recommended input schema.

## Minimal workflow

CAME starts from structured visual-observation CSV files rather than raw videos. The expected input is a frame-wise object-level table containing bounding boxes, instance contours or masks, head-tail keypoints, posture labels, functional-zone labels, frame numbers and anonymous local object identifiers.

The intended workflow is:

1. visual-observation completeness assessment;
2. second-wise feature extraction;
3. context-anchored stationary-bout extraction;
4. micro-dynamic phase decoding;
5. bout-level and episode-level descriptor summarisation;
6. figure source-data and diagnostic-plot export.

The corresponding scripts will be progressively organised in the `CAME_core_scripts/scripts/` directory.

## Documentation

- [Input format](docs/input_format.md)
- [Visual front-end](docs/visual_frontend.md)
- [CAME workflow](docs/came_workflow.md)
- [Output files](docs/output_files.md)
