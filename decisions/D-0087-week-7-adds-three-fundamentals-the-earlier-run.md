# D-0087 — Week 7 adds three fundamentals the earlier run taught and ours lacks: the loss function and gradient descent before backprop, training against validation curves, and the confusion matrix with precision and recall; a Keras CNN build waits for the P1 spec

- Date: 2026-11-17
- Status: accepted
- Decision: Week 7 adds three fundamentals the earlier run taught and ours lacks: the loss function and gradient descent before backprop, training against validation curves, and the confusion matrix with precision and recall; a Keras CNN build waits for the P1 spec
- Why: Gap read on 2026-11-17 of the earlier run's week 1 (github.com/AICogEngineer/week1-ai-ml-fundamentals, 22 readings) against the week-6 pages and notebooks: 'loss function' appears nowhere in week 6 and cross-entropy only as a compile argument on W6D5, yet W7D1 teaches backpropagation; W6D5 plots training loss only, so no learner has read a validation curve; confusion matrix, precision and recall are a few sentences on the W6D1 page and in no notebook. All three are interview fundamentals and fit the W7D1 digit classifier without a new subtopic. The trainer accepted the recommendation in session. Items judged nitty-gritty under D-0086 (leaky ReLU and derivatives, weight initialisation, universal approximation, global pooling, famous architectures, curse of dimensionality, word2vec and RNN hands-on) are left out on purpose.
- Affects: harness/curriculum.json (w07d1 and w07d3 day notes), week 7 plan, STATUS.md O-30
- Supersedes: —
- Superseded-by: —

## Notes

W7D1 opens with the loss function (MSE for a number, cross-entropy for a class, lower is better) and gradient descent as small downhill steps, before backprop; its digit classifier trains with a validation split and the room reads the two curves for overfitting; its evaluation shows a confusion matrix on the ten digits, with precision and recall defined on one digit against the rest; XOR is the named example for the limit of one perceptron. W7D3 names dropout and regularisation in one sentence where the training process is customised, with no demo. Early stopping and checkpoints stay at name level. Not added: reinforcement learning as a third family on the live W6D1 page (low priority, a live-page edit). Open: whether a day builds and trains a Keras CNN (Conv2D, pooling, Flatten) is decided when the P1 spec is published (O-30).
