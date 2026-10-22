# Scene event VM

`uv run python -m tools.scene_script NN [--edited] [--bytes]` lists scene NN's event data, with the French first
line next to each message. The module docstring has the byte formats.

- Dispatcher C2:1271 (per frame, until a yielding opcode), C2:1297 (runs to an FF). Opcode table C2:3769, indexed
  by opcode + 1. VM pc saved in `$0238`, frame countdown `$0234`, call stack at `($FE)`.
- Operand values: C2:310C. Variables at `$7E:FEC3 + index`; system variables through the 24-bit pointer table
  C2:383F. `sys.w[0xc]` is the map id.
- Result register `$0278`: set by `actor_get`, `flag_test` and others, written out by `store_result`.
- Expressions (`set`): C2:12CA, operators C2:16A7 (byte) / C2:16B9 (word), final store C2:16DD.
- Conditions (`if`): C2:17C9, comparators C2:18FE, joiner loop C2:17F7.
- Start-up: the code right after the header (`call setup; loop: wait 1; goto loop`). The header entries are
  triggers (kind, id, address); what fires each kind is not traced yet.

Checked: all 94 scenes sweep clean (scenes 2, 52, 76 end in one stray 0x80); 28k traced instructions from five
saves land on instruction starts with the expected lengths. Most `op_NN` names are still unread.
