# Exact Mac–Linux input specification diagnosis

Target: `search_cma-g00-c000-DoorKey-8x8-2000000-seed1000`.

**The candidate vector itself differs numerically.** Its zero-based coordinates **4, 7, 10 and 11** differ by exactly one float64 ULP each. Decoded relief parameters 0 and 3 and growth parameter 3 differ as well, including their copies in the training configuration. These are scientific input fields. A paths/version/platform-only fix is therefore inapplicable.

## Full specifications and provenance

- [Mac full input](mac-specification.json), [Mac execution metadata](mac-dump-metadata.json).
- [Linux full input](linux-specification.json), [Linux execution metadata](linux-dump-metadata.json).
- [Complete unified diff](specification.diff).
- [Every changed field, exact values, float hex and ULPs](field-differences.csv).
- [Machine-readable comparison, including every unchanged field](field-differences.json).

The Mac specification reproduces the original recorded canonical SHA256 `6984a4a2f4eedf4408a645b4986ea825c4a60e6153769374f0cd58b26ef3fa3a`. The diagnostic Linux specification reproduces the failed replay's canonical SHA256 `f65304c4d5315a0ac775bb302457e86220ccf47f2b00b6f719a726f41212b639` **exactly**. This is a faithful regeneration of both compared inputs, not a comparison against a different Linux output. The failed check had saved only hashes; the full Linux input was generated in this new explicitly authorized read-only diagnostic.

These are hashes of compact, key-sorted JSON, matching the registered hash function. Pretty-printed file-byte hashes are different because whitespace differs. Metadata is stored separately and is not part of the input hash.

The isolated diagnostic run is `fc91e753-e0e1-467a-af65-44566804fb09`, source `de75a8e49c6b06ca9e57c63dcfed48545f5079f5`, Linux Intel family 6, model 85, with the same pinned NumPy/CMA/SciPy versions as the Mac. It only constructs the specified first input and prints it. No trainer, controller, historical ask/tell replay or worker/volume mutation is invoked. The reported Mac dump was regenerated after that diagnostic protocol was committed; an earlier local sanity dump gave the same hash.

## All differing fields

| Field | Mac | Linux | Linux − Mac | ULPs |
|---|---:|---:|---:|---:|
| `$.config.intrinsic.growth[3]` | `0.0022552192936547604` | `0.002255219293654762` | `1.734723475976807094411924481391906738281250E-18` | 4 |
| `$.config.intrinsic.relief[0]` | `0.34923006114806593` | `0.349230061148066` | `5.5511151231257827021181583404541015625E-17` | 1 |
| `$.config.intrinsic.relief[3]` | `0.31642174648727045` | `0.3164217464872704` | `-5.5511151231257827021181583404541015625E-17` | 1 |
| `$.genome.growth[3]` | `0.0022552192936547604` | `0.002255219293654762` | `1.734723475976807094411924481391906738281250E-18` | 4 |
| `$.genome.relief[0]` | `0.34923006114806593` | `0.349230061148066` | `5.5511151231257827021181583404541015625E-17` | 1 |
| `$.genome.relief[3]` | `0.31642174648727045` | `0.3164217464872704` | `-5.5511151231257827021181583404541015625E-17` | 1 |
| `$.latent[4]` | `0.34923006114806593` | `0.349230061148066` | `5.5511151231257827021181583404541015625E-17` | 1 |
| `$.latent[7]` | `0.31642174648727045` | `0.3164217464872704` | `-5.5511151231257827021181583404541015625E-17` | 1 |
| `$.latent[10]` | `0.4831377996847192` | `0.48313779968471915` | `-5.5511151231257827021181583404541015625E-17` | 1 |
| `$.latent[11]` | `0.5529411535717416` | `0.5529411535717417` | `1.1102230246251565404236316680908203125E-16` | 1 |


No object keys, array lengths or scalar types differ. **All other 64 leaf fields are identical**, including paths and non-scientific input metadata. The dump execution metadata necessarily describes different platforms, but those platform/version/CPU records are outside the specifications and are not responsible for this hash comparison.

Vector coordinates 4 and 7 map directly to relief for `new_view` and `toggle`, respectively. Coordinate 10 is the drop-growth latent value; both platform values are below 0.5, so both decode to growth 0. Coordinate 11 controls toggle growth, whose decoded values differ by 4 ULPs. The record does not identify the lower-level operation/library responsible for the differing initial samples; no untested numerical-cause claim is made.

## Scope and stop

The registered search runtime, scientific code, lock files, configurations and provider ledger are unchanged by this diagnosis. The Linux job used a separate child experiment with only a diagnostic launcher and script; its calculation-input hashes were recorded before launch. Its isolated launcher is not a change to the registered search launcher. Both full specifications and the field comparison are mirrored into the canonical Mac handoff folder.

Per the user's instruction: **stop and report**. No metadata fix, replay-check rerun or training restart has been performed or proposed as a workaround for this numerical mismatch. The user said they will resume on the Mac after this finding; no Mac restart is inferred from that statement.
