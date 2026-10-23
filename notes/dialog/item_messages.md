# Item messages

Messages the game builds in `$7E:6100` instead of reading them from a scene (`src/dialog/chest.s`).

## Chest, field find, inventory full

- Chest (C2:05F2) and field find (syscall 55, C6:DD40): one item or a Fol amount, then the suffix.
- Inventory full: C2:5169, after a chest message closes when C6:D6B9 cannot add the item.

## Item list (C6:DAA4, field state `$0598` = 2)

- `$02EF`: four slot words, filled by CA:C4EF from the `$7F:B000` / `B240` / `B480` entries 0x200-0x23F. A fifth
  item hangs the game there on purpose (`bcs` to itself).
- A slot word: item id low byte, bit 15 the id's ninth bit, a count in bits 8-13. Zero = empty, skipped.
- C6:DBB4 adds each slot to the inventory (C6:D6B9, the count capped at 20).
- C6:DAD7 lists the names; the count is not shown. Each name is `[color] 6, [item] 0x1387 + id, [color] 2`.
- The original joined the names with "、" and left the line breaks to the engine. With the French names, the
  engine's own break cut a name and a second one drew over the line before. The patch's builder breaks between
  names from a width table (`tools/item_list.py`), and moves to a new page past 3 lines.
- A first slot left empty made the original read past the list (its counter was never set).
- C6:38AF sets the state. What fills the `$7F:B000` entries in play is not known yet.
