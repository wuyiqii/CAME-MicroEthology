<p align="center">
  <img src="docs/figures/title.png" alt="CAME title" width="800">
</p>

---

<h1 align="center">CAME-MicroEthology</h1>

<p align="center">
  <strong>Context-Anchored Micro-Ethology for stationary-bout behavioural analysis</strong>
</p>

<p align="center">
  <em>An unsupervised computational framework for resolving micro-dynamic organisation within context-anchored stationary animal behaviour.</em>
</p>

<p align="center">
  🔬 Framework &nbsp;&nbsp;|&nbsp;&nbsp; 🧭 Context-anchored analysis &nbsp;&nbsp;|&nbsp;&nbsp; 🐖 Pig behaviour &nbsp;&nbsp;|&nbsp;&nbsp; 📊 Structured visual observations
</p>

This repository is associated with the manuscript:

**A Context-Anchored Micro-Ethological Computational Framework for Behavioural Analysis of Pigs in Stationary Bouts**

The repository is under active organisation. At this stage, it provides essential scripts and documentation for organising structured visual observations into anonymous tubelets and assessing visual-observation completeness.

## 🧠 Concept

<p align="center">
  <img src="docs/figures/came_conceptual_design.png" alt="CAME conceptual design" width="600">
</p>

<p align="center">
  <em>Conceptual design of Context-Anchored Micro-Ethology.</em>
</p>

## 🗺️ Framework Overview

<p align="center">
  <img src="docs/figures/came_framework_overview.png" alt="CAME framework overview" width="850">
</p>

<p align="center">
  <em>CAME converts structured visual observations into context-anchored stationary bouts, micro-dynamic phases and behavioural descriptors.</em>
</p>

## ✨ Scope

CAME operates after visual observations have been generated. Each object-level observation may include:

- Bounding boxes;
- Instance contours or masks;
- Anatomical head-tail keypoints;
- Coarse posture labels;
- Functional-zone labels;
- Anonymous local object identifiers.

<table align="center" border="0" cellspacing="0" cellpadding="6" style="border: none; border-collapse: collapse;">
  <tr>
    <td align="center" valign="top" style="border: none;">
      <img src="docs/figures/drink.gif" alt="Standing visual observation" height="160"><br>
      <sub><strong>Standing visual observation</strong></sub>
    </td>
    <td align="center" valign="top" style="border: none;">
      <img src="docs/figures/run.gif" alt="Locomotion visual observation" height="160"><br>
      <sub><strong>Locomotion visual observation</strong></sub>
    </td>
    <td align="center" valign="top" style="border: none;">
      <img src="docs/figures/sitting.gif" alt="Resting visual observation" height="160"><br>
      <sub><strong>Resting visual observation</strong></sub>
    </td>
  </tr>
</table>

<table align="center" border="0" cellspacing="0" cellpadding="6" style="border: none; border-collapse: collapse;">
  <tr>
    <td align="center" valign="top" style="border: none;">
      <img src="docs/figures/keypoints_lying.gif" alt="Resting visual observation" height="160"><br>
      <sub><strong>Resting visual observation</strong></sub>
    </td>
    <td align="center" valign="top" style="border: none;">
      <img src="docs/figures/keypoints_sleep.gif" alt="Resting visual observation" height="160"><br>
      <sub><strong>Resting visual observation</strong></sub>
    </td>
  </tr>
</table>

> [!NOTE]
> CAME does not require long-term identity-preserved tracking. Instead, it organises detections into anonymous short-term tubelets for downstream micro-dynamic feature construction.

> [!TIP]
> CAME-MicroEthology assumes that structured visual observations have already been generated. The repository does not require a specific upstream detector or annotation format. The core workflow begins from cleaned visual-observation CSV files.

Example CSV files are provided in [`examples/minimal_csv`](examples/minimal_csv). These files illustrate the expected input schema, including frame index, anonymous local object ID, bounding box, instance contour, head-tail keypoints, posture label and functional-zone label. They are anonymised short tubelets for demonstrating the minimal CAME workflow, not the full dataset used in the manuscript.

## 👁️ Visual Front-End

CAME is model-agnostic with respect to upstream visual perception. In our study, visual observations were generated using:

- SAM3-based segmentation;
- YOLO-based posture classification;
- DeepLabCut ResNet-based head-tail keypoint estimation.
These models are optional upstream tools. CAME starts from cleaned visual-observation CSV files and does not redistribute SAM3, YOLO, DeepLabCut or their model weights.

See [Visual front-end](docs/visual_frontend.md) for optional installation notes and recommended input schema.

## 🚀 Installation

```bash
git clone https://github.com/wuyiqii/CAME-MicroEthology.git
cd CAME-MicroEthology

conda create -n came python=3.12
conda activate came

pip install -r requirements.txt
```

## ⚙️ Minimal Workflow

CAME starts from structured visual-observation CSV files rather than raw videos. The expected input is a frame-wise object-level table containing bounding boxes, instance contours or masks, head-tail keypoints, posture labels, functional-zone labels, frame numbers and anonymous local object identifiers.

The minimal core workflow includes:

1. Second-wise feature extraction;
2. Context-anchored stationary-bout extraction;
3. Micro-dynamic phase decoding;
4. Bout-level descriptor summarisation.

```bash
python scripts/run_minimal_demo.py \
  --input-dir examples/minimal_csv \
  --output-dir outputs/minimal_demo \
  --config configs/came_minimal.yaml \
  --fps 1.0
```

## 📚 Documentation

- [Input format](docs/input_format.md)
- [Visual front-end](docs/visual_frontend.md)
- [CAME workflow](docs/came_workflow.md)
- [Output files](docs/output_files.md)

## 📖 Citation

If you use CAME-MicroEthology in your research, please cite the associated manuscript:

```text
Wu, Y. and Li, J. A Context-Anchored Micro-Ethological Computational Framework for Behavioural Analysis of Pigs in Stationary Bouts. Manuscript under review.
```

A complete citation, DOI and BibTeX entry will be added after publication.

For correspondence, please contact Jiangong Li at [jli153@cau.edu.cn](mailto:jli153@cau.edu.cn).

### BibTeX

```bibtex
@article{wu_came_microethology_2026,
  title  = {A Context-Anchored Micro-Ethological Computational Framework for Behavioural Analysis of Pigs in Stationary Bouts},
  author = {Wu, Yiqi and Li, Jiangong},
  year   = {2026},
  note   = {Manuscript under review}
}
```

### Related tools

The visual front-end used in our study refers to SAM3, YOLO-based posture classification and DeepLabCut. These tools are not redistributed in this repository. Users should cite the corresponding tools and comply with their licences and model-weight terms when using them.

## 📜 License

CAME-MicroEthology is released for non-commercial academic use only.

- Code is licensed under the PolyForm Noncommercial License 1.0.0.
- Documentation, figures and example materials are licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0), unless otherwise stated.
- Commercial use, redistribution for commercial purposes, and integration into commercial products are not permitted without prior written permission from the authors.

This repository does not redistribute SAM3, YOLO, DeepLabCut or their model weights. These third-party tools are governed by their own licences and terms of use.
