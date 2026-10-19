# Cooperative scheduler

- Every task chain roots at `C2:0009` / `C2:0047`; kintsuki's shadow callstack shows the
  stack switches (frame flag 1).
- Dialog runs as a task (`C2:38AB`) and yields once per glyph → typewriter effect.
