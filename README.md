# fleet-midi-bridge

Ternary vectors → MIDI pitch sequences. The same mapping implemented in Python and Go. Minimal, deterministic, no I/O.

## Problem

The SuperInstance fleet represents musical state as ternary vectors — sequences of `{1, 0, -1}`. To turn these into MIDI, you need a deterministic mapping from ternary space to pitch space. This repo provides that mapping, cross-verified in two languages.

## Insight

The mapping is trivially simple:
- `1` → go up 4 semitones (a major third)
- `-1` → go down 4 semitones
- `0` → stay (repeat the previous pitch)

Starting from a base note (MIDI 60 = middle C), this produces a sequence of pitches. The choice of 4 semitones is arbitrary but musically useful — it creates major-third intervals, which sound consonant and generate interesting melodic contours.

The resulting pitch sequences are *not* standard MIDI files — they're raw pitch arrays. Another tool in the fleet would need to wrap these in MIDI events with timing information.

## How It Works

```
Input:  ternary vector [1, 0, -1, 1, 0, -1, 1, 1]
        base pitch 60 (middle C)

Step 1: Start with [60]
Step 2: For each element:
  1  → 60 + 4 = 64  → [60, 64]
  0  → 64 + 0 = 64  → [60, 64, 64]
 -1  → 64 - 4 = 60  → [60, 64, 64, 60]
  1  → 60 + 4 = 64  → [60, 64, 64, 60, 64]
  0  → 64 + 0 = 64  → [60, 64, 64, 60, 64, 64]
 -1  → 64 - 4 = 60  → [60, 64, 64, 60, 64, 64, 60]
  1  → 60 + 4 = 64  → [60, 64, 64, 60, 64, 64, 60, 64]
  1  → 64 + 4 = 68  → [60, 64, 64, 60, 64, 64, 60, 64, 68]

Output: [60, 64, 64, 60, 64, 64, 60, 64, 68]
```

The `stats()` function computes:
- **density**: fraction of non-zero elements (how "active" the vector is)
- **balance**: (ups - downs) / total (net direction bias)

For `[1, 0, -1, 1, 0, -1, 1, 1]`: density = 0.75, balance = 0.25 (slightly upward-biased).

## Code

### Python (`lib/engine.py`)

```python
from lib.engine import process, stats

result = process([1, 0, -1, 1, 0, -1, 1, 1])
# {'notes': [60, 64, 64, 60, 64, 64, 60, 64, 68], 'vector': [...], 'length': 9}

s = stats([1, 0, -1, 1, 0, -1, 1, 1])
# {'density': 0.75, 'balance': 0.25}
```

### Go (`lib/go/`)

```go
// Identical algorithm, same output
v := []int{1, 0, -1, 1, 0, -1, 1, 1}
fmt.Println(process(v, 60))
// [60 64 64 60 64 64 60 64 68]
```

Both produce identical output for identical input. Verified manually.

## Module Map

```
lib/
  engine.py        — process() and stats() functions + CLI demo
  go/
    process.go     — identical algorithm in Go
    go.mod         — Go module file (fleet-midi-bridge, go 1.23.4)
```

## Design Decisions

### What was chosen

- **4-semitone step size.** Major third intervals. Produces consonant-sounding sequences. Could be parameterized but isn't.
- **Cumulative pitch.** Each new pitch is relative to the previous one, not to the base. This means the sequence can drift far from the starting pitch if the vector has sustained directional bias.
- **Pure computation, no I/O.** The Python function takes a vector and returns a dict. No files, no network, no MIDI file generation. It's a math function that happens to map to pitch space.

### Known limitations

1. **Not MIDI output.** This produces pitch arrays, not MIDI files. The pitch values need to be wrapped in note-on/note-off events with timing to become playable MIDI. That's a different repo's job.

2. **No octave wrapping.** If you feed in a long sequence of `1`s, the pitch climbs indefinitely. No clamp to a reasonable MIDI range (0-127). Real use would need bounds checking.

3. **Fixed step size.** Always 4 semitones. A more flexible version would accept a step parameter or even a mapping function.

4. **README claims 6 languages, only 2 exist.** The README mentions Python, JavaScript, Go, Rust, C, and C++. Only Python and Go implementations are present.

5. **Go code is a standalone `main`.** The Go implementation isn't importable as a library — it's a `main` package with a hardcoded demo vector. Not useful as a Go module dependency.

6. **No tests.** Neither language has any test coverage.

### What this is not

- Not a MIDI file generator. It produces pitch arrays.
- Not a bridge in the networking sense. It's a mathematical transform.
- Not a complete cross-language reference (despite README claims).

## Status

**Works correctly for what it does.** The Python and Go implementations produce identical output for the same input. The algorithm is simple enough that correctness is obvious on inspection.

**Not a bridge.** The name suggests MIDI I/O bridging, but it's a pure math function with no I/O. The "bridge" is conceptual — it bridges ternary vector space to pitch space.

**Not complete.** README claims 6-language cross-verification. Only 2 languages are implemented. The other 4 (JavaScript, Rust, C, C++) don't exist in this repo.

**No tests, no packaging, no CI.**
