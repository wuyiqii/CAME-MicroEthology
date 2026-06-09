# Visual front-end

CAME-MicroEthology is model-agnostic with respect to the upstream visual front-end.

In our study, visual observations were generated using:

- a SAM3-based segmentation workflow for candidate instance masks and bounding boxes;
- a YOLO-based posture classification model for coarse posture labels;
- a DeepLabCut ResNet-based pose estimation model for head-tail keypoints.

The data organisation follows the semi-automated workflow proposed in our Accelerated-Data-Engine project, where model-generated candidate outputs are manually reviewed, corrected or filtered before downstream analysis.

These visual models are not mandatory components of CAME. Users may replace them with other detection, segmentation, posture classification or pose-estimation models if the final outputs follow the CAME input schema.

CAME does not require long-term identity-preserved tracking. It operates on anonymous short-term tubelets.