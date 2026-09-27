# Structure probe: flywire (no simulation)

2026-09-27 01:29. `experiments/edge/structure_probe.py --dataset flywire`. Raw load: Connectome(flywire/shiu_min1: 139248 neurons, 15090883 connections, 54490416 synapses, w_syn_scale=1.000, signs=shiu). Variants: `shiu_min1+known+eln0.25` (the paper's model), `shiu_min1+eln0.25` (the published signs, the paper's eLN x0.25), `shiu_min1` (the published model). 61 s.

Definitions (module docstring): hops over all connections; paths = simple neuron-level paths of length <= 3; w_k = mean over the target neurons of x_k = x_{k-1} @ Wn from x_0 = 1 on the sources, Wn = W / column sum of |W| (w_1 = signed fraction of the targets' input synapses coming from the sources). `w_max` = the w_k (k = 1..4) with the largest |w_k|, shown as `value kK`.

## Checks

- known-sign flips: 11,010 recomputed here; apply_model_options 11,010; connectome.py docstring and paper: 11,010.
- eLN (ALLN with a positive row sign): 166 under the Shiu signs, 150 under the known signs; known+eln0.25: 150, shiu+eln0.25: 166 (connectome.py docstring: 150).
- routes: the exact chains of k = 1..3 add up to w_k (max relative error 7.0e-13); forward and backward w_k agree (max relative error 6.3e-13); every combination's w_k is the sum of its single groups' (max relative error 1.7e-14).

## (a) Sensory input -> deciders

### Hops / simple paths within 3 hops (all connections; the same in every variant)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / 5,170 | 2 / 53,744 | 2 / 33,633 | 3 / 42,469 | 3 / 15,494 | 3 / 15,935 | 3 / 9,365 | 3 / 1,714 |
| cVA-long (Or65a/DL3) | 3 / 827 | 3 / 4,268 | 3 / 2,656 | 3 / 2,273 | 3 / 2,461 | 3 / 1,102 | 3 / 1,461 | 3 / 121 |
| Or47b (VA1v) | 3 / 1,143 | 3 / 5,546 | 3 / 8,048 | 2 / 32,151 | 3 / 4,607 | 3 / 3,601 | 3 / 3,859 | 3 / 598 |
| Or88a (VA1d) | 2 / 1,070 | 3 / 4,790 | 2 / 7,004 | 2 / 32,053 | 3 / 4,500 | 3 / 2,789 | 3 / 3,924 | 3 / 449 |
| Or83c (DC3) | 3 / 903 | 2 / 4,239 | 2 / 3,902 | 2 / 6,590 | 3 / 1,878 | 3 / 1,640 | 3 / 916 | 3 / 195 |
| all pheromone ORNs | 2 / 9,113 | 2 / 72,587 | 2 / 55,243 | 2 / 115,536 | 3 / 28,940 | 3 / 25,067 | 3 / 19,525 | 3 / 3,077 |
| food odor | 2 / 12,986 | 2 / 41,181 | 2 / 40,269 | 3 / 36,295 | 2 / 13,874 | 3 / 14,480 | 2 / 3,298 | 3 / 423 |
| CO2 (V) | 2 / 1,962 | 3 / 7,948 | 2 / 10,484 | 3 / 13,322 | 3 / 2,328 | 3 / 9,585 | 3 / 1,491 | 3 / 68 |
| aversive odor (DA2/DL4) | 3 / 1,490 | 3 / 4,481 | 3 / 4,477 | 3 / 3,271 | 2 / 1,713 | 3 / 2,527 | 3 / 304 | 3 / 13 |
| song/sound (JO-A) | 3 / 885 | 2 / 10,370 | 2 / 43,674 | 2 / 86,461 | 1 / 211,800 | 3 / 3,344 | 2 / 42,579 | 2 / 3,371 |
| sound (JO-B) | 3 / 277 | 2 / 3,490 | 2 / 26,196 | 2 / 67,688 | 2 / 162,063 | 3 / 1,901 | 2 / 23,962 | 3 / 2,984 |
| wind/gravity (JO-CE) | 3 / 1,392 | 2 / 12,177 | 2 / 100,336 | 2 / 219,582 | 2 / 325,091 | 3 / 8,042 | 2 / 58,775 | 2 / 11,042 |
| touch (all head bristles) | 2 / 38,385 | 2 / 89,162 | 2 / 437,983 | 2 / 1,245,106 | 2 / 875,091 | 2 / 122,089 | 2 / 436,741 | 2 / 627,689 |
| touch (antennal bristles) | 3 / 2,666 | 3 / 6,838 | 3 / 42,434 | 2 / 115,735 | 2 / 81,035 | 2 / 10,228 | 2 / 35,268 | 2 / 32,378 |
| touch (eye bristles) | 2 / 22,756 | 2 / 48,770 | 2 / 260,333 | 2 / 769,545 | 2 / 549,067 | 2 / 69,722 | 2 / 280,795 | 2 / 231,282 |
| sugar GRNs | 2 / 9,343 | 2 / 34,927 | 2 / 32,032 | 2 / 36,264 | 2 / 15,227 | 2 / 52,984 | 2 / 9,293 | 2 / 106,050 |
| bitter GRNs | 2 / 13,169 | 2 / 40,761 | 2 / 36,444 | 2 / 38,757 | 2 / 11,867 | 2 / 61,141 | 3 / 9,387 | 2 / 34,159 |
| cVA + food | 2 / 18,156 | 2 / 94,925 | 2 / 73,902 | 3 / 78,764 | 2 / 29,368 | 3 / 30,415 | 2 / 12,663 | 3 / 2,137 |
| cVA + touch | 2 / 43,555 | 2 / 142,906 | 2 / 471,616 | 2 / 1,287,575 | 2 / 890,585 | 2 / 138,024 | 2 / 446,106 | 2 / 629,403 |
| cVA + song | 2 / 6,055 | 2 / 64,114 | 2 / 77,307 | 2 / 128,930 | 1 / 227,294 | 3 / 19,279 | 2 / 51,944 | 2 / 5,085 |
| Or47b + song | 3 / 2,028 | 2 / 15,916 | 2 / 51,722 | 2 / 118,612 | 1 / 216,407 | 3 / 6,945 | 2 / 46,438 | 2 / 3,969 |
| Or47b + touch | 2 / 39,528 | 2 / 94,708 | 2 / 446,031 | 2 / 1,277,257 | 2 / 879,698 | 2 / 125,690 | 2 / 440,600 | 2 / 628,287 |
| food + touch | 2 / 51,371 | 2 / 130,343 | 2 / 478,252 | 2 / 1,281,401 | 2 / 888,965 | 2 / 136,569 | 2 / 440,039 | 2 / 628,112 |
| CO2 + touch | 2 / 40,347 | 2 / 97,110 | 2 / 448,467 | 2 / 1,258,428 | 2 / 877,419 | 2 / 131,674 | 2 / 438,232 | 2 / 627,757 |
| pheromones + song + touch | 2 / 48,383 | 2 / 172,119 | 2 / 536,900 | 2 / 1,447,103 | 1 / 1,115,831 | 2 / 150,500 | 2 / 498,845 | 2 / 634,137 |
| cVA + sugar | 2 / 14,513 | 2 / 88,671 | 2 / 65,665 | 2 / 78,733 | 2 / 30,721 | 2 / 68,919 | 2 / 18,658 | 2 / 107,764 |

### `shiu_min1+known+eln0.25`: strongest signed propagated weight w_max (and its k)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | -5.5e-05 k3 | +1.4e-03 k3 | +1.7e-03 k2 | +3.3e-04 k3 | +9.4e-05 k4 | +1.6e-04 k3 | +1.2e-04 k3 | +2.7e-05 k4 |
| cVA-long (Or65a/DL3) | -5.6e-06 k4 | +8.4e-05 k3 | -7.8e-06 k4 | -2.1e-06 k3 | -5.1e-06 k4 | +3.3e-05 k3 | +7.9e-06 k3 | -1.3e-06 k4 |
| Or47b (VA1v) | +5.6e-06 k4 | -3.7e-05 k4 | -8.0e-06 k4 | -1.2e-04 k3 | +1.6e-05 k4 | -1.9e-05 k4 | -2.1e-05 k4 | -6.8e-07 k4 |
| Or88a (VA1d) | +3.1e-06 k4 | -3.8e-05 k4 | -4.1e-06 k3 | -1.2e-04 k3 | +1.3e-05 k4 | -3.4e-05 k4 | -1.4e-05 k4 | -4.2e-06 k4 |
| Or83c (DC3) | -6.9e-06 k4 | +2.0e-04 k3 | -2.0e-05 k3 | -4.9e-06 k3 | -7.5e-06 k4 | -6.7e-05 k4 | +1.5e-05 k4 | +2.3e-07 k3 |
| all pheromone ORNs | -5.4e-05 k3 | +1.7e-03 k3 | +1.7e-03 k2 | -1.4e-04 k2 | +1.1e-04 k4 | +1.5e-04 k3 | +1.3e-04 k3 | +2.1e-05 k4 |
| food odor | -7.3e-05 k4 | -1.5e-04 k4 | -9.9e-05 k4 | -2.6e-05 k4 | -1.6e-06 k3 | -1.9e-04 k4 | +7.1e-06 k3 | +4.1e-07 k4 |
| CO2 (V) | -1.3e-04 k4 | +4.3e-05 k3 | -3.0e-05 k4 | +2.3e-05 k3 | -2.3e-06 k4 | +2.2e-04 k3 | -4.7e-06 k3 | -7.6e-07 k4 |
| aversive odor (DA2/DL4) | -5.5e-05 k4 | -4.7e-05 k4 | -2.8e-05 k3 | -7.5e-06 k4 | -5.0e-06 k4 | -1.1e-04 k4 | +2.5e-06 k4 | -4.5e-09 k4 |
| song/sound (JO-A) | +1.8e-06 k3 | +7.1e-06 k3 | +7.4e-06 k2 | +3.1e-05 k3 | -6.7e-04 k2 | +2.5e-06 k4 | +6.1e-05 k2 | +3.6e-05 k3 |
| sound (JO-B) | -2.3e-06 k4 | +3.0e-05 k4 | -2.0e-05 k4 | -3.6e-05 k2 | -8.1e-04 k3 | +1.6e-06 k3 | -7.7e-05 k4 | +1.3e-05 k4 |
| wind/gravity (JO-CE) | +3.4e-06 k3 | +1.3e-05 k4 | -1.1e-04 k4 | -4.0e-05 k2 | -1.5e-03 k3 | +8.5e-06 k4 | -1.7e-04 k4 | -3.4e-05 k3 |
| touch (all head bristles) | -1.1e-04 k2 | -5.1e-05 k3 | +2.2e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +8.7e-05 k4 | +1.5e-03 k3 | -8.8e-03 k2 |
| touch (antennal bristles) | +3.3e-05 k3 | -3.1e-06 k3 | -1.3e-05 k4 | +1.1e-04 k3 | -3.7e-04 k3 | +8.8e-06 k4 | +9.1e-05 k3 | +8.7e-05 k3 |
| touch (eye bristles) | -1.8e-05 k4 | -9.0e-06 k4 | -4.2e-05 k4 | +4.6e-04 k3 | -1.9e-03 k3 | +2.3e-05 k4 | +5.8e-04 k3 | +1.4e-03 k3 |
| sugar GRNs | -5.7e-05 k4 | -1.6e-05 k4 | +7.4e-06 k4 | -2.9e-05 k3 | +3.5e-05 k2 | +2.4e-04 k3 | -5.5e-05 k4 | +1.7e-03 k3 |
| bitter GRNs | -2.4e-04 k4 | -4.1e-05 k2 | -1.9e-05 k4 | +3.3e-05 k3 | +1.3e-05 k2 | -4.6e-04 k3 | -1.6e-05 k3 | -2.1e-04 k3 |
| cVA + food | -1.1e-04 k4 | +1.5e-03 k3 | +1.7e-03 k2 | +3.2e-04 k3 | +9.6e-05 k4 | +2.9e-04 k3 | +1.3e-04 k3 | +2.7e-05 k4 |
| cVA + touch | -1.1e-04 k2 | +1.4e-03 k3 | +1.7e-03 k2 | +1.8e-03 k3 | -4.1e-03 k3 | +2.2e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + song | -5.4e-05 k3 | +1.4e-03 k3 | +1.7e-03 k2 | +3.7e-04 k3 | -6.7e-04 k2 | +1.6e-04 k3 | +1.1e-04 k3 | +4.4e-05 k3 |
| Or47b + song | +5.5e-06 k4 | -4.4e-05 k4 | -1.5e-05 k4 | -9.1e-05 k3 | -6.7e-04 k2 | -1.6e-05 k4 | -7.1e-05 k4 | +3.6e-05 k3 |
| Or47b + touch | -1.1e-04 k2 | -4.4e-05 k4 | +2.3e-04 k3 | +1.3e-03 k3 | -4.1e-03 k3 | +6.8e-05 k4 | +1.5e-03 k3 | -8.8e-03 k2 |
| food + touch | -1.4e-04 k2 | -1.5e-04 k4 | +2.4e-04 k3 | +1.4e-03 k3 | -4.1e-03 k3 | +2.0e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| CO2 + touch | -1.2e-04 k4 | +1.2e-05 k4 | +2.3e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +2.9e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| pheromones + song + touch | -1.1e-04 k2 | +1.7e-03 k3 | +1.7e-03 k2 | +1.6e-03 k3 | -4.2e-03 k3 | +2.1e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + sugar | -9.8e-05 k4 | +1.4e-03 k3 | +1.7e-03 k2 | +3.1e-04 k3 | +9.6e-05 k4 | +3.9e-04 k3 | +1.0e-04 k3 | +1.8e-03 k4 |

### `shiu_min1+known+eln0.25`: excitatory-only hops / w_exc_3 (upper bound of what can excite)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / +1.3e-05 | 2 / +1.4e-03 | 2 / +6.4e-04 | 3 / +3.4e-04 | 3 / +4.6e-05 | 3 / +1.4e-04 | 3 / +4.3e-05 | 3 / +1.2e-05 |
| cVA-long (Or65a/DL3) | 3 / +1.9e-06 | 3 / +8.8e-05 | 3 / +9.1e-06 | 3 / +1.6e-07 | 3 / +3.7e-06 | 3 / +3.4e-05 | 3 / +8.5e-06 | 3 / +1.1e-09 |
| Or47b (VA1v) | 3 / +1.6e-06 | 3 / +2.0e-05 | 3 / +1.8e-05 | 3 / +4.3e-06 | 3 / +1.6e-08 | 3 / +1.4e-05 | 3 / +7.5e-07 | 3 / +5.6e-07 |
| Or88a (VA1d) | 2 / +4.3e-07 | 3 / +6.9e-06 | 2 / +2.1e-06 | 3 / +1.2e-06 | 3 / +1.0e-07 | 3 / +2.4e-06 | 3 / +3.2e-07 | 4 / 0 |
| Or83c (DC3) | 3 / +1.5e-06 | 2 / +2.1e-04 | 2 / +1.8e-05 | 3 / +4.4e-06 | 3 / +1.3e-06 | 3 / +1.1e-05 | 3 / +1.3e-05 | 3 / +3.0e-07 |
| all pheromone ORNs | 2 / +1.8e-05 | 2 / +1.8e-03 | 2 / +6.8e-04 | 3 / +3.5e-04 | 3 / +5.1e-05 | 3 / +2.0e-04 | 3 / +6.5e-05 | 3 / +1.3e-05 |
| food odor | 2 / +2.4e-05 | 2 / +1.4e-04 | 2 / +6.4e-05 | 3 / +2.2e-05 | 2 / +6.6e-06 | 3 / +2.2e-04 | 2 / +8.2e-06 | 3 / +4.7e-08 |
| CO2 (V) | 2 / +2.8e-06 | 3 / +6.5e-05 | 2 / +1.8e-05 | 3 / +2.8e-05 | 3 / +1.3e-06 | 3 / +3.5e-04 | 3 / +4.5e-06 | 3 / +9.1e-09 |
| aversive odor (DA2/DL4) | 3 / +6.0e-07 | 3 / +1.0e-05 | 3 / +4.4e-06 | 3 / +2.0e-06 | 3 / +1.5e-07 | 3 / +4.5e-05 | 3 / +5.6e-07 | 4 / 0 |
| song/sound (JO-A) | 3 / +7.6e-07 | 2 / +2.2e-05 | 2 / +7.1e-05 | 2 / +4.8e-05 | 1 / +9.2e-04 | 3 / +2.6e-06 | 2 / +2.6e-04 | 3 / +2.9e-06 |
| sound (JO-B) | 3 / +7.7e-08 | 2 / +1.9e-06 | 2 / +2.8e-05 | 2 / +4.5e-05 | 2 / +1.5e-03 | 3 / +1.1e-06 | 2 / +1.0e-04 | 3 / +3.4e-06 |
| wind/gravity (JO-CE) | 3 / +8.8e-07 | 2 / +1.3e-05 | 2 / +1.0e-04 | 2 / +8.6e-05 | 2 / +1.6e-03 | 3 / +5.9e-06 | 2 / +1.8e-04 | 2 / +2.4e-05 |
| touch (all head bristles) | 3 / +5.1e-05 | 2 / +7.1e-05 | 2 / +3.5e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +1.8e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| touch (antennal bristles) | 3 / +5.6e-06 | 3 / +9.3e-06 | 3 / +3.4e-05 | 2 / +1.2e-04 | 2 / +1.2e-04 | 2 / +1.0e-05 | 2 / +2.3e-04 | 2 / +2.4e-04 |
| touch (eye bristles) | 3 / +2.3e-05 | 3 / +3.1e-05 | 3 / +1.5e-04 | 2 / +5.6e-04 | 2 / +4.2e-04 | 2 / +4.3e-05 | 2 / +1.4e-03 | 2 / +1.4e-03 |
| sugar GRNs | 2 / +2.3e-05 | 2 / +3.4e-05 | 2 / +2.4e-05 | 2 / +2.0e-05 | 2 / +3.2e-05 | 2 / +7.0e-04 | 2 / +2.3e-05 | 2 / +1.7e-03 |
| bitter GRNs | 2 / +2.6e-04 | 2 / +1.2e-04 | 2 / +5.9e-05 | 3 / +2.0e-05 | 2 / +1.3e-05 | 2 / +6.6e-04 | 3 / +6.2e-06 | 2 / +6.6e-05 |
| cVA + food | 2 / +3.6e-05 | 2 / +1.6e-03 | 2 / +7.0e-04 | 3 / +3.6e-04 | 2 / +5.2e-05 | 3 / +3.6e-04 | 2 / +5.2e-05 | 3 / +1.2e-05 |
| cVA + touch | 2 / +6.4e-05 | 2 / +1.5e-03 | 2 / +9.9e-04 | 2 / +1.7e-03 | 2 / +1.1e-03 | 2 / +3.2e-04 | 2 / +3.4e-03 | 2 / +8.9e-03 |
| cVA + song | 2 / +1.3e-05 | 2 / +1.5e-03 | 2 / +7.1e-04 | 2 / +3.8e-04 | 1 / +9.7e-04 | 3 / +1.4e-04 | 2 / +3.0e-04 | 3 / +1.5e-05 |
| Or47b + song | 3 / +2.4e-06 | 2 / +4.2e-05 | 2 / +8.9e-05 | 2 / +5.2e-05 | 1 / +9.2e-04 | 3 / +1.6e-05 | 2 / +2.6e-04 | 3 / +3.5e-06 |
| Or47b + touch | 3 / +5.3e-05 | 2 / +9.1e-05 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +2.0e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| food + touch | 2 / +7.5e-05 | 2 / +2.1e-04 | 2 / +4.1e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +4.0e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| CO2 + touch | 2 / +5.4e-05 | 2 / +1.4e-04 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +5.4e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| pheromones + song + touch | 2 / +7.0e-05 | 2 / +1.9e-03 | 2 / +1.1e-03 | 2 / +1.7e-03 | 1 / +2.0e-03 | 2 / +3.9e-04 | 2 / +3.7e-03 | 2 / +8.9e-03 |
| cVA + sugar | 2 / +3.5e-05 | 2 / +1.5e-03 | 2 / +6.6e-04 | 2 / +3.6e-04 | 2 / +7.8e-05 | 2 / +8.4e-04 | 2 / +6.6e-05 | 2 / +1.7e-03 |

- reference touch (all head bristles) -> DNp13 reject: hops 2, 436,741 paths, w_max +1.5e-03 (k3), w_exc_3 +3.3e-03; top route `touch (all head bristles) > AN_AVLP_GNG_18 > AVLP340 > DNp13 reject` (+1.2e-03)
- reference sugar GRNs -> MN9: hops 2, 106,050 paths, w_max +1.7e-03 (k3), w_exc_3 +1.7e-03; top route `sugar GRNs > CB0118 > CB0862 > MN9` (+3.9e-04)
- largest decider |w_max| (single sensory groups): touch (all head bristles) -> vpoEN/DN accept, -4.1e-03 (k3) = 2.78x the weaker reference's.
- largest decider positive w_max (single sensory groups): all pheromone ORNs -> pC1d/e aggr, +1.7e-03 (k2) = 1.16x the weaker reference's.
- largest decider w_exc_3 (single sensory groups): all pheromone ORNs -> pC1b/c, +1.8e-03 = 1.03x the weaker reference's.
- 60 of 102 single-group sensory-decider pairs have a negative w_max (net inhibitory).

Strongest single sensory group per decider under `shiu_min1+known+eln0.25` (top route; share of that w_k):

- pC1a recept: bitter GRNs, w_max -2.4e-04 (k4), hops 2; `bitter GRNs > CB0638 > AN_FLA_SMP_2 > pC1a recept` +2.1e-04 (k3, 178% of w_3)
- pC1b/c: all pheromone ORNs, w_max +1.7e-03 (k3), hops 2; `all pheromone ORNs > DA1_lPN > CB0997 > pC1b/c` +9.2e-04 (k3, 54% of w_3)
- pC1d/e aggr: all pheromone ORNs, w_max +1.7e-03 (k2), hops 2; `all pheromone ORNs > M_lvPNm45 > pC1d/e aggr` +1.7e-03 (k2, 99% of w_2)
- aIPg aggr: touch (all head bristles), w_max +1.5e-03 (k3), hops 2; `touch (all head bristles) > CB0619 > AOTU064 > aIPg aggr` +5.8e-04 (k3, 40% of w_3)
- vpoEN/DN accept: touch (all head bristles), w_max -4.1e-03 (k3), hops 2; `touch (all head bristles) > CB0443 > CB1484 > vpoEN/DN accept` -8.4e-04 (k3, 21% of w_3)
- oviDN egg: bitter GRNs, w_max -4.6e-04 (k3), hops 2; `bitter GRNs > CB0159 > SA_VTV_5 > mAL_f2 > oviDN egg` +6.7e-04 (k4, 153% of w_4)

### `shiu_min1+eln0.25`: strongest signed propagated weight w_max (and its k)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | -6.2e-05 k3 | +1.6e-03 k3 | +1.7e-03 k2 | +3.4e-04 k3 | +1.0e-04 k4 | +1.7e-04 k3 | +1.3e-04 k3 | +2.8e-05 k4 |
| cVA-long (Or65a/DL3) | -7.6e-06 k4 | +9.7e-05 k3 | +8.5e-07 k4 | -7.0e-06 k4 | -5.7e-06 k4 | +3.8e-05 k3 | +9.3e-06 k4 | -1.2e-06 k4 |
| Or47b (VA1v) | +6.1e-06 k4 | -2.1e-05 k4 | +9.6e-06 k3 | -1.4e-04 k3 | +1.7e-05 k4 | -2.0e-05 k4 | -2.4e-05 k4 | -6.4e-07 k4 |
| Or88a (VA1d) | +2.5e-06 k4 | -2.2e-05 k4 | +4.6e-06 k4 | -1.3e-04 k3 | +1.3e-05 k4 | -3.7e-05 k4 | -1.4e-05 k4 | -4.3e-06 k4 |
| Or83c (DC3) | -7.4e-06 k4 | +2.1e-04 k3 | -2.0e-05 k3 | -6.6e-06 k3 | -7.8e-06 k4 | -7.1e-05 k4 | +1.7e-05 k4 | +2.4e-07 k4 |
| all pheromone ORNs | -6.0e-05 k3 | +1.9e-03 k3 | +1.7e-03 k2 | -1.5e-04 k2 | +1.2e-04 k4 | +1.6e-04 k3 | +1.4e-04 k3 | +2.2e-05 k4 |
| food odor | -8.0e-05 k4 | -1.4e-04 k4 | -8.6e-05 k4 | -3.2e-05 k4 | -1.4e-06 k3 | -1.9e-04 k4 | +7.2e-06 k3 | +7.5e-07 k4 |
| CO2 (V) | -1.3e-04 k4 | +4.3e-05 k3 | -3.1e-05 k4 | +2.3e-05 k3 | -2.4e-06 k4 | +2.2e-04 k3 | -4.6e-06 k3 | -7.7e-07 k4 |
| aversive odor (DA2/DL4) | -5.7e-05 k4 | -3.6e-05 k4 | -2.7e-05 k3 | -9.2e-06 k4 | -5.1e-06 k4 | -1.1e-04 k4 | +3.2e-06 k4 | +2.0e-08 k4 |
| song/sound (JO-A) | +1.8e-06 k3 | +7.1e-06 k3 | +7.4e-06 k2 | +3.1e-05 k3 | -6.7e-04 k2 | +2.5e-06 k4 | +6.1e-05 k2 | +3.8e-05 k3 |
| sound (JO-B) | -2.3e-06 k4 | +3.0e-05 k4 | -2.0e-05 k4 | -3.6e-05 k2 | -8.1e-04 k3 | +1.6e-06 k3 | -7.7e-05 k4 | +1.4e-05 k4 |
| wind/gravity (JO-CE) | +3.4e-06 k3 | +1.3e-05 k4 | -1.1e-04 k4 | -4.0e-05 k2 | -1.5e-03 k3 | +8.1e-06 k4 | -1.7e-04 k4 | -3.4e-05 k3 |
| touch (all head bristles) | -1.1e-04 k2 | -5.1e-05 k3 | +2.2e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +7.5e-05 k4 | +1.5e-03 k3 | -8.8e-03 k2 |
| touch (antennal bristles) | +3.3e-05 k3 | -3.2e-06 k3 | -1.2e-05 k4 | +1.1e-04 k3 | -3.7e-04 k3 | +7.3e-06 k4 | +9.1e-05 k3 | +8.7e-05 k3 |
| touch (eye bristles) | -1.8e-05 k4 | -1.0e-05 k4 | -4.2e-05 k4 | +4.6e-04 k3 | -1.9e-03 k3 | +2.0e-05 k4 | +5.7e-04 k3 | +1.4e-03 k3 |
| sugar GRNs | -5.9e-05 k4 | -1.6e-05 k4 | +7.6e-06 k4 | -2.9e-05 k3 | +3.5e-05 k2 | +2.4e-04 k3 | -5.7e-05 k4 | +1.7e-03 k3 |
| bitter GRNs | -2.4e-04 k4 | -4.1e-05 k2 | -2.1e-05 k4 | +3.3e-05 k3 | +1.3e-05 k2 | -4.8e-04 k3 | -1.7e-05 k3 | -2.1e-04 k3 |
| cVA + food | -1.3e-04 k4 | +1.7e-03 k3 | +1.8e-03 k2 | +3.2e-04 k3 | +1.1e-04 k4 | +3.1e-04 k3 | +1.4e-04 k3 | +2.9e-05 k4 |
| cVA + touch | -1.1e-04 k2 | +1.5e-03 k3 | +1.7e-03 k2 | +1.8e-03 k3 | -4.1e-03 k3 | +2.3e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + song | -6.0e-05 k3 | +1.6e-03 k3 | +1.7e-03 k2 | +3.7e-04 k3 | -6.7e-04 k2 | +1.7e-04 k3 | +1.1e-04 k3 | +4.7e-05 k3 |
| Or47b + song | +6.0e-06 k4 | -2.7e-05 k4 | +1.7e-05 k3 | -1.0e-04 k3 | -6.7e-04 k2 | -1.7e-05 k4 | -7.5e-05 k4 | +3.9e-05 k3 |
| Or47b + touch | -1.1e-04 k2 | -3.9e-05 k3 | +2.3e-04 k3 | +1.3e-03 k3 | -4.1e-03 k3 | +6.1e-05 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| food + touch | -1.4e-04 k2 | -1.5e-04 k4 | +2.5e-04 k3 | +1.4e-03 k3 | -4.1e-03 k3 | +2.0e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| CO2 + touch | -1.2e-04 k4 | +8.1e-06 k4 | +2.2e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +2.8e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| pheromones + song + touch | -1.1e-04 k2 | +1.9e-03 k3 | +1.8e-03 k2 | +1.5e-03 k3 | -4.2e-03 k3 | +2.2e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + sugar | -1.1e-04 k4 | +1.6e-03 k3 | +1.7e-03 k2 | +3.1e-04 k3 | +1.1e-04 k4 | +4.0e-04 k3 | +1.1e-04 k3 | +1.8e-03 k4 |

### `shiu_min1+eln0.25`: excitatory-only hops / w_exc_3 (upper bound of what can excite)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / +1.3e-05 | 2 / +1.6e-03 | 2 / +7.1e-04 | 3 / +3.5e-04 | 3 / +4.7e-05 | 3 / +1.5e-04 | 3 / +4.7e-05 | 3 / +1.2e-05 |
| cVA-long (Or65a/DL3) | 3 / +2.2e-06 | 3 / +1.0e-04 | 3 / +1.1e-05 | 3 / +1.8e-07 | 3 / +4.4e-06 | 3 / +3.8e-05 | 3 / +9.7e-06 | 3 / +1.1e-09 |
| Or47b (VA1v) | 3 / +1.9e-06 | 3 / +2.2e-05 | 3 / +2.0e-05 | 3 / +4.6e-06 | 3 / +3.2e-08 | 3 / +1.4e-05 | 3 / +8.0e-07 | 3 / +5.9e-07 |
| Or88a (VA1d) | 2 / +5.0e-07 | 3 / +7.8e-06 | 2 / +2.6e-06 | 3 / +1.4e-06 | 3 / +5.9e-07 | 3 / +2.7e-06 | 3 / +3.4e-07 | 4 / 0 |
| Or83c (DC3) | 3 / +1.6e-06 | 2 / +2.2e-04 | 2 / +1.9e-05 | 3 / +4.6e-06 | 3 / +1.6e-06 | 3 / +1.1e-05 | 3 / +1.3e-05 | 3 / +3.2e-07 |
| all pheromone ORNs | 2 / +1.9e-05 | 2 / +2.0e-03 | 2 / +7.7e-04 | 3 / +3.7e-04 | 3 / +5.4e-05 | 3 / +2.2e-04 | 3 / +7.1e-05 | 3 / +1.3e-05 |
| food odor | 2 / +2.5e-05 | 2 / +1.4e-04 | 2 / +6.7e-05 | 3 / +2.2e-05 | 2 / +7.0e-06 | 3 / +2.2e-04 | 2 / +8.4e-06 | 3 / +4.8e-08 |
| CO2 (V) | 2 / +3.0e-06 | 3 / +6.6e-05 | 2 / +1.8e-05 | 3 / +2.8e-05 | 3 / +1.3e-06 | 3 / +3.5e-04 | 3 / +4.5e-06 | 3 / +9.2e-09 |
| aversive odor (DA2/DL4) | 3 / +6.6e-07 | 3 / +1.0e-05 | 3 / +4.7e-06 | 3 / +2.0e-06 | 2 / +1.9e-07 | 3 / +4.6e-05 | 3 / +5.8e-07 | 4 / 0 |
| song/sound (JO-A) | 3 / +7.8e-07 | 2 / +2.2e-05 | 2 / +7.1e-05 | 2 / +4.8e-05 | 1 / +9.2e-04 | 3 / +2.6e-06 | 2 / +2.6e-04 | 2 / +4.8e-06 |
| sound (JO-B) | 3 / +7.7e-08 | 2 / +1.9e-06 | 2 / +2.8e-05 | 2 / +4.5e-05 | 2 / +1.5e-03 | 3 / +1.1e-06 | 2 / +1.0e-04 | 3 / +3.4e-06 |
| wind/gravity (JO-CE) | 3 / +8.8e-07 | 2 / +1.3e-05 | 2 / +1.0e-04 | 2 / +8.7e-05 | 2 / +1.6e-03 | 3 / +6.0e-06 | 2 / +1.8e-04 | 2 / +2.4e-05 |
| touch (all head bristles) | 3 / +5.1e-05 | 2 / +7.1e-05 | 2 / +3.5e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +1.8e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| touch (antennal bristles) | 3 / +5.6e-06 | 3 / +9.3e-06 | 3 / +3.4e-05 | 2 / +1.2e-04 | 2 / +1.2e-04 | 2 / +9.8e-06 | 2 / +2.3e-04 | 2 / +2.4e-04 |
| touch (eye bristles) | 3 / +2.3e-05 | 3 / +3.1e-05 | 3 / +1.5e-04 | 2 / +5.6e-04 | 2 / +4.3e-04 | 2 / +4.3e-05 | 2 / +1.4e-03 | 2 / +1.4e-03 |
| sugar GRNs | 2 / +2.3e-05 | 2 / +3.4e-05 | 2 / +2.4e-05 | 2 / +2.0e-05 | 2 / +3.2e-05 | 2 / +7.0e-04 | 2 / +2.2e-05 | 2 / +1.7e-03 |
| bitter GRNs | 2 / +2.6e-04 | 2 / +1.2e-04 | 2 / +5.9e-05 | 3 / +2.0e-05 | 2 / +1.3e-05 | 2 / +6.4e-04 | 3 / +6.2e-06 | 2 / +6.7e-05 |
| cVA + food | 2 / +3.8e-05 | 2 / +1.8e-03 | 2 / +7.8e-04 | 3 / +3.8e-04 | 2 / +5.4e-05 | 3 / +3.8e-04 | 2 / +5.5e-05 | 3 / +1.2e-05 |
| cVA + touch | 2 / +6.4e-05 | 2 / +1.7e-03 | 2 / +1.1e-03 | 2 / +1.7e-03 | 2 / +1.1e-03 | 2 / +3.3e-04 | 2 / +3.4e-03 | 2 / +8.9e-03 |
| cVA + song | 2 / +1.4e-05 | 2 / +1.6e-03 | 2 / +7.9e-04 | 2 / +4.0e-04 | 1 / +9.7e-04 | 3 / +1.5e-04 | 2 / +3.0e-04 | 2 / +1.7e-05 |
| Or47b + song | 3 / +2.6e-06 | 2 / +4.4e-05 | 2 / +9.1e-05 | 2 / +5.2e-05 | 1 / +9.2e-04 | 3 / +1.7e-05 | 2 / +2.6e-04 | 2 / +5.3e-06 |
| Or47b + touch | 3 / +5.3e-05 | 2 / +9.3e-05 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +2.0e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| food + touch | 2 / +7.6e-05 | 2 / +2.1e-04 | 2 / +4.2e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +4.1e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| CO2 + touch | 2 / +5.4e-05 | 2 / +1.4e-04 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +5.4e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| pheromones + song + touch | 2 / +7.1e-05 | 2 / +2.1e-03 | 2 / +1.2e-03 | 2 / +1.7e-03 | 1 / +2.0e-03 | 2 / +4.0e-04 | 2 / +3.7e-03 | 2 / +8.9e-03 |
| cVA + sugar | 2 / +3.6e-05 | 2 / +1.6e-03 | 2 / +7.4e-04 | 2 / +3.8e-04 | 2 / +7.9e-05 | 2 / +8.5e-04 | 2 / +6.9e-05 | 2 / +1.7e-03 |

- reference touch (all head bristles) -> DNp13 reject: hops 2, 436,741 paths, w_max +1.5e-03 (k3), w_exc_3 +3.3e-03; top route `touch (all head bristles) > AN_AVLP_GNG_18 > AVLP340 > DNp13 reject` (+1.2e-03)
- reference sugar GRNs -> MN9: hops 2, 106,050 paths, w_max +1.7e-03 (k3), w_exc_3 +1.7e-03; top route `sugar GRNs > CB0118 > CB0862 > MN9` (+3.9e-04)
- largest decider |w_max| (single sensory groups): touch (all head bristles) -> vpoEN/DN accept, -4.1e-03 (k3) = 2.78x the weaker reference's.
- largest decider positive w_max (single sensory groups): all pheromone ORNs -> pC1b/c, +1.9e-03 (k3) = 1.28x the weaker reference's.
- largest decider w_exc_3 (single sensory groups): all pheromone ORNs -> pC1b/c, +2.0e-03 = 1.14x the weaker reference's.
- 57 of 102 single-group sensory-decider pairs have a negative w_max (net inhibitory).

Strongest single sensory group per decider under `shiu_min1+eln0.25` (top route; share of that w_k):

- pC1a recept: bitter GRNs, w_max -2.4e-04 (k4), hops 2; `bitter GRNs > CB0638 > AN_FLA_SMP_2 > pC1a recept` +2.1e-04 (k3, 178% of w_3)
- pC1b/c: all pheromone ORNs, w_max +1.9e-03 (k3), hops 2; `all pheromone ORNs > DA1_lPN > CB0997 > pC1b/c` +1.0e-03 (k3, 54% of w_3)
- pC1d/e aggr: all pheromone ORNs, w_max +1.7e-03 (k2), hops 2; `all pheromone ORNs > M_lvPNm45 > pC1d/e aggr` +1.7e-03 (k2, 99% of w_2)
- aIPg aggr: touch (all head bristles), w_max +1.5e-03 (k3), hops 2; `touch (all head bristles) > CB0619 > AOTU064 > aIPg aggr` +5.8e-04 (k3, 40% of w_3)
- vpoEN/DN accept: touch (all head bristles), w_max -4.1e-03 (k3), hops 2; `touch (all head bristles) > CB0443 > CB1484 > vpoEN/DN accept` -8.4e-04 (k3, 21% of w_3)
- oviDN egg: bitter GRNs, w_max -4.8e-04 (k3), hops 2; `bitter GRNs > CB0159 > SA_VTV_5 > mAL_f2 > oviDN egg` +6.7e-04 (k4, 156% of w_4)

### `shiu_min1`: strongest signed propagated weight w_max (and its k)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | -4.8e-05 k3 | +1.2e-03 k3 | +1.7e-03 k2 | +2.8e-04 k3 | +7.9e-05 k4 | +1.3e-04 k3 | +1.1e-04 k3 | +2.4e-05 k4 |
| cVA-long (Or65a/DL3) | -6.8e-06 k4 | +7.7e-05 k3 | +7.5e-06 k4 | -6.9e-06 k4 | -4.3e-06 k4 | +3.0e-05 k3 | +7.0e-06 k3 | -1.2e-06 k4 |
| Or47b (VA1v) | +4.0e-06 k4 | +8.4e-06 k3 | +6.8e-06 k3 | -1.1e-04 k3 | +1.6e-05 k4 | -1.4e-05 k4 | -1.7e-05 k4 | -7.3e-07 k4 |
| Or88a (VA1d) | +1.7e-06 k4 | -5.8e-06 k4 | +8.7e-06 k4 | -1.1e-04 k3 | +1.2e-05 k4 | -2.4e-05 k4 | -1.2e-05 k4 | -4.0e-06 k4 |
| Or83c (DC3) | -5.8e-06 k4 | +1.5e-04 k3 | -1.3e-05 k3 | -5.7e-06 k3 | -5.4e-06 k4 | -4.8e-05 k4 | +1.2e-05 k4 | +2.1e-07 k3 |
| all pheromone ORNs | -4.7e-05 k3 | +1.4e-03 k3 | +1.7e-03 k2 | -1.3e-04 k2 | +9.8e-05 k4 | +1.3e-04 k3 | +1.1e-04 k3 | +1.9e-05 k4 |
| food odor | -7.1e-05 k4 | +7.7e-05 k2 | +3.6e-05 k3 | -2.7e-05 k4 | +1.6e-06 k4 | -1.6e-04 k4 | +6.2e-06 k3 | +8.7e-07 k4 |
| CO2 (V) | -1.1e-04 k4 | +3.5e-05 k3 | -2.2e-05 k4 | +1.8e-05 k3 | -2.6e-06 k4 | +1.8e-04 k3 | -4.5e-06 k3 | -1.3e-06 k4 |
| aversive odor (DA2/DL4) | -4.6e-05 k4 | -2.0e-05 k4 | -1.9e-05 k3 | -7.4e-06 k4 | -4.2e-06 k4 | -8.7e-05 k4 | +2.8e-06 k4 | +2.6e-08 k4 |
| song/sound (JO-A) | +1.8e-06 k3 | +7.1e-06 k3 | +7.4e-06 k2 | +3.1e-05 k3 | -6.7e-04 k2 | +2.5e-06 k4 | +6.1e-05 k2 | +3.8e-05 k3 |
| sound (JO-B) | -2.3e-06 k4 | +3.0e-05 k4 | -2.0e-05 k4 | -3.6e-05 k2 | -8.1e-04 k3 | +1.6e-06 k3 | -7.7e-05 k4 | +1.4e-05 k4 |
| wind/gravity (JO-CE) | +3.4e-06 k3 | +1.3e-05 k4 | -1.1e-04 k4 | -4.0e-05 k2 | -1.5e-03 k3 | +7.9e-06 k4 | -1.7e-04 k4 | -3.4e-05 k3 |
| touch (all head bristles) | -1.1e-04 k2 | -5.0e-05 k3 | +2.2e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +7.5e-05 k4 | +1.5e-03 k3 | -8.8e-03 k2 |
| touch (antennal bristles) | +3.3e-05 k3 | -3.0e-06 k3 | -1.2e-05 k4 | +1.1e-04 k3 | -3.7e-04 k3 | +7.5e-06 k4 | +9.1e-05 k3 | +8.7e-05 k3 |
| touch (eye bristles) | -1.8e-05 k4 | -8.0e-06 k4 | -4.1e-05 k4 | +4.6e-04 k3 | -1.9e-03 k3 | +2.0e-05 k4 | +5.7e-04 k3 | +1.4e-03 k3 |
| sugar GRNs | -5.9e-05 k4 | -1.6e-05 k4 | +7.8e-06 k4 | -2.9e-05 k3 | +3.5e-05 k2 | +2.4e-04 k3 | -5.7e-05 k4 | +1.7e-03 k3 |
| bitter GRNs | -2.4e-04 k4 | -4.1e-05 k2 | -2.1e-05 k4 | +3.3e-05 k3 | +1.3e-05 k2 | -4.8e-04 k3 | -1.7e-05 k3 | -2.1e-04 k3 |
| cVA + food | -1.1e-04 k4 | +1.2e-03 k3 | +1.7e-03 k2 | +2.6e-04 k3 | +8.1e-05 k4 | +2.5e-04 k3 | +1.1e-04 k3 | +2.5e-05 k4 |
| cVA + touch | -1.1e-04 k2 | +1.1e-03 k3 | +1.7e-03 k2 | +1.7e-03 k3 | -4.1e-03 k3 | +1.9e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + song | -4.6e-05 k3 | +1.2e-03 k3 | +1.7e-03 k2 | +3.1e-04 k3 | -6.7e-04 k2 | +1.4e-04 k3 | +9.3e-05 k3 | +4.6e-05 k3 |
| Or47b + song | +3.8e-06 k4 | +1.5e-05 k3 | +1.4e-05 k3 | -7.6e-05 k3 | -6.7e-04 k2 | -1.1e-05 k4 | -6.8e-05 k4 | +3.9e-05 k3 |
| Or47b + touch | -1.1e-04 k2 | -4.2e-05 k3 | +2.3e-04 k3 | +1.3e-03 k3 | -4.1e-03 k3 | +6.2e-05 k4 | +1.5e-03 k3 | -8.8e-03 k2 |
| food + touch | -1.4e-04 k2 | -8.0e-05 k4 | +2.6e-04 k3 | +1.4e-03 k3 | -4.1e-03 k3 | +1.7e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| CO2 + touch | -1.1e-04 k2 | -1.5e-05 k3 | +2.3e-04 k3 | +1.5e-03 k3 | -4.1e-03 k3 | +2.4e-04 k3 | +1.5e-03 k3 | -8.8e-03 k2 |
| pheromones + song + touch | -1.1e-04 k2 | +1.4e-03 k3 | +1.7e-03 k2 | +1.5e-03 k3 | -4.2e-03 k3 | +1.9e-04 k3 | +1.6e-03 k3 | -8.8e-03 k2 |
| cVA + sugar | -9.7e-05 k4 | +1.2e-03 k3 | +1.7e-03 k2 | +2.5e-04 k3 | +8.1e-05 k4 | +3.7e-04 k3 | +8.6e-05 k3 | +1.8e-03 k4 |

### `shiu_min1`: excitatory-only hops / w_exc_3 (upper bound of what can excite)

| source | pC1a | pC1b/c | pC1d/e | aIPg | vpoEN/DN | oviDN | DNp13 (ref) | MN9 (ref) |
|---|---|---|---|---|---|---|---|---|
| cVA (Or67d/DA1) | 2 / +1.2e-05 | 2 / +1.2e-03 | 2 / +5.1e-04 | 3 / +3.0e-04 | 3 / +4.2e-05 | 3 / +1.2e-04 | 3 / +3.8e-05 | 3 / +1.1e-05 |
| cVA-long (Or65a/DL3) | 3 / +1.7e-06 | 3 / +8.0e-05 | 3 / +1.3e-05 | 3 / +1.3e-07 | 3 / +3.5e-06 | 3 / +3.0e-05 | 3 / +7.6e-06 | 3 / +1.0e-09 |
| Or47b (VA1v) | 3 / +1.3e-06 | 3 / +1.6e-05 | 3 / +1.5e-05 | 3 / +3.4e-06 | 3 / +5.0e-08 | 3 / +1.1e-05 | 3 / +6.1e-07 | 3 / +5.1e-07 |
| Or88a (VA1d) | 2 / +4.1e-07 | 3 / +6.6e-06 | 2 / +3.5e-06 | 3 / +9.9e-07 | 3 / +4.3e-07 | 3 / +1.9e-06 | 3 / +2.7e-07 | 4 / 0 |
| Or83c (DC3) | 3 / +1.2e-06 | 2 / +1.6e-04 | 2 / +1.7e-05 | 3 / +3.5e-06 | 3 / +1.2e-06 | 3 / +9.1e-06 | 3 / +9.9e-06 | 3 / +2.8e-07 |
| all pheromone ORNs | 2 / +1.7e-05 | 2 / +1.5e-03 | 2 / +5.6e-04 | 3 / +3.1e-04 | 3 / +4.7e-05 | 3 / +1.7e-04 | 3 / +5.6e-05 | 3 / +1.2e-05 |
| food odor | 2 / +2.1e-05 | 2 / +1.2e-04 | 2 / +6.6e-05 | 3 / +2.0e-05 | 2 / +6.4e-06 | 3 / +1.8e-04 | 2 / +7.5e-06 | 3 / +4.4e-08 |
| CO2 (V) | 2 / +2.4e-06 | 3 / +5.5e-05 | 2 / +1.6e-05 | 3 / +2.2e-05 | 3 / +1.2e-06 | 3 / +2.9e-04 | 3 / +4.1e-06 | 3 / +9.1e-09 |
| aversive odor (DA2/DL4) | 3 / +7.0e-07 | 3 / +9.6e-06 | 3 / +7.8e-06 | 3 / +1.8e-06 | 2 / +1.9e-07 | 3 / +3.6e-05 | 3 / +4.8e-07 | 4 / 0 |
| song/sound (JO-A) | 3 / +7.8e-07 | 2 / +2.2e-05 | 2 / +7.1e-05 | 2 / +4.8e-05 | 1 / +9.2e-04 | 3 / +2.6e-06 | 2 / +2.6e-04 | 2 / +4.8e-06 |
| sound (JO-B) | 3 / +7.7e-08 | 2 / +1.9e-06 | 2 / +2.8e-05 | 2 / +4.5e-05 | 2 / +1.5e-03 | 3 / +1.1e-06 | 2 / +1.0e-04 | 3 / +3.4e-06 |
| wind/gravity (JO-CE) | 3 / +8.8e-07 | 2 / +1.3e-05 | 2 / +1.0e-04 | 2 / +8.7e-05 | 2 / +1.6e-03 | 3 / +6.0e-06 | 2 / +1.8e-04 | 2 / +2.4e-05 |
| touch (all head bristles) | 3 / +5.1e-05 | 2 / +7.1e-05 | 2 / +3.5e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +1.8e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| touch (antennal bristles) | 3 / +5.6e-06 | 3 / +9.3e-06 | 3 / +3.4e-05 | 2 / +1.2e-04 | 2 / +1.2e-04 | 2 / +9.8e-06 | 2 / +2.3e-04 | 2 / +2.4e-04 |
| touch (eye bristles) | 3 / +2.3e-05 | 3 / +3.1e-05 | 3 / +1.5e-04 | 2 / +5.6e-04 | 2 / +4.3e-04 | 2 / +4.3e-05 | 2 / +1.4e-03 | 2 / +1.4e-03 |
| sugar GRNs | 2 / +2.3e-05 | 2 / +3.4e-05 | 2 / +2.4e-05 | 2 / +2.0e-05 | 2 / +3.2e-05 | 2 / +7.0e-04 | 2 / +2.2e-05 | 2 / +1.7e-03 |
| bitter GRNs | 2 / +2.6e-04 | 2 / +1.2e-04 | 2 / +5.9e-05 | 3 / +2.0e-05 | 2 / +1.3e-05 | 2 / +6.4e-04 | 3 / +6.2e-06 | 2 / +6.7e-05 |
| cVA + food | 2 / +3.3e-05 | 2 / +1.3e-03 | 2 / +5.7e-04 | 3 / +3.2e-04 | 2 / +4.8e-05 | 3 / +3.0e-04 | 2 / +4.5e-05 | 3 / +1.1e-05 |
| cVA + touch | 2 / +6.3e-05 | 2 / +1.3e-03 | 2 / +8.6e-04 | 2 / +1.6e-03 | 2 / +1.1e-03 | 2 / +3.0e-04 | 2 / +3.4e-03 | 2 / +8.9e-03 |
| cVA + song | 2 / +1.3e-05 | 2 / +1.2e-03 | 2 / +5.8e-04 | 2 / +3.5e-04 | 1 / +9.7e-04 | 3 / +1.2e-04 | 2 / +3.0e-04 | 2 / +1.6e-05 |
| Or47b + song | 3 / +2.1e-06 | 2 / +3.8e-05 | 2 / +8.6e-05 | 2 / +5.1e-05 | 1 / +9.2e-04 | 3 / +1.4e-05 | 2 / +2.6e-04 | 2 / +5.3e-06 |
| Or47b + touch | 3 / +5.2e-05 | 2 / +8.7e-05 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +1.9e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| food + touch | 2 / +7.2e-05 | 2 / +1.9e-04 | 2 / +4.2e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +3.6e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| CO2 + touch | 2 / +5.3e-05 | 2 / +1.3e-04 | 2 / +3.7e-04 | 2 / +1.3e-03 | 2 / +1.1e-03 | 2 / +4.7e-04 | 2 / +3.3e-03 | 2 / +8.9e-03 |
| pheromones + song + touch | 2 / +6.9e-05 | 2 / +1.6e-03 | 2 / +9.8e-04 | 2 / +1.7e-03 | 1 / +2.0e-03 | 2 / +3.6e-04 | 2 / +3.6e-03 | 2 / +8.9e-03 |
| cVA + sugar | 2 / +3.5e-05 | 2 / +1.2e-03 | 2 / +5.3e-04 | 2 / +3.2e-04 | 2 / +7.4e-05 | 2 / +8.2e-04 | 2 / +6.0e-05 | 2 / +1.7e-03 |

- reference touch (all head bristles) -> DNp13 reject: hops 2, 436,741 paths, w_max +1.5e-03 (k3), w_exc_3 +3.3e-03; top route `touch (all head bristles) > AN_AVLP_GNG_18 > AVLP340 > DNp13 reject` (+1.2e-03)
- reference sugar GRNs -> MN9: hops 2, 106,050 paths, w_max +1.7e-03 (k3), w_exc_3 +1.7e-03; top route `sugar GRNs > CB0118 > CB0862 > MN9` (+3.9e-04)
- largest decider |w_max| (single sensory groups): touch (all head bristles) -> vpoEN/DN accept, -4.1e-03 (k3) = 2.78x the weaker reference's.
- largest decider positive w_max (single sensory groups): all pheromone ORNs -> pC1d/e aggr, +1.7e-03 (k2) = 1.12x the weaker reference's.
- largest decider w_exc_3 (single sensory groups): wind/gravity (JO-CE) -> vpoEN/DN accept, +1.6e-03 = 0.93x the weaker reference's.
- 53 of 102 single-group sensory-decider pairs have a negative w_max (net inhibitory).

Strongest single sensory group per decider under `shiu_min1` (top route; share of that w_k):

- pC1a recept: bitter GRNs, w_max -2.4e-04 (k4), hops 2; `bitter GRNs > CB0638 > AN_FLA_SMP_2 > pC1a recept` +2.1e-04 (k3, 177% of w_3)
- pC1b/c: all pheromone ORNs, w_max +1.4e-03 (k3), hops 2; `all pheromone ORNs > DA1_lPN > CB0997 > pC1b/c` +7.6e-04 (k3, 54% of w_3)
- pC1d/e aggr: all pheromone ORNs, w_max +1.7e-03 (k2), hops 2; `all pheromone ORNs > M_lvPNm45 > pC1d/e aggr` +1.6e-03 (k2, 99% of w_2)
- aIPg aggr: touch (all head bristles), w_max +1.5e-03 (k3), hops 2; `touch (all head bristles) > CB0619 > AOTU064 > aIPg aggr` +5.8e-04 (k3, 40% of w_3)
- vpoEN/DN accept: touch (all head bristles), w_max -4.1e-03 (k3), hops 2; `touch (all head bristles) > CB0443 > CB1484 > vpoEN/DN accept` -8.4e-04 (k3, 21% of w_3)
- oviDN egg: bitter GRNs, w_max -4.8e-04 (k3), hops 2; `bitter GRNs > CB0159 > SA_VTV_5 > mAL_f2 > oviDN egg` +6.7e-04 (k4, 155% of w_4)

## (b) Hunger / fullness neurons against SAG and pC1 (synapse counts from the raw table)

### `shiu_min1+known+eln0.25`: cells = hops / paths <= 3 / w_max

| source | role | n | out syn | per neuron | partners | exc | MN9 | feed MNs | PAM | PPL1 |
|---|---|---|---|---|---|---|---|---|---|---|
| fed (IPC tonic) | hunger/fullness | 18 | 157 | 9 | 105 | 1.00 | 3 / 64 / -2.6e-07 | 2 / 9,234 / -1.6e-06 | 2 / 22,434 / +4.3e-07 | 2 / 6,545 / -1.1e-06 |
| fed (DH44 tonic) | hunger/fullness | 6 | 69 | 12 | 61 | 1.00 | 2 / 178 / -2.8e-06 | 2 / 14,289 / +7.4e-06 | 2 / 5,631 / -1.0e-06 | 2 / 2,075 / -1.1e-06 |
| hungry (NPF tonic) | hunger/fullness | 4 | 2,487 | 622 | 1210 | 1.00 | 2 / 2,048 / -1.4e-05 | 2 / 67,209 / -7.8e-06 | 1 / 696,941 / +5.2e-05 | 1 / 212,779 / +3.2e-05 |
| SIFa tonic | hunger/fullness | 4 | 1,873 | 468 | 1323 | 0.00 | 2 / 588 / +2.6e-06 | 2 / 30,298 / -2.9e-06 | 2 / 328,764 / -3.2e-05 | 2 / 88,568 / -3.1e-05 |
| AstA tonic | hunger/fullness | 2 | 23,871 | 11,936 | 3296 | 0.00 | 2 / 2,282 / +2.4e-05 | 2 / 85,457 / +1.6e-05 | 1 / 1,591,253 / -1.2e-04 | 1 / 555,051 / -4.1e-04 |
| virgin (SAG tonic) | comparison | 2 | 1,367 | 684 | 240 | 1.00 | 3 / 106 / +4.3e-07 | 2 / 7,692 / -1.1e-06 | 2 / 139,223 / -6.0e-06 | 2 / 42,518 / -8.3e-06 |
| aroused female (pC1a-c tonic) | comparison | 6 | 9,024 | 1,504 | 1169 | 1.00 | 2 / 1,674 / -7.7e-06 | 2 / 68,426 / -1.1e-05 | 1 / 1,262,732 / +9.6e-05 | 1 / 406,576 / -8.7e-05 |
| sugar GRNs | reference | 129 | 25,221 | 196 | 720 | 0.95 | 2 / 106,050 / +1.7e-03 | 1 / 5,278,981 / +9.5e-04 | 2 / 626,802 / +7.7e-05 | 2 / 141,663 / +4.2e-05 |

### `shiu_min1+eln0.25`: cells = hops / paths <= 3 / w_max

| source | role | n | out syn | per neuron | partners | exc | MN9 | feed MNs | PAM | PPL1 |
|---|---|---|---|---|---|---|---|---|---|---|
| fed (IPC tonic) | hunger/fullness | 18 | 157 | 9 | 105 | 1.00 | 3 / 64 / -2.4e-07 | 2 / 9,234 / -1.3e-06 | 2 / 22,434 / +4.4e-07 | 2 / 6,545 / -1.1e-06 |
| fed (DH44 tonic) | hunger/fullness | 6 | 69 | 12 | 61 | 1.00 | 2 / 178 / -2.8e-06 | 2 / 14,289 / +7.4e-06 | 2 / 5,631 / -1.0e-06 | 2 / 2,075 / -1.1e-06 |
| hungry (NPF tonic) | hunger/fullness | 4 | 2,487 | 622 | 1210 | 1.00 | 2 / 2,048 / -1.4e-05 | 2 / 67,209 / -7.8e-06 | 1 / 696,941 / +5.2e-05 | 1 / 212,779 / +3.2e-05 |
| SIFa tonic | hunger/fullness | 4 | 1,873 | 468 | 1323 | 1.00 | 2 / 588 / -2.8e-06 | 2 / 30,298 / +2.9e-06 | 2 / 328,764 / +3.3e-05 | 2 / 88,568 / +3.1e-05 |
| AstA tonic | hunger/fullness | 2 | 23,871 | 11,936 | 3296 | 0.00 | 2 / 2,282 / +2.4e-05 | 2 / 85,457 / +1.8e-05 | 1 / 1,591,253 / -1.2e-04 | 1 / 555,051 / -4.1e-04 |
| virgin (SAG tonic) | comparison | 2 | 1,367 | 684 | 240 | 1.00 | 3 / 106 / +5.0e-07 | 2 / 7,692 / -1.1e-06 | 2 / 139,223 / -6.1e-06 | 2 / 42,518 / -8.3e-06 |
| aroused female (pC1a-c tonic) | comparison | 6 | 9,024 | 1,504 | 1169 | 1.00 | 2 / 1,674 / -7.7e-06 | 2 / 68,426 / -1.1e-05 | 1 / 1,262,732 / +9.6e-05 | 1 / 406,576 / -8.7e-05 |
| sugar GRNs | reference | 129 | 25,221 | 196 | 720 | 0.95 | 2 / 106,050 / +1.7e-03 | 1 / 5,278,981 / +9.5e-04 | 2 / 626,802 / +8.4e-05 | 2 / 141,663 / +4.3e-05 |

### `shiu_min1`: cells = hops / paths <= 3 / w_max

| source | role | n | out syn | per neuron | partners | exc | MN9 | feed MNs | PAM | PPL1 |
|---|---|---|---|---|---|---|---|---|---|---|
| fed (IPC tonic) | hunger/fullness | 18 | 157 | 9 | 105 | 1.00 | 3 / 64 / -2.4e-07 | 2 / 9,234 / -1.3e-06 | 2 / 22,434 / +4.4e-07 | 2 / 6,545 / -1.1e-06 |
| fed (DH44 tonic) | hunger/fullness | 6 | 69 | 12 | 61 | 1.00 | 2 / 178 / -2.8e-06 | 2 / 14,289 / +7.4e-06 | 2 / 5,631 / -1.0e-06 | 2 / 2,075 / -1.1e-06 |
| hungry (NPF tonic) | hunger/fullness | 4 | 2,487 | 622 | 1210 | 1.00 | 2 / 2,048 / -1.4e-05 | 2 / 67,209 / -7.8e-06 | 1 / 696,941 / +5.2e-05 | 1 / 212,779 / +3.2e-05 |
| SIFa tonic | hunger/fullness | 4 | 1,873 | 468 | 1323 | 1.00 | 2 / 588 / -2.8e-06 | 2 / 30,298 / +2.9e-06 | 2 / 328,764 / +2.9e-05 | 2 / 88,568 / +3.1e-05 |
| AstA tonic | hunger/fullness | 2 | 23,871 | 11,936 | 3296 | 0.00 | 2 / 2,282 / +2.4e-05 | 2 / 85,457 / +1.8e-05 | 1 / 1,591,253 / -1.2e-04 | 1 / 555,051 / -4.1e-04 |
| virgin (SAG tonic) | comparison | 2 | 1,367 | 684 | 240 | 1.00 | 3 / 106 / +5.0e-07 | 2 / 7,692 / -1.1e-06 | 2 / 139,223 / -6.2e-06 | 2 / 42,518 / -8.3e-06 |
| aroused female (pC1a-c tonic) | comparison | 6 | 9,024 | 1,504 | 1169 | 1.00 | 2 / 1,674 / -7.7e-06 | 2 / 68,426 / -1.1e-05 | 1 / 1,262,732 / +9.6e-05 | 1 / 406,576 / -8.7e-05 |
| sugar GRNs | reference | 129 | 25,221 | 196 | 720 | 0.95 | 2 / 106,050 / +1.7e-03 | 1 / 5,278,981 / +9.5e-04 | 2 / 626,802 / +8.5e-05 | 2 / 141,663 / +4.1e-05 |

Top postsynaptic types (synapses):

- fed (IPC tonic): IPC (25), CB0991 (15), CB4203 (8), SMP746 (7), CB0026 (6)
- fed (DH44 tonic): DH44 (6), CB2506 (4), CB1814 (3), CB2231 (2), CB2468 (2)
- hungry (NPF tonic): AVLP076 (80), PVLP010 (57), AVLP201 (41), PVLP021 (40), CB1085 (33)
- SIFa tonic: LT33 (149), Dm10 (73), TmY3 (54), KCab (51), lLN2P_a (49)
- AstA tonic: CL269 (405), CL071b (339), CL359 (336), CL069 (273), CL065 (269)
- virgin (SAG tonic): pC1a (387), pC1b (312), pC1c (166), CB0094 (90), CB0405 (48)
- aroused female (pC1a-c tonic): SMP553 (564), DNp37 (498), SMP333 (363), pC1c (308), SMP555,SMP556 (287)
- sugar GRNs: LB3 (3209), CB0248 (1621), CB0192 (1311), AN_GNG_30 (1238), CB0008 (1180)

Neuroendocrine cells (IPC, DH44, ...) act mostly by hormone release, which W does not contain; the rows above are their synaptic outputs only.

## (c) Neurons whose sign signs=known flips

- 11,010 of 81,245 neurons with a known transmitter; {'exc->inh': 9572, 'inh->exc': 1438} ; 1.6% of all output synapses.
- photoreceptors (super_class sensory, cell_class visual): 8,359 (75.9% of the flips; of 11,391 photoreceptors); types {'R1-6': 6532, 'R8': 1002, 'R7': 825}; sub-classes {'(none)': 8219, 'DRA': 140}. Of all photoreceptors 8,620 are predicted excitatory and 837 have no output synapse (sign 0, never flipped); 5 histaminergic flips are not photoreceptors. (connectome.py docstring: 9,200 photoreceptors.)
- known transmitter of the flipped neurons: {'histamine': 8364, 'acetylcholine': 1399, 'glutamate': 912, 'gaba': 296, 'serotonin': 16, 'octopamine': 14, 'dopamine': 9}.
- antennal-lobe local neurons flipped: 16; central complex (cell_class CX): 94.

By super_class:

| super_class | n | out_syn |
|---|---|---|
| sensory | 8360 | 225,202 |
| optic | 2440 | 357,994 |
| central | 155 | 185,398 |
| descending | 24 | 15,958 |
| visual_projection | 18 | 10,539 |
| visual_centrifugal | 9 | 49,157 |
| ascending | 4 | 1,050 |

Top 15 cell_class (all super_classes):

| super_class | cell_class | direction | n | out_syn |
|---|---|---|---|---|
| sensory | visual | exc->inh | 8359 | 225,046 |
| optic | ME | exc->inh | 818 | 81,555 |
| optic | LA>ME | inh->exc | 548 | 123,480 |
| optic | ME>LOP | inh->exc | 325 | 27,351 |
| optic | LO>LOP | inh->exc | 289 | 26,692 |
| optic | ME>LA | exc->inh | 230 | 17,657 |
| optic | ME | inh->exc | 136 | 63,473 |
| central | CX | exc->inh | 58 | 46,308 |
| central | CX | inh->exc | 36 | 24,691 |
| central |  | inh->exc | 31 | 47,376 |
| optic | LA>ME | exc->inh | 24 | 5,251 |
| optic | ME>LA | inh->exc | 22 | 3,212 |
| central | ALLN | exc->inh | 16 | 56,207 |
| optic | ME>LO | exc->inh | 15 | 1,794 |
| optic | ME>LO | inh->exc | 15 | 4,360 |

## (d) Antennal-lobe local neurons (cell_class ALLN) by predicted transmitter and sign

429 ALLN. eLN (positive row sign, what an eLN scale multiplies): 166 under the Shiu signs, by top_nt {'acetylcholine': 72, 'serotonin': 40, 'gaba': 29, 'dopamine': 12, 'glutamate': 11, 'octopamine': 2}; 150 under the known signs, by top_nt {'acetylcholine': 71, 'serotonin': 38, 'gaba': 16, 'dopamine': 12, 'glutamate': 11, 'octopamine': 2}.

| top_nt | sign_shiu | sign_known | n | out_syn | out_syn_to_alpn |
|---|---|---|---|---|---|
| acetylcholine | + | + | 71 | 123,171 | 37,842 |
| acetylcholine | + | - | 1 | 11,450 | 2,299 |
| acetylcholine | - | - | 8 | 4,384 | 2,196 |
| dopamine | + | + | 12 | 46,905 | 17,143 |
| gaba | + | + | 16 | 60,149 | 14,975 |
| gaba | + | - | 13 | 40,247 | 12,387 |
| gaba | - | - | 118 | 186,870 | 62,303 |
| glutamate | + | + | 11 | 19,701 | 9,455 |
| glutamate | - | - | 137 | 72,747 | 34,365 |
| octopamine | + | + | 2 | 1,424 | 350 |
| serotonin | + | + | 38 | 187,344 | 62,872 |
| serotonin | + | - | 2 | 4,510 | 3,657 |

Files: `structure_paths_flywire.csv`, `structure_routes_flywire.csv`, `structure_state_flywire.csv`, `structure_aln_flywire.csv`, `structure_signflips_flywire.csv`
