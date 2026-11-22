"""
The menus' 8x8 VWF records (src/menu/vwf8.s) in battle (notes/vram/battle.md). The battle draws names8 strings by id
(`C0:3FA3`: party window, enemy names) and 8x8 strings at A:Y (`C0:4154`, a copy of the menus' `CA:BCAD`: the item
list, ...) into its two BG3 shadows ($7E:5100 / $5900, X = the offset in both, $24 = palette and priority). A string
with a record is drawn from pool tiles; anything else (party names from RAM, numbers) by the game.

The fight's start (`C1:0006`, before the item names table) opens the battle pool (a string drawn before it, in a
savestate taken mid-fight, opens it too), its end (`C0:20F7`) the menus' again; the line-216 IRQ's DMA list
uploads the queued tiles (`C0:0188`, its wait for V-blank). Switched by BATTLE_VWF8 in a816.toml.
"""

.import "core/preamble"
.import "menu/vwf8"

.if BATTLE_VWF8 {
    _OFFSET = 0x22  ; the game's: X in the shadows
    _PALETTE = 0x24  ; the game's: palette and priority word
    _SHADOW := 0x5100
    _NAMES := 0x0DF6  ; names8's strings in bank D7, from the offset list

; Fight start: `jsl C8:1050` (the item names table).
    .alloc at 0xC10006 size 4 {
        jsl battle_vwf8_open
    }

; C0:3FA3 found the id at D7:06FA + Y: `lda $0000,y / tay` (M16 X16, DB = D7).
    .alloc at 0xC03FD2 size 4 {
        jml battle_vwf8_name
    }

; C0:4154: `sta $24 / stx $22 / plb` (M16 X16, the string's bank on the stack, Y = its address).
    .alloc at 0xC04163 size 5 {
        jml battle_vwf8_string
        nop
    }

; The DMA list's end: `lda $4212 / bpl` (wait for V-blank).
    .alloc at 0xC00188 size 5 {
        jsl vwf8_drain_battle
        nop
    }

    .alloc battle_vwf8_code in text16 {
        .a16
        .i16
battle_vwf8_open:
"""The battle pool, then the item names table the hook replaced."""
        php
        sep #0x20
        jsl vwf8_battle_open
        plp
        jml 0xC81050

battle_vwf8_name:
"""
The name's offset into Y; drawn from its record (C0:4061: the writer's return) or by the game (C0:3FD6). An L/R
window name ($20 = its names8 id) whose special move fits the row is drawn from the move's battle16 record instead.
"""
        lda.b 0x20
        sec
        sbc.w #VWF8_LR_FIRST
        cmp.w #VWF8_LR_COUNT
        bcs _plain
        tax
        lda.l vwf8_lr, x
        and.w #0x00FF
        cmp.w #VWF8_NO_TALENT
        beq _plain
        phy
        jsr.w _draw_talent
        ply
        bcs _name_drawn
_plain:
        lda.w 0x0000, y
        tay
        phy
        clc
        adc.w #_NAMES
        tay
        jsr.w _draw
        ply
        bcs _name_drawn
        jml 0xC03FD6
_name_drawn:
        jml 0xC04061

battle_vwf8_string:
"""The hook's three instructions, then the string from its record (C0:41E1: the writer's end) or by the game."""
        sta.b _PALETTE
        stx.b _OFFSET
        plb
        jsr.w _draw
        bcs _string_drawn
        jml 0xC04168
_string_drawn:
        jml 0xC041E1

_draw_talent:
"""
The special move at combo position A (vwf8_combos) into the battle shadows from $22: carry set and X past its cells
when drawn, else X = $22. M16 X16; vwf8's direct page ($20-$27) saved around the call.
"""
        pha
        sep #0x20
        jsl vwf8_battle_ready
        rep #0x20
        pei (0x20)
        pei (0x22)
        pei (0x24)
        pei (0x26)
        lda 9, s  ; the combo position
        clc
        adc.w #VWF8_KEYS
        sta.l vwf8.id
        lda 9, s
        asl
        asl
        tax
        lda.l vwf8_combos, x
        sta.b 0x20
        lda.l vwf8_combos + 2, x
        sta.b 0x22
        lda 5, s  ; the game's $22
        clc
        adc.w #_SHADOW
        sta.b 0x24  ; the cursor
        lda 3, s  ; the game's $24
        xba
        and.w #0x00FF
        sta.b 0x26  ; the attribute, $27 = 0
        sep #0x20
        jsl vwf8_record
        rep #0x20
        bcc _talent_refused
        txa
        sec
        sbc.w #_SHADOW
        tax
        pla
        sta.b 0x26
        pla
        sta.b 0x24
        pla
        sta.b 0x22
        pla
        sta.b 0x20
        pla
        sec
        rts
_talent_refused:
        pla
        sta.b 0x26
        pla
        sta.b 0x24
        pla
        sta.b 0x22
        pla
        sta.b 0x20
        pla
        ldx.b _OFFSET
        clc
        rts

_draw:
"""
The string at DB:Y into the battle shadows from $22: carry set and X past its cells when drawn, else X = $22 and Y
kept. M16 X16; vwf8's direct page ($20-$27) saved around the call.
"""
        phy
        sep #0x20
        jsl vwf8_battle_ready
        rep #0x20
        pei (0x20)
        pei (0x22)
        pei (0x24)
        pei (0x26)
        sty.b 0x20
        lda.b _OFFSET
        clc
        adc.w #_SHADOW
        sta.b 0x24  ; the cursor
        phb
        phb
        pla  ; DB twice
        and.w #0x00FF
        sta.b 0x22  ; the bank, then $23 = 0
        lda 3, s  ; the game's $24
        xba
        and.w #0x00FF  ; the attribute byte, $27 = 0: no cell limit
        sta.b 0x26
        sep #0x20
        jsl vwf8_string
        rep #0x20
        bcc _refused
        txa
        sec
        sbc.w #_SHADOW
        tax
        pla
        sta.b 0x26
        pla
        sta.b 0x24
        pla
        sta.b 0x22
        pla
        sta.b 0x20
        ply
        sec
        rts
_refused:
        pla
        sta.b 0x26
        pla
        sta.b 0x24
        pla
        sta.b 0x22
        pla
        sta.b 0x20
        ply
        ldx.b _OFFSET
        clc
        rts
    }
}
