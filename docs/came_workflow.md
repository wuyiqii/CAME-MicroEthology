# CAME workflow

The minimal CAME workflow contains three computational stages.

## 1. Feature extraction

Input:
structured visual-observation CSV

Output:
feature-level CSV

Main outputs include geometry, morphology, orientation, head-tail coordination, local kinematics and feature-group energy variables.

## 2. Context-anchored stationary-bout extraction

Input:
feature-level CSV

Output:
stationary-bout frame table and bout index table

CAME extracts stationary bouts using three constraints:

- low locomotion or stationary label;
- coarse posture;
- functional-zone context.

The current minimal implementation supports:

- LAS: lying-associated stationary bouts;
- FAS: feeding-associated stationary bouts;
- SAS: standing-associated stationary bouts.

## 3. Micro-dynamic phase decoding

Input:
stationary-bout feature table

Output:
frame-level phase states, phase segments and bout descriptors

The framework computes:

- I_t: dynamic instability;
- B_t: boundary strength;
- R_t: fluctuation degree;
- E_t: overall activity magnitude.

Based on global or within-demo reference thresholds, CAME decodes stationary behaviour into:

- SP: Stable phase;
- IIP: Intermediate-instability phase;
- HIP: High-instability phase.