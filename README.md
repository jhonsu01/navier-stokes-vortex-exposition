# A Vortex, a Force and a Loophole

An exposition of OpenAI's claimed finite-time blowup for the forced three-dimensional Navier–Stokes equations, and of what its Lean proof does and does not certify.

**This is exposition only. It claims no new mathematical result.** All the mathematics of the construction is due to the cited authors. The essay and video were prepared with AI assistance (Claude, Anthropic).

- **Problem:** Navier–Stokes existence and smoothness, JSP-000005, [MathDB #315852](https://mathdb.com/p/315852/navier-stokes-existence-and-smoothness)
- **Category:** Exposition
- **Author:** @jhonsu777
- **Contact:** 2xrqx82e2@mozmail.com
- **Version:** v1.0, 4 November 2026 (UTC). Not independently reviewed.
- **Video:** <https://youtu.be/d3L9XvjKxvU>

## Contents

| Path | What it is |
| --- | --- |
| `essay/essay_en.pdf` | The essay |
| `essay/essay_en.md`, `essay/figures/` | Essay source and figures |
| `video/navier_stokes_en.mp4` | Narrated video, about 5:51, 1080p (attached to the release, not stored in git) |
| `video/navier_stokes_en.srt` | Subtitles (timing is approximate) |
| `video/video_script.md` | Narration script |
| `checks/scale_checks.py` | Symbolic scale checks used in the essay |
| `verification/` | Logs and scripts of our Lean runs |
| `production/` | Scripts that generate figures, animation, audio and sound effects |
| `NOTICE.md` | Licenses and credits |
| `SHA256SUMS.txt` | File checksums |

## What we checked

Every claim in the essay is tagged by origin. In summary, on commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd` of `openai/NavierStokesAndEuler`, with Lean v4.34.0-rc2 in Linux containers:

- `lake build NavierStokes.ComparatorSolution` completed all 9,371 jobs without errors.
- `#print axioms` reports only `propext`, `Classical.choice` and `Quot.sound` for both target theorems.
- `leanchecker --fresh` exited with code 0.
- On a new volume, as an unprivileged user, Comparator accepted the solution with both the Lean kernel and nanoda.

## What we did not check

- We did not verify the written 166-page proof. We read sections 1 to 3 and parts of section 10 closely.
- Whether the formal statement faithfully matches Clay's (C) and (D) is our reading, not an expert certification.
- Our Comparator run lacked the recommended `systemd-run` restriction on AF_UNIX sockets. It ran on a WSL2 6.6 kernel with Landlock ABI v3.
- None of this is an independent mathematical review. Alternatives (A) and (B) remain open.

## Reproducing

Scale checks, with Python and SymPy:

```bash
python checks/scale_checks.py
```

Comparator, in a container with no prior compilation of the solution, using an empty Docker volume mounted at `/vol`, this script mounted at `/comparator.sh` and a log folder at `/logs`:

```bash
docker run --rm --security-opt no-new-privileges -v VOLUME:/vol -v "$PWD/verification/comparator_container.sh:/comparator.sh:ro" -v "$PWD/logs:/logs" debian:bookworm-slim bash /comparator.sh
```

`verification/comparator_clean.sh` is an untested variant for a dedicated Linux machine, which adds the recommended `systemd-run` restriction. The scripts in `production/` contain absolute Windows paths from the original machine and need editing to run elsewhere.
