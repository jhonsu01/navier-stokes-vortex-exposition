# Licenses and credits

## This exposition

The essay, script, figures, animation and original sound are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The scripts in this package may be used under the same license.

## The mathematics and the formal proof

The construction described here is due to OpenAI: *Finite time blowup for Navier–Stokes* and the repository [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler) (Apache-2.0). This package cites that work and contains no copy of its source code. The verification logs contain output that names its modules and theorems.

The formal statement adapts [Formal Conjectures](https://github.com/google-deepmind/formal-conjectures) by Google DeepMind (Apache-2.0).

## Narration voice

English narration was generated with the [Phonon 31M English model](https://huggingface.co/gradium/phonon-31m-en) and the Preston voice from [gradium/phonon-voices](https://huggingface.co/gradium/phonon-voices). Their pages list the Apache-2.0 license. The [ptts](https://pypi.org/project/ptts/) runtime is MIT OR Apache-2.0.

## Sound

The background sound and effects were generated from scratch by `production/make_sfx.py` and `production/mix_final.py`. They use no external samples.

## Verification tools

Runs used [Lean 4](https://lean-lang.org/), [Mathlib](https://github.com/leanprover-community/mathlib4), [Comparator](https://github.com/leanprover/comparator), [lean4export](https://github.com/leanprover/lean4export), [landrun](https://github.com/Zouuup/landrun) and [nanoda_lib](https://github.com/ammkrn/nanoda_lib).

## AI assistance

The essay, script, code and verification runs were prepared with Claude (Anthropic), under the author's direction. The author is responsible for the submission.
