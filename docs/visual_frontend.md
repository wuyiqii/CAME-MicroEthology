# Visual front-end

CAME-MicroEthology is model-agnostic with respect to the upstream visual front-end. The core CAME workflow begins from cleaned visual-observation CSV files and does not require users to install any specific detector, segmenter, posture classifier or pose-estimation model.

In our study, structured visual observations were generated using:

* a SAM3-based segmentation workflow for instance contours and bounding boxes;
* a YOLO-based posture classification model for coarse posture labels;
* a DeepLabCut ResNet-based pose-estimation model for head-tail keypoints.

The data organisation follows the semi-automated workflow proposed in our Accelerated-Data-Engine project, where model-generated candidate outputs are manually reviewed, corrected or filtered before downstream CAME analysis.

Users may replace SAM3, YOLO or DeepLabCut with other state-of-the-art visual models if the final outputs follow the CAME input schema.

## Optional installation notes

The following commands are provided only as optional installation examples for reproducing a visual front-end similar to the one used in our study. They are not required for running the core CAME scripts.

### 1. SAM3 for segmentation

```bash
conda create -n sam3 python=3.12
conda activate sam3

pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128

git clone https://github.com/facebookresearch/sam3.git
cd sam3
pip install -e .
```

### 2. Ultralytics YOLO for posture classification

```bash
conda create -n yolo python=3.10
conda activate yolo

pip install -U ultralytics
```

### 3. DeepLabCut for head-tail keypoint estimation

```bash
conda create -n dlc python=3.10
conda activate dlc

pip install "deeplabcut[gui]"
```

For headless use, users may install DeepLabCut without GUI components according to the official DeepLabCut documentation.

## Expected output from the visual front-end

The CAME core scripts expect cleaned CSV files with object-centred visual observations. Recommended columns include:

```text
FrameNumber
group_id
box
mask
kps0_det
kps1_det
posture
zone_label
pred_ds_label
```

The `group_id` field denotes an anonymous local object assignment within a short tubelet. It does not represent long-term animal identity.

## License and model-weight notice

This repository does not redistribute SAM3, YOLO, DeepLabCut or their model weights. Users should install these tools from their official repositories and comply with their respective licenses, model-weight terms and citation requirements.
