# D-0095 — W7D3 trains one small Keras CNN on MNIST as a going-deeper subsection, answering O-30; Dropout and EarlyStopping appear in code there

- Date: 2026-11-18
- Status: accepted
- Decision: W7D3 trains one small Keras CNN on MNIST as a going-deeper subsection, answering O-30; Dropout and EarlyStopping appear in code there
- Why: Project 1 lets a learner classify images with a CNN, and until now the CNN was numpy concepts only (W6D3) plus layer shapes (W7D3 section 2.3). D-0087 left the build to the P1 spec and D-0091 kept week 7 Keras-first so the section is cheap: Conv2D, MaxPooling2D, Conv2D, MaxPooling2D, Flatten, Dropout, Dense on the MNIST arrays the week already loads, 3 epochs on a CPU runtime, its test accuracy read beside the 784-128-10 network. Modelled on the reference cohort CNNs_Intro demo. The ten minutes come from Wednesday sprint / project work.
- Affects: harness/plans/week-07.md (w07d3 sections, minutes, anti-spoiler and deviation ledgers), STATUS.md O-30, w07d3 research brief and notebook when authored
- Supersedes: —
- Superseded-by: —

## Notes

D-0087 stands for the rest: no RNN hands-on, no famous architectures, no data augmentation. Embedding stays shapes only.
