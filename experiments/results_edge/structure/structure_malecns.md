# Structure probe: malecns (no simulation)

2026-09-27 08:25. `experiments/edge/structure_probe.py --dataset malecns`. Raw load: Connectome(malecns/all_min1: 164439 neurons, 25550959 connections, 123967656 synapses, w_syn_scale=0.542, signs=shiu). Variants: `all_min1+eln0.25` (the paper's model), `all_min1` (the published model). 60 s.

Definitions (module docstring): hops over all connections; paths = simple neuron-level paths of length <= 3; w_k = mean over the target neurons of x_k = x_{k-1} @ Wn from x_0 = 1 on the sources, Wn = W / column sum of |W| (w_1 = signed fraction of the targets' input synapses coming from the sources). `w_max` = the w_k (k = 1..4) with the largest |w_k|, shown as `value kK`.

## Checks

- eLN (ALLN with a positive row sign): 206 under the Shiu signs, 206 under the known signs; known+eln0.25: 206 (connectome.py docstring: 150).
- routes: the exact chains of k = 1..3 add up to w_k (max relative error 4.0e-13); forward and backward w_k agree (max relative error 6.8e-13); every combination's w_k is the sum of its single groups' (max relative error 7.2e-15).

## (a) Sensory input -> deciders

### Hops / simple paths within 3 hops (all connections; the same in every variant)

| source | P1/pC1 | pIP10 | aIPg | vpoEN/DN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / 7,190,583 | 2 / 127,170 | 2 / 764,188 | 2 / 56,418 | 2 / 263,761 | 3 / 13,398 |
| cVA-long (Or65a/DL3) | 2 / 344,822 | 3 / 2,158 | 3 / 24,619 | 3 / 4,538 | 2 / 10,931 | 3 / 1,074 |
| Or47b (VA1v) | 2 / 2,887,847 | 2 / 49,998 | 2 / 415,014 | 3 / 29,145 | 2 / 112,531 | 3 / 8,472 |
| Or88a (VA1d) | 2 / 1,655,832 | 3 / 29,943 | 2 / 250,662 | 3 / 17,379 | 2 / 65,323 | 3 / 4,886 |
| Or83c (DC3) | 2 / 687,769 | 3 / 11,267 | 2 / 86,789 | 3 / 7,326 | 2 / 27,214 | 3 / 2,267 |
| food odor | 2 / 2,759,795 | 3 / 34,196 | 2 / 246,793 | 2 / 34,104 | 2 / 97,467 | 3 / 12,024 |
| CO2 (V) | 2 / 449,518 | 3 / 7,718 | 2 / 46,716 | 3 / 5,081 | 2 / 15,985 | 3 / 1,938 |
| aversive odor (DA2/DL4) | 2 / 555,874 | 2 / 4,866 | 2 / 41,979 | 3 / 6,648 | 2 / 19,711 | 3 / 1,830 |
| song/sound (JO-A) | 1 / 2,772,866 | 2 / 80,942 | 2 / 322,430 | 1 / 321,176 | 2 / 98,882 | 2 / 9,062 |
| sound (JO-B) | 2 / 1,754,477 | 2 / 59,317 | 2 / 222,518 | 2 / 352,356 | 2 / 73,138 | 2 / 14,810 |
| wind/gravity (JO-CE) | 2 / 9,834,127 | 2 / 408,372 | 2 / 1,635,694 | 2 / 1,237,600 | 2 / 558,193 | 2 / 92,872 |
| touch (all head bristles) | 2 / 19,695,863 | 2 / 794,481 | 2 / 2,983,483 | 2 / 854,130 | 2 / 1,511,423 | 2 / 1,034,231 |
| touch (eye bristles) | 2 / 14,080,732 | 2 / 543,431 | 2 / 2,063,803 | 2 / 648,671 | 2 / 1,064,869 | 2 / 420,377 |
| sugar GRNs | 2 / 4,180,461 | 2 / 166,225 | 2 / 406,894 | 2 / 38,399 | 2 / 277,263 | 2 / 350,348 |
| cVA + food | 2 / 9,950,378 | 2 / 161,366 | 2 / 1,010,981 | 2 / 90,522 | 2 / 361,228 | 3 / 25,422 |
| cVA + touch | 2 / 26,886,446 | 2 / 921,651 | 2 / 3,747,671 | 2 / 910,548 | 2 / 1,775,184 | 2 / 1,047,629 |
| cVA + song | 1 / 9,963,449 | 2 / 208,112 | 2 / 1,086,618 | 1 / 377,594 | 2 / 362,643 | 2 / 22,460 |
| Or47b + song | 1 / 5,660,713 | 2 / 130,940 | 2 / 737,444 | 1 / 350,321 | 2 / 211,413 | 2 / 17,534 |
| Or47b + touch | 2 / 22,583,710 | 2 / 844,479 | 2 / 3,398,497 | 2 / 883,275 | 2 / 1,623,954 | 2 / 1,042,703 |
| food + touch | 2 / 22,455,658 | 2 / 828,677 | 2 / 3,230,276 | 2 / 888,234 | 2 / 1,608,890 | 2 / 1,046,255 |
| CO2 + touch | 2 / 20,145,381 | 2 / 802,199 | 2 / 3,030,199 | 2 / 859,211 | 2 / 1,527,408 | 2 / 1,036,169 |
| cVA + sugar | 2 / 11,371,044 | 2 / 293,395 | 2 / 1,171,082 | 2 / 94,817 | 2 / 541,024 | 2 / 363,746 |
| contact pheromone (ppk23/25) | 2 / 34,279,723 | 2 / 925,701 | 2 / 4,033,153 | 2 / 720,511 | 2 / 1,525,326 | 2 / 135,834 |
| ppk23 only (male CHC) | 2 / 16,714,206 | 2 / 439,540 | 2 / 1,992,120 | 2 / 333,603 | 2 / 718,548 | 2 / 64,705 |
| ppk25 only (female CHC) | 2 / 17,565,517 | 2 / 486,161 | 2 / 2,041,033 | 2 / 386,908 | 2 / 806,778 | 2 / 71,129 |
| cVA + contact pheromone | 2 / 41,470,306 | 2 / 1,052,871 | 2 / 4,797,341 | 2 / 776,929 | 2 / 1,789,087 | 2 / 149,232 |
| ppk25 + touch | 2 / 37,261,380 | 2 / 1,280,642 | 2 / 5,024,516 | 2 / 1,241,038 | 2 / 2,318,201 | 2 / 1,105,360 |
| all pheromones + contact + touch | 2 / 66,742,439 | 2 / 1,940,718 | 2 / 8,557,908 | 2 / 1,689,447 | 2 / 3,516,509 | 2 / 1,200,162 |

### `all_min1+eln0.25`: strongest signed propagated weight w_max (and its k)

| source | P1/pC1 | pIP10 | aIPg | vpoEN/DN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | +8.7e-04 k3 | -8.7e-04 k3 | +1.0e-03 k3 | -4.5e-05 k4 | +1.7e-03 k3 | +5.3e-05 k4 |
| cVA-long (Or65a/DL3) | +9.2e-05 k2 | +2.2e-05 k4 | +6.2e-06 k3 | -4.8e-06 k4 | +6.2e-06 k3 | -3.2e-07 k4 |
| Or47b (VA1v) | -4.7e-04 k3 | -1.9e-04 k4 | -6.6e-04 k3 | +4.6e-05 k4 | -8.3e-04 k4 | -1.0e-05 k3 |
| Or88a (VA1d) | -1.2e-04 k3 | +3.8e-05 k3 | -1.8e-04 k3 | +2.5e-05 k4 | -2.3e-04 k4 | -5.2e-06 k3 |
| Or83c (DC3) | -6.9e-06 k4 | +5.2e-05 k4 | +4.1e-05 k3 | -2.5e-06 k4 | +4.1e-05 k3 | -3.7e-07 k3 |
| food odor | +2.4e-05 k3 | +1.5e-05 k4 | +7.4e-05 k3 | -8.3e-06 k4 | +3.2e-05 k3 | -1.4e-06 k3 |
| CO2 (V) | +9.2e-06 k3 | -5.8e-06 k3 | +5.9e-06 k4 | -3.9e-06 k4 | -2.5e-05 k3 | +2.3e-06 k4 |
| aversive odor (DA2/DL4) | +5.9e-05 k3 | +8.6e-06 k4 | +1.4e-05 k3 | +5.6e-06 k3 | +1.3e-05 k4 | -2.7e-07 k4 |
| song/sound (JO-A) | -5.4e-05 k4 | -6.2e-05 k3 | +6.2e-05 k3 | -3.0e-03 k3 | -1.2e-04 k2 | -9.8e-06 k4 |
| sound (JO-B) | +7.1e-05 k3 | -1.5e-05 k4 | +6.0e-05 k3 | -1.8e-03 k3 | +4.8e-05 k4 | -1.3e-05 k3 |
| wind/gravity (JO-CE) | +1.5e-04 k3 | -9.5e-05 k4 | +1.4e-04 k3 | -4.1e-03 k3 | +2.4e-04 k3 | +5.3e-05 k4 |
| touch (all head bristles) | +2.1e-04 k3 | -4.6e-05 k3 | +3.9e-04 k3 | -9.5e-04 k3 | +3.7e-04 k3 | -8.0e-03 k2 |
| touch (eye bristles) | +5.6e-05 k2 | -1.5e-05 k4 | +1.4e-04 k3 | -5.4e-04 k3 | +7.0e-05 k3 | +5.5e-04 k3 |
| sugar GRNs | -5.6e-05 k2 | +3.6e-06 k3 | +2.2e-05 k4 | -5.9e-06 k4 | +5.1e-05 k3 | +1.7e-03 k3 |
| cVA + food | +9.0e-04 k3 | -8.6e-04 k3 | +1.1e-03 k3 | -5.4e-05 k4 | +1.8e-03 k3 | +5.2e-05 k4 |
| cVA + touch | +1.1e-03 k3 | -9.1e-04 k3 | +1.4e-03 k3 | -9.9e-04 k3 | +2.1e-03 k3 | -8.0e-03 k2 |
| cVA + song | +8.5e-04 k3 | -9.3e-04 k3 | +1.1e-03 k3 | -3.0e-03 k3 | +1.8e-03 k3 | +4.3e-05 k4 |
| Or47b + song | -5.0e-04 k3 | -2.3e-04 k4 | -6.3e-04 k4 | -3.0e-03 k3 | -8.4e-04 k4 | -1.3e-05 k4 |
| Or47b + touch | -3.8e-04 k4 | -2.1e-04 k4 | -4.4e-04 k4 | -9.5e-04 k3 | -6.5e-04 k4 | -8.0e-03 k2 |
| food + touch | +2.4e-04 k3 | -4.2e-05 k3 | +4.6e-04 k3 | -9.6e-04 k3 | +4.1e-04 k3 | -8.0e-03 k2 |
| CO2 + touch | +2.2e-04 k3 | -5.2e-05 k3 | +3.9e-04 k3 | -9.5e-04 k3 | +3.5e-04 k3 | -8.0e-03 k2 |
| cVA + sugar | +8.4e-04 k3 | -8.6e-04 k3 | +1.0e-03 k3 | -5.1e-05 k4 | +1.8e-03 k3 | +1.7e-03 k3 |
| contact pheromone (ppk23/25) | +1.3e-03 k4 | +1.5e-04 k4 | -2.7e-03 k2 | -4.7e-04 k3 | -5.6e-03 k2 | -4.2e-05 k4 |
| ppk23 only (male CHC) | +1.2e-03 k3 | +5.2e-05 k2 | -2.1e-03 k2 | -3.0e-04 k3 | -5.1e-03 k2 | -3.1e-05 k4 |
| ppk25 only (female CHC) | +1.2e-03 k4 | +1.1e-04 k4 | -5.5e-04 k2 | -2.1e-04 k4 | +1.7e-03 k4 | -1.1e-05 k4 |
| cVA + contact pheromone | +2.1e-03 k4 | -8.7e-04 k3 | -2.8e-03 k2 | -5.1e-04 k3 | -5.7e-03 k2 | -2.3e-05 k3 |
| ppk25 + touch | +1.3e-03 k4 | +9.3e-05 k4 | +6.0e-04 k4 | -1.1e-03 k3 | +1.9e-03 k4 | -7.9e-03 k2 |
| all pheromones + contact + touch | +1.7e-03 k4 | -8.9e-04 k3 | -3.2e-03 k2 | -1.5e-03 k3 | -5.7e-03 k2 | -7.9e-03 k2 |

### `all_min1+eln0.25`: excitatory-only hops / w_exc_3 (upper bound of what can excite)

| source | P1/pC1 | pIP10 | aIPg | vpoEN/DN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / +1.8e-03 | 2 / +3.1e-04 | 2 / +1.6e-03 | 2 / +2.6e-05 | 2 / +2.6e-03 | 3 / +1.5e-05 |
| cVA-long (Or65a/DL3) | 2 / +1.1e-04 | 3 / +1.6e-06 | 3 / +1.3e-05 | 3 / +4.1e-07 | 2 / +1.6e-05 | 3 / +2.4e-08 |
| Or47b (VA1v) | 2 / +1.3e-04 | 2 / +1.7e-05 | 2 / +1.1e-04 | 3 / +4.9e-07 | 2 / +7.4e-05 | 3 / +1.5e-06 |
| Or88a (VA1d) | 2 / +5.8e-05 | 3 / +8.0e-07 | 3 / +9.6e-05 | 3 / +9.0e-08 | 2 / +1.0e-04 | 3 / +4.3e-08 |
| Or83c (DC3) | 2 / +5.2e-05 | 3 / +1.3e-06 | 3 / +5.9e-05 | 3 / +2.0e-07 | 2 / +7.1e-05 | 3 / +8.5e-08 |
| food odor | 2 / +5.5e-05 | 3 / +1.0e-05 | 2 / +7.0e-05 | 2 / +3.4e-06 | 2 / +3.8e-05 | 3 / +9.3e-07 |
| CO2 (V) | 2 / +2.9e-05 | 3 / +2.4e-06 | 2 / +1.1e-05 | 3 / +3.3e-06 | 2 / +3.9e-06 | 3 / +1.8e-07 |
| aversive odor (DA2/DL4) | 2 / +6.7e-05 | 2 / +3.9e-07 | 2 / +1.3e-05 | 3 / +5.9e-06 | 2 / +1.2e-05 | 3 / +2.7e-08 |
| song/sound (JO-A) | 1 / +3.9e-04 | 2 / +5.7e-05 | 2 / +2.1e-04 | 1 / +3.1e-03 | 2 / +2.0e-04 | 2 / +5.1e-06 |
| sound (JO-B) | 2 / +2.2e-04 | 2 / +1.8e-05 | 2 / +1.1e-04 | 2 / +3.4e-03 | 2 / +7.1e-05 | 2 / +7.4e-06 |
| wind/gravity (JO-CE) | 2 / +5.1e-04 | 2 / +1.3e-04 | 2 / +3.9e-04 | 2 / +4.0e-03 | 2 / +3.5e-04 | 2 / +1.9e-04 |
| touch (all head bristles) | 2 / +5.6e-04 | 2 / +1.7e-04 | 2 / +6.7e-04 | 2 / +3.3e-04 | 2 / +7.4e-04 | 2 / +5.7e-03 |
| touch (eye bristles) | 2 / +2.0e-04 | 2 / +7.2e-05 | 2 / +2.3e-04 | 2 / +1.7e-04 | 2 / +2.4e-04 | 2 / +9.5e-04 |
| sugar GRNs | 2 / +1.1e-04 | 2 / +4.6e-05 | 2 / +4.8e-05 | 2 / +7.6e-06 | 2 / +6.6e-05 | 2 / +2.3e-03 |
| cVA + food | 2 / +1.9e-03 | 2 / +3.2e-04 | 2 / +1.6e-03 | 2 / +3.0e-05 | 2 / +2.7e-03 | 3 / +1.6e-05 |
| cVA + touch | 2 / +2.4e-03 | 2 / +4.8e-04 | 2 / +2.2e-03 | 2 / +3.6e-04 | 2 / +3.4e-03 | 2 / +5.7e-03 |
| cVA + song | 1 / +2.2e-03 | 2 / +3.6e-04 | 2 / +1.8e-03 | 1 / +3.1e-03 | 2 / +2.8e-03 | 2 / +2.0e-05 |
| Or47b + song | 1 / +5.2e-04 | 2 / +7.4e-05 | 2 / +3.2e-04 | 1 / +3.1e-03 | 2 / +2.8e-04 | 2 / +6.6e-06 |
| Or47b + touch | 2 / +6.9e-04 | 2 / +1.9e-04 | 2 / +7.8e-04 | 2 / +3.4e-04 | 2 / +8.1e-04 | 2 / +5.7e-03 |
| food + touch | 2 / +6.1e-04 | 2 / +1.8e-04 | 2 / +7.4e-04 | 2 / +3.4e-04 | 2 / +7.8e-04 | 2 / +5.7e-03 |
| CO2 + touch | 2 / +5.8e-04 | 2 / +1.7e-04 | 2 / +6.8e-04 | 2 / +3.4e-04 | 2 / +7.4e-04 | 2 / +5.7e-03 |
| cVA + sugar | 2 / +1.9e-03 | 2 / +3.5e-04 | 2 / +1.6e-03 | 2 / +3.4e-05 | 2 / +2.7e-03 | 2 / +2.4e-03 |
| contact pheromone (ppk23/25) | 2 / +1.4e-03 | 2 / +3.5e-04 | 2 / +9.1e-04 | 2 / +3.1e-04 | 2 / +6.2e-04 | 2 / +7.9e-05 |
| ppk23 only (male CHC) | 2 / +7.5e-04 | 2 / +1.8e-04 | 2 / +5.9e-04 | 2 / +1.3e-04 | 2 / +3.9e-04 | 2 / +4.1e-05 |
| ppk25 only (female CHC) | 2 / +6.8e-04 | 2 / +1.7e-04 | 2 / +3.2e-04 | 2 / +1.9e-04 | 2 / +2.3e-04 | 2 / +3.8e-05 |
| cVA + contact pheromone | 2 / +3.3e-03 | 2 / +6.6e-04 | 2 / +2.5e-03 | 2 / +3.4e-04 | 2 / +3.2e-03 | 2 / +9.5e-05 |
| ppk25 + touch | 2 / +1.2e-03 | 2 / +3.4e-04 | 2 / +9.9e-04 | 2 / +5.2e-04 | 2 / +9.7e-04 | 2 / +5.8e-03 |
| all pheromones + contact + touch | 2 / +4.2e-03 | 2 / +8.5e-04 | 2 / +3.4e-03 | 2 / +6.8e-04 | 2 / +4.2e-03 | 2 / +5.8e-03 |

- reference touch (all head bristles) -> DNp13 reject: hops 2, 1,511,423 paths, w_max +3.7e-04 (k3), w_exc_3 +7.4e-04; top route `touch (all head bristles) > AN01A089 > PVLP204m > DNp13 reject` (+1.0e-04)
- reference sugar GRNs -> MN9: hops 2, 350,348 paths, w_max +1.7e-03 (k3), w_exc_3 +2.3e-03; top route `sugar GRNs > GNG042 > GNG015 > MN9` (+4.0e-04)
- largest decider |w_max| (single sensory groups): wind/gravity (JO-CE) -> vpoEN/DN accept, -4.1e-03 (k3) = 10.99x the weaker reference's.
- largest decider positive w_max (single sensory groups): contact pheromone (ppk23/25) -> P1/pC1 male, +1.3e-03 (k4) = 3.48x the weaker reference's.
- largest decider w_exc_3 (single sensory groups): wind/gravity (JO-CE) -> vpoEN/DN accept, +4.0e-03 = 5.39x the weaker reference's.
- 32 of 68 single-group sensory-decider pairs have a negative w_max (net inhibitory).

Strongest single sensory group per decider under `all_min1+eln0.25` (top route; share of that w_k):

- P1/pC1 male: contact pheromone (ppk23/25), w_max +1.3e-03 (k4), hops 2; `contact pheromone (ppk23/25) > AN09B017g > P1/pC1 male` -5.3e-04 (k2, 54% of w_2)
- pIP10 song cmd: cVA (Or67d/DA1), w_max -8.7e-04 (k3), hops 2; `cVA (Or67d/DA1) > DA1_lPN > LH007m > pIP10 song cmd` -6.5e-04 (k3, 75% of w_3)
- aIPg aggr: contact pheromone (ppk23/25), w_max -2.7e-03 (k2), hops 2; `contact pheromone (ppk23/25) > AN09B017c > aIPg aggr` -2.2e-03 (k2, 81% of w_2)
- vpoEN/DN accept: wind/gravity (JO-CE), w_max -4.1e-03 (k3), hops 2; `wind/gravity (JO-CE) > WED118 > vpoEN/DN accept` +2.6e-03 (k2, 118% of w_2)

### `all_min1`: strongest signed propagated weight w_max (and its k)

| source | P1/pC1 | pIP10 | aIPg | vpoEN/DN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | +7.4e-04 k3 | -7.7e-04 k3 | +9.1e-04 k3 | -3.9e-05 k4 | +1.5e-03 k3 | +4.9e-05 k4 |
| cVA-long (Or65a/DL3) | +8.3e-05 k2 | +1.8e-05 k4 | -6.8e-06 k4 | -4.4e-06 k4 | +5.7e-06 k3 | -3.6e-07 k4 |
| Or47b (VA1v) | -4.1e-04 k3 | -1.7e-04 k4 | -5.6e-04 k3 | +4.2e-05 k4 | -7.1e-04 k3 | -9.2e-06 k3 |
| Or88a (VA1d) | -1.1e-04 k3 | +3.2e-05 k3 | -1.6e-04 k3 | +2.3e-05 k4 | -1.9e-04 k4 | -4.8e-06 k3 |
| Or83c (DC3) | -7.0e-06 k3 | +3.5e-05 k4 | +3.3e-05 k3 | -1.8e-06 k4 | +3.1e-05 k3 | -3.3e-07 k4 |
| food odor | +2.7e-05 k3 | +6.9e-06 k4 | +5.8e-05 k3 | -7.5e-06 k4 | +2.8e-05 k3 | -1.8e-06 k4 |
| CO2 (V) | +6.4e-06 k3 | -5.3e-06 k3 | +4.0e-06 k3 | -3.8e-06 k4 | -2.2e-05 k3 | +1.8e-06 k4 |
| aversive odor (DA2/DL4) | +4.7e-05 k3 | +4.7e-06 k4 | +9.9e-06 k3 | +4.4e-06 k3 | +1.1e-05 k4 | -6.2e-07 k4 |
| song/sound (JO-A) | -5.4e-05 k4 | -6.2e-05 k3 | +6.2e-05 k3 | -3.0e-03 k3 | -1.2e-04 k2 | -9.8e-06 k4 |
| sound (JO-B) | +7.1e-05 k3 | -1.5e-05 k4 | +6.0e-05 k3 | -1.8e-03 k3 | +4.8e-05 k4 | -1.3e-05 k3 |
| wind/gravity (JO-CE) | +1.5e-04 k3 | -9.4e-05 k4 | +1.4e-04 k3 | -4.1e-03 k3 | +2.4e-04 k3 | +5.3e-05 k4 |
| touch (all head bristles) | +2.1e-04 k3 | -4.6e-05 k3 | +3.9e-04 k3 | -9.5e-04 k3 | +3.7e-04 k3 | -8.0e-03 k2 |
| touch (eye bristles) | +5.6e-05 k2 | -1.5e-05 k4 | +1.4e-04 k3 | -5.4e-04 k3 | +7.0e-05 k3 | +5.5e-04 k3 |
| sugar GRNs | -5.6e-05 k2 | +3.6e-06 k3 | +2.2e-05 k4 | -5.8e-06 k4 | +5.1e-05 k3 | +1.7e-03 k3 |
| cVA + food | +7.7e-04 k3 | -7.7e-04 k3 | +9.7e-04 k3 | -4.6e-05 k4 | +1.6e-03 k3 | +4.7e-05 k4 |
| cVA + touch | +9.6e-04 k3 | -8.2e-04 k3 | +1.3e-03 k3 | -9.9e-04 k3 | +1.9e-03 k3 | -8.0e-03 k2 |
| cVA + song | +7.2e-04 k3 | -8.4e-04 k3 | +9.7e-04 k3 | -3.0e-03 k3 | +1.7e-03 k3 | +3.9e-05 k4 |
| Or47b + song | -4.3e-04 k3 | -2.1e-04 k4 | -5.0e-04 k3 | -3.0e-03 k3 | -6.8e-04 k4 | -1.2e-05 k4 |
| Or47b + touch | -2.8e-04 k4 | -1.9e-04 k4 | -3.0e-04 k4 | -9.5e-04 k3 | -4.8e-04 k4 | -8.0e-03 k2 |
| food + touch | +2.4e-04 k3 | -4.2e-05 k3 | +4.4e-04 k3 | -9.6e-04 k3 | +4.0e-04 k3 | -8.0e-03 k2 |
| CO2 + touch | +2.2e-04 k3 | -5.1e-05 k3 | +3.9e-04 k3 | -9.5e-04 k3 | +3.5e-04 k3 | -8.0e-03 k2 |
| cVA + sugar | +7.1e-04 k3 | -7.7e-04 k3 | +9.3e-04 k3 | -4.4e-05 k4 | +1.6e-03 k3 | +1.7e-03 k3 |
| contact pheromone (ppk23/25) | +1.3e-03 k4 | +1.5e-04 k4 | -2.7e-03 k2 | -4.7e-04 k3 | -5.6e-03 k2 | -4.2e-05 k4 |
| ppk23 only (male CHC) | +1.2e-03 k3 | +5.2e-05 k2 | -2.1e-03 k2 | -3.0e-04 k3 | -5.1e-03 k2 | -3.1e-05 k4 |
| ppk25 only (female CHC) | +1.2e-03 k4 | +1.1e-04 k4 | -5.5e-04 k2 | -2.1e-04 k4 | +1.7e-03 k4 | -1.1e-05 k4 |
| cVA + contact pheromone | +1.9e-03 k4 | -7.7e-04 k3 | -2.8e-03 k2 | -5.0e-04 k3 | -5.6e-03 k2 | -2.2e-05 k3 |
| ppk25 + touch | +1.3e-03 k4 | +9.3e-05 k4 | +6.0e-04 k4 | -1.1e-03 k3 | +1.9e-03 k4 | -7.9e-03 k2 |
| all pheromones + contact + touch | +1.6e-03 k4 | -8.0e-04 k3 | -3.2e-03 k2 | -1.5e-03 k3 | -5.7e-03 k2 | -7.9e-03 k2 |

### `all_min1`: excitatory-only hops / w_exc_3 (upper bound of what can excite)

| source | P1/pC1 | pIP10 | aIPg | vpoEN/DN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / +1.6e-03 | 2 / +2.8e-04 | 2 / +1.4e-03 | 2 / +2.3e-05 | 2 / +2.4e-03 | 3 / +1.4e-05 |
| cVA-long (Or65a/DL3) | 2 / +9.0e-05 | 3 / +1.5e-06 | 3 / +1.2e-05 | 3 / +3.7e-07 | 2 / +1.5e-05 | 3 / +2.9e-08 |
| Or47b (VA1v) | 2 / +1.1e-04 | 2 / +1.6e-05 | 2 / +9.8e-05 | 3 / +5.1e-07 | 2 / +6.7e-05 | 3 / +1.4e-06 |
| Or88a (VA1d) | 2 / +4.9e-05 | 3 / +7.6e-07 | 3 / +8.2e-05 | 3 / +1.3e-07 | 2 / +8.5e-05 | 3 / +5.4e-08 |
| Or83c (DC3) | 2 / +4.2e-05 | 3 / +1.2e-06 | 3 / +4.8e-05 | 3 / +2.0e-07 | 2 / +5.7e-05 | 3 / +1.0e-07 |
| food odor | 2 / +5.4e-05 | 3 / +9.0e-06 | 2 / +6.0e-05 | 2 / +3.2e-06 | 2 / +3.4e-05 | 3 / +1.4e-06 |
| CO2 (V) | 2 / +2.3e-05 | 3 / +2.3e-06 | 2 / +9.0e-06 | 3 / +3.0e-06 | 2 / +3.8e-06 | 3 / +1.6e-07 |
| aversive odor (DA2/DL4) | 2 / +5.5e-05 | 2 / +3.5e-07 | 2 / +1.1e-05 | 3 / +4.7e-06 | 2 / +1.0e-05 | 3 / +3.7e-08 |
| song/sound (JO-A) | 1 / +3.9e-04 | 2 / +5.7e-05 | 2 / +2.1e-04 | 1 / +3.1e-03 | 2 / +2.0e-04 | 2 / +5.1e-06 |
| sound (JO-B) | 2 / +2.2e-04 | 2 / +1.8e-05 | 2 / +1.1e-04 | 2 / +3.4e-03 | 2 / +7.1e-05 | 2 / +7.4e-06 |
| wind/gravity (JO-CE) | 2 / +5.1e-04 | 2 / +1.3e-04 | 2 / +3.9e-04 | 2 / +4.0e-03 | 2 / +3.5e-04 | 2 / +1.9e-04 |
| touch (all head bristles) | 2 / +5.6e-04 | 2 / +1.7e-04 | 2 / +6.7e-04 | 2 / +3.3e-04 | 2 / +7.4e-04 | 2 / +5.7e-03 |
| touch (eye bristles) | 2 / +2.0e-04 | 2 / +7.2e-05 | 2 / +2.3e-04 | 2 / +1.7e-04 | 2 / +2.4e-04 | 2 / +9.5e-04 |
| sugar GRNs | 2 / +1.1e-04 | 2 / +4.6e-05 | 2 / +4.8e-05 | 2 / +7.5e-06 | 2 / +6.6e-05 | 2 / +2.3e-03 |
| cVA + food | 2 / +1.7e-03 | 2 / +2.9e-04 | 2 / +1.4e-03 | 2 / +2.7e-05 | 2 / +2.4e-03 | 3 / +1.6e-05 |
| cVA + touch | 2 / +2.2e-03 | 2 / +4.5e-04 | 2 / +2.1e-03 | 2 / +3.6e-04 | 2 / +3.1e-03 | 2 / +5.7e-03 |
| cVA + song | 1 / +2.0e-03 | 2 / +3.4e-04 | 2 / +1.6e-03 | 1 / +3.1e-03 | 2 / +2.6e-03 | 2 / +1.9e-05 |
| Or47b + song | 1 / +4.9e-04 | 2 / +7.3e-05 | 2 / +3.1e-04 | 1 / +3.1e-03 | 2 / +2.7e-04 | 2 / +6.5e-06 |
| Or47b + touch | 2 / +6.6e-04 | 2 / +1.8e-04 | 2 / +7.7e-04 | 2 / +3.4e-04 | 2 / +8.1e-04 | 2 / +5.7e-03 |
| food + touch | 2 / +6.1e-04 | 2 / +1.8e-04 | 2 / +7.3e-04 | 2 / +3.4e-04 | 2 / +7.7e-04 | 2 / +5.7e-03 |
| CO2 + touch | 2 / +5.8e-04 | 2 / +1.7e-04 | 2 / +6.8e-04 | 2 / +3.4e-04 | 2 / +7.4e-04 | 2 / +5.7e-03 |
| cVA + sugar | 2 / +1.7e-03 | 2 / +3.3e-04 | 2 / +1.4e-03 | 2 / +3.1e-05 | 2 / +2.4e-03 | 2 / +2.4e-03 |
| contact pheromone (ppk23/25) | 2 / +1.4e-03 | 2 / +3.5e-04 | 2 / +9.1e-04 | 2 / +3.1e-04 | 2 / +6.2e-04 | 2 / +7.9e-05 |
| ppk23 only (male CHC) | 2 / +7.5e-04 | 2 / +1.8e-04 | 2 / +5.9e-04 | 2 / +1.3e-04 | 2 / +3.9e-04 | 2 / +4.1e-05 |
| ppk25 only (female CHC) | 2 / +6.8e-04 | 2 / +1.7e-04 | 2 / +3.2e-04 | 2 / +1.9e-04 | 2 / +2.3e-04 | 2 / +3.8e-05 |
| cVA + contact pheromone | 2 / +3.0e-03 | 2 / +6.4e-04 | 2 / +2.3e-03 | 2 / +3.4e-04 | 2 / +3.0e-03 | 2 / +9.4e-05 |
| ppk25 + touch | 2 / +1.2e-03 | 2 / +3.4e-04 | 2 / +9.9e-04 | 2 / +5.2e-04 | 2 / +9.7e-04 | 2 / +5.8e-03 |
| all pheromones + contact + touch | 2 / +3.9e-03 | 2 / +8.2e-04 | 2 / +3.2e-03 | 2 / +6.7e-04 | 2 / +3.9e-03 | 2 / +5.8e-03 |

- reference touch (all head bristles) -> DNp13 reject: hops 2, 1,511,423 paths, w_max +3.7e-04 (k3), w_exc_3 +7.4e-04; top route `touch (all head bristles) > AN01A089 > PVLP204m > DNp13 reject` (+1.0e-04)
- reference sugar GRNs -> MN9: hops 2, 350,348 paths, w_max +1.7e-03 (k3), w_exc_3 +2.3e-03; top route `sugar GRNs > GNG042 > GNG015 > MN9` (+4.0e-04)
- largest decider |w_max| (single sensory groups): wind/gravity (JO-CE) -> vpoEN/DN accept, -4.1e-03 (k3) = 10.99x the weaker reference's.
- largest decider positive w_max (single sensory groups): contact pheromone (ppk23/25) -> P1/pC1 male, +1.3e-03 (k4) = 3.48x the weaker reference's.
- largest decider w_exc_3 (single sensory groups): wind/gravity (JO-CE) -> vpoEN/DN accept, +4.0e-03 = 5.39x the weaker reference's.
- 33 of 68 single-group sensory-decider pairs have a negative w_max (net inhibitory).

Strongest single sensory group per decider under `all_min1` (top route; share of that w_k):

- P1/pC1 male: contact pheromone (ppk23/25), w_max +1.3e-03 (k4), hops 2; `contact pheromone (ppk23/25) > AN09B017g > P1/pC1 male` -5.3e-04 (k2, 54% of w_2)
- pIP10 song cmd: cVA (Or67d/DA1), w_max -7.7e-04 (k3), hops 2; `cVA (Or67d/DA1) > DA1_lPN > LH007m > pIP10 song cmd` -5.8e-04 (k3, 74% of w_3)
- aIPg aggr: contact pheromone (ppk23/25), w_max -2.7e-03 (k2), hops 2; `contact pheromone (ppk23/25) > AN09B017c > aIPg aggr` -2.2e-03 (k2, 81% of w_2)
- vpoEN/DN accept: wind/gravity (JO-CE), w_max -4.1e-03 (k3), hops 2; `wind/gravity (JO-CE) > WED118 > vpoEN/DN accept` +2.6e-03 (k2, 118% of w_2)

## (b) Hunger / fullness neurons against SAG and pC1 (synapse counts from the raw table)

### `all_min1+eln0.25`: cells = hops / paths <= 3 / w_max

| source | role | n | out syn | per neuron | partners | exc | MN9 | feed MNs | PAM | PPL1 |
|---|---|---|---|---|---|---|---|---|---|---|
| fed (IPC tonic) | hunger/fullness | 16 | 218 | 14 | 103 | 1.00 | 2 / 458 / +3.9e-07 | 2 / 19,034 / -2.5e-07 | 2 / 70,845 / -1.4e-07 | 2 / 18,742 / -2.3e-07 |
| fed (DH44 tonic) | hunger/fullness | 6 | 542 | 90 | 162 | 1.00 | 2 / 1,088 / -4.5e-06 | 2 / 58,559 / +6.2e-06 | 2 / 111,813 / +4.4e-07 | 2 / 24,793 / +6.9e-07 |
| hungry (NPF tonic) | hunger/fullness | 4 | 9,258 | 2,314 | 3052 | 1.00 | 2 / 12,884 / -3.6e-06 | 2 / 235,007 / -8.9e-06 | 1 / 4,200,555 / +2.7e-05 | 1 / 952,769 / +3.7e-05 |
| SIFa tonic | hunger/fullness | 4 | 13,400 | 3,350 | 7166 | 1.00 | 2 / 25,750 / +3.0e-05 | 1 / 630,742 / +1.9e-04 | 1 / 3,466,905 / +9.1e-05 | 2 / 653,590 / +7.0e-05 |
| AstA tonic | hunger/fullness | 2 | 44,425 | 22,212 | 4042 | 0.00 | 2 / 5,898 / +5.9e-06 | 2 / 168,230 / -1.9e-05 | 1 / 4,901,703 / -6.8e-05 | 1 / 1,208,975 / -2.3e-04 |
| courting male (P1/pC1 tonic) | comparison | 148 | 234,500 | 1,584 | 5395 | 1.00 | 2 / 152,522 / +7.8e-05 | 2 / 2,547,877 / +5.9e-05 | 1 / 61,131,818 / +1.9e-03 | 1 / 13,287,295 / +1.5e-03 |
| sugar GRNs | reference | 162 | 71,637 | 442 | 1096 | 1.00 | 2 / 350,348 / +1.7e-03 | 1 / 9,974,416 / +4.4e-04 | 2 / 4,806,962 / +1.3e-04 | 2 / 716,063 / +1.9e-04 |

### `all_min1`: cells = hops / paths <= 3 / w_max

| source | role | n | out syn | per neuron | partners | exc | MN9 | feed MNs | PAM | PPL1 |
|---|---|---|---|---|---|---|---|---|---|---|
| fed (IPC tonic) | hunger/fullness | 16 | 218 | 14 | 103 | 1.00 | 2 / 458 / +3.9e-07 | 2 / 19,034 / -2.5e-07 | 2 / 70,845 / -1.4e-07 | 2 / 18,742 / -2.3e-07 |
| fed (DH44 tonic) | hunger/fullness | 6 | 542 | 90 | 162 | 1.00 | 2 / 1,088 / -4.5e-06 | 2 / 58,559 / +6.2e-06 | 2 / 111,813 / +4.4e-07 | 2 / 24,793 / +6.9e-07 |
| hungry (NPF tonic) | hunger/fullness | 4 | 9,258 | 2,314 | 3052 | 1.00 | 2 / 12,884 / -3.6e-06 | 2 / 235,007 / -8.8e-06 | 1 / 4,200,555 / +2.7e-05 | 1 / 952,769 / +3.7e-05 |
| SIFa tonic | hunger/fullness | 4 | 13,400 | 3,350 | 7166 | 1.00 | 2 / 25,750 / +3.0e-05 | 1 / 630,742 / +1.9e-04 | 1 / 3,466,905 / +7.6e-05 | 2 / 653,590 / +6.1e-05 |
| AstA tonic | hunger/fullness | 2 | 44,425 | 22,212 | 4042 | 0.00 | 2 / 5,898 / +5.9e-06 | 2 / 168,230 / -1.9e-05 | 1 / 4,901,703 / -6.8e-05 | 1 / 1,208,975 / -2.3e-04 |
| courting male (P1/pC1 tonic) | comparison | 148 | 234,500 | 1,584 | 5395 | 1.00 | 2 / 152,522 / +7.8e-05 | 2 / 2,547,877 / +5.9e-05 | 1 / 61,131,818 / +1.9e-03 | 1 / 13,287,295 / +1.5e-03 |
| sugar GRNs | reference | 162 | 71,637 | 442 | 1096 | 1.00 | 2 / 350,348 / +1.7e-03 | 1 / 9,974,416 / +4.4e-04 | 2 / 4,806,962 / +1.3e-04 | 2 / 716,063 / +1.9e-04 |

Top postsynaptic types (synapses):

- fed (IPC tonic): IPC (86), DH44 (23), DMS (9), hDeltaE (6), PRW073 (5)
- fed (DH44 tonic): DH44 (57), PRW060 (45), IPC (35), CB4125 (34), SMP261 (26)
- hungry (NPF tonic): AVLP001 (256), AVLP076 (244), PVLP010 (184), AVLP542 (116), AVLP201 (114)
- SIFa tonic: lLN2P_a (391), LT33 (367), lLN2P_b (347), lLN2P_c (318), lLN2T_c (280)
- AstA tonic: (central/) (869), CL071_b (598), CL269 (482), CL257 (479), AVLP210 (449)
- courting male (P1/pC1 tonic): pC1_18b (4344), SIP104m (3719), AVLP749m (3714), SIP106m (3527), mAL_m8 (3519)
- sugar GRNs: GNG016 (4431), GNG038 (2414), GNG087 (2347), LB3c (2303), GNG042 (1937)

Neuroendocrine cells (IPC, DH44, ...) act mostly by hormone release, which W does not contain; the rows above are their synaptic outputs only.

## (c) Known-sign flips

No `known_nt` column in this dataset: signs=known applies nothing.

## (d) Antennal-lobe local neurons (cell_class ALLN) by predicted transmitter and sign

420 ALLN. eLN (positive row sign, what an eLN scale multiplies): 206 under the Shiu signs, by top_nt {'acetylcholine': 137, 'unclear': 67, 'octopamine': 2}; 206 under the known signs, by top_nt {'acetylcholine': 137, 'unclear': 67, 'octopamine': 2}.

| top_nt | sign_shiu | sign_known | n | out_syn | out_syn_to_alpn |
|---|---|---|---|---|---|
| acetylcholine | + | + | 137 | 701,542 | 216,510 |
| gaba | - | - | 115 | 399,801 | 134,948 |
| glutamate | - | - | 99 | 56,106 | 29,114 |
| octopamine | + | + | 2 | 7,704 | 2,158 |
| unclear | + | + | 67 | 230,501 | 73,239 |

Files: `structure_paths_malecns.csv`, `structure_routes_malecns.csv`, `structure_state_malecns.csv`, `structure_aln_malecns.csv`
