#!/usr/bin/env python3
"""
ztest.py - Headless Z-machine v5 interpreter for automated gameplay testing.

Loads a .z5 story file, feeds it a scripted list of commands at each `aread`
(input) call, and prints all screen (stream-1) output to stdout.  Intended for
regression-testing text-adventure gameplay after code changes, since the only
local interpreter (Frotz) is GUI-only and cannot be driven from a pipe.

Usage:
    python ztest.py [--story STORY.z5] [--script cmds.txt] [--seed N] [--mark]
                    [command ...]

If --script is given, its lines are the commands (one per line, '#' = comment).
Remaining positional args are commands (one each).  If neither is given, commands
are read interactively from stdin.

--mark prefixes each command with a "###CMD: <cmd>" line so output can be parsed
per-command.  Default story is adventure_lovecraft.z5 in this directory.
"""

import sys
import os
import struct
import argparse
import random


# ---------------------------------------------------------------------------
# ZSCII alphabet tables (v2+)
# A0/A1 indexed by z-char (6..31); A2 has special entries at 6 (escape) and 7 (nl)
# ---------------------------------------------------------------------------
A0 = "abcdefghijklmnopqrstuvwxyz"
A1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# A2 chars for z-char indices 8..31 (index 6 = escape, 7 = newline handled specially)
A2 = "0123456789.,!?_#'\"/\\-:()"  # length 24 -> indices 8..31
A2_MAP = {c: 8 + i for i, c in enumerate(A2)}  # inverse: char -> z-char index
A2_MAP['\n'] = 7


def signed16(x):
    x &= 0xFFFF
    return x - 0x10000 if x & 0x8000 else x


class Frame:
    __slots__ = ("return_pc", "locals", "stack_base", "store_var", "discard",
                "num_args")

    def __init__(self, return_pc, locals_, stack_base, store_var, discard,
                 num_args):
        self.return_pc = return_pc
        self.locals = locals_
        self.stack_base = stack_base
        self.store_var = store_var
        self.discard = discard
        self.num_args = num_args


class Quit(Exception):
    pass


class ZMachine:
    def __init__(self, story_path, commands, mark=False, seed=None):
        self.original = open(story_path, "rb").read()
        self.mem = bytearray(self.original)
        self.version = self.mem[0]
        if self.version != 5:
            raise RuntimeError("only z-machine v5 supported, got v%d"
                               % self.version)
        self.commands = commands
        self.cmd_idx = 0
        self.mark = mark
        self.out_buf = []
        self.running = True

        # header
        self.high_mem = self.word(0x04)
        self.initial_pc = self.word(0x06)
        self.dict_addr = self.word(0x08)
        self.obj_table = self.word(0x0a)
        self.globals = self.word(0x0c)
        self.static_mem = self.word(0x0e)
        self.abbrev_table = self.word(0x18)

        # dictionary header
        d = self.dict_addr
        self.dict_n_sep = self.mem[d]
        self.dict_seps = set(self.mem[d + 1: d + 1 + self.dict_n_sep])
        self.dict_entry_len = self.mem[d + 1 + self.dict_n_sep]
        self.dict_n_entries = struct.unpack(">H",
            self.mem[d + 2 + self.dict_n_sep: d + 4 + self.dict_n_sep])[0]
        self.dict_base = d + 4 + self.dict_n_sep
        self.dict_encoded_len = 6  # v5 Inform: 9 z-chars = 3 words = 6 bytes

        # packed-address multiplier (v1-3: 2, v4-5: 4)
        self.pack_mult = 4

        # execution state
        self.pc = self.initial_pc
        self.stack = []
        # top-level frame: no locals, returning quits
        self.frames = [Frame(None, [], 0, None, True, 0)]
        self.current_frame = self.frames[0]

        # output streams: 1=screen, 3=memory stack
        self.stream1_on = True
        self.stream3 = []  # list of [table_addr, offset]

        # windows
        self.cur_window = 0

        # undo
        self.undo_snapshot = None
        self.undo_seq = 0

        # random
        if seed is not None:
            random.seed(seed)

    # ---- memory access ----
    def byte(self, a):
        return self.mem[a]

    def word(self, a):
        return (self.mem[a] << 8) | self.mem[a + 1]

    def set_byte(self, a, v):
        self.mem[a] = v & 0xFF

    def set_word(self, a, v):
        v &= 0xFFFF
        self.mem[a] = (v >> 8) & 0xFF
        self.mem[a + 1] = v & 0xFF

    # ---- variables ----
    def read_var(self, v):
        if v == 0:
            return self.pop()
        if v < 16:
            return self.current_frame.locals[v - 1]
        return self.word(self.globals + 2 * (v - 16))

    def write_var(self, v, val):
        val &= 0xFFFF
        if v == 0:
            self.push(val)
        elif v < 16:
            self.current_frame.locals[v - 1] = val
        else:
            self.set_word(self.globals + 2 * (v - 16), val)

    def peek_var(self, v):
        # read without popping stack
        if v == 0:
            return self.stack[-1]
        return self.read_var(v)

    def poke_var(self, v, val):
        # write without pushing onto stack (replace top)
        val &= 0xFFFF
        if v == 0:
            self.stack[-1] = val
        else:
            self.write_var(v, val)

    # ---- eval stack ----
    def push(self, v):
        self.stack.append(v & 0xFFFF)

    def pop(self):
        return self.stack.pop()

    # ---- output ----
    def emit(self, ch):
        # route to stream3 (memory) or stream1 (screen)
        if self.stream3:
            table, off = self.stream3[-1]
            self.set_byte(table + off, ord(ch) & 0xFF)
            self.stream3[-1][1] = off + 1
            return
        if self.stream1_on:
            self.out_buf.append(ch)

    def emit_zscii(self, z):
        if z == 13:
            self.emit("\n")
        elif 32 <= z <= 126:
            self.emit(chr(z))
        elif z == 9:
            self.emit("\t")
        elif z == 0:
            pass
        elif 155 <= z <= 251:
            # extended ZSCII; map a few common ones, else '?'
            self.emit("?")
        else:
            self.emit("?")

    # ---- text decoding ----
    def decode_zstring(self, addr):
        """Decode the z-encoded string at byte addr, emitting chars.
        Returns the address past the end of the string."""
        zchars = []
        while True:
            w = self.word(addr)
            addr += 2
            zchars.append((w >> 10) & 0x1F)
            zchars.append((w >> 5) & 0x1F)
            zchars.append(w & 0x1F)
            if w & 0x8000:
                break
        self._emit_zchars(zchars)
        return addr

    def _emit_zchars(self, zchars):
        i = 0
        n = len(zchars)
        shift_pending = False
        shift_alpha = 0
        while i < n:
            z = zchars[i]
            i += 1
            if z == 0:
                self.emit(" ")
                shift_pending = False
            elif z in (1, 2, 3):
                # abbreviation: next z-char is index
                if i < n:
                    nxt = zchars[i]
                    i += 1
                    abbr = 32 * (z - 1) + nxt
                    self._decode_abbrev(abbr)
                shift_pending = False
            elif z == 4:
                shift_pending = True
                shift_alpha = 1
            elif z == 5:
                shift_pending = True
                shift_alpha = 2
            else:
                # z >= 6
                a = shift_alpha if shift_pending else 0
                shift_pending = False
                if a == 0:
                    self.emit(A0[z - 6])
                elif a == 1:
                    self.emit(A1[z - 6])
                else:
                    if z == 6:
                        # 10-bit ZSCII escape
                        if i + 1 < n:
                            hi = zchars[i]
                            lo = zchars[i + 1]
                            i += 2
                            self.emit_zscii((hi << 5) | lo)
                    elif z == 7:
                        self.emit("\n")
                    else:
                        self.emit(A2[z - 8])

    def _decode_abbrev(self, abbr):
        pa = self.word(self.abbrev_table + 2 * abbr)
        self.decode_zstring(pa * self.pack_mult)

    # ---- objects ----
    def obj_addr(self, obj):
        # v5: 63 default-property words (126 bytes), 14-byte entries
        return self.obj_table + 126 + (obj - 1) * 14

    def get_attr(self, obj, attr):
        a = self.obj_addr(obj)
        byte_idx = attr // 8
        bit = 7 - (attr % 8)
        return (self.mem[a + byte_idx] >> bit) & 1

    def set_attr(self, obj, attr):
        a = self.obj_addr(obj)
        byte_idx = attr // 8
        bit = 7 - (attr % 8)
        self.mem[a + byte_idx] |= (1 << bit)

    def clear_attr(self, obj, attr):
        a = self.obj_addr(obj)
        byte_idx = attr // 8
        bit = 7 - (attr % 8)
        self.mem[a + byte_idx] &= ~(1 << bit) & 0xFF

    def obj_parent(self, obj):
        return self.word(self.obj_addr(obj) + 6)

    def obj_sibling(self, obj):
        return self.word(self.obj_addr(obj) + 8)

    def obj_child(self, obj):
        return self.word(self.obj_addr(obj) + 10)

    def set_parent(self, obj, v):
        self.set_word(self.obj_addr(obj) + 6, v)

    def set_sibling(self, obj, v):
        self.set_word(self.obj_addr(obj) + 8, v)

    def set_child(self, obj, v):
        self.set_word(self.obj_addr(obj) + 10, v)

    def obj_prop_table_addr(self, obj):
        return self.word(self.obj_addr(obj) + 12)

    def obj_name(self, obj):
        pa = self.obj_prop_table_addr(obj)
        tlen = self.mem[pa]
        if tlen == 0:
            return ""
        # capture name to a temp buffer
        saved = self.out_buf
        self.out_buf = []
        self.decode_zstring(pa + 1)
        name = "".join(self.out_buf)
        self.out_buf = saved
        return name

    def insert_obj(self, obj, dest):
        # detach obj from current parent's child chain
        self.remove_obj(obj)
        # make obj first child of dest
        old_child = self.obj_child(dest)
        self.set_parent(obj, dest)
        self.set_sibling(obj, old_child)
        self.set_child(dest, obj)

    def remove_obj(self, obj):
        parent = self.obj_parent(obj)
        if parent == 0:
            return
        child = self.obj_child(parent)
        if child == obj:
            self.set_child(parent, self.obj_sibling(obj))
        else:
            while child != 0:
                sib = self.obj_sibling(child)
                if sib == obj:
                    self.set_sibling(child, self.obj_sibling(obj))
                    break
                child = sib
        self.set_parent(obj, 0)
        self.set_sibling(obj, 0)

    # ---- properties ----
    def _prop_list_iter(self, obj):
        pa = self.obj_prop_table_addr(obj)
        tlen = self.mem[pa]
        p = pa + 1 + 2 * tlen
        while True:
            size_byte = self.mem[p]
            if size_byte == 0:
                return
            if size_byte & 0x80:
                # two-byte form: bit7 set on first byte
                num = size_byte & 0x3F
                size = self.mem[p + 1] & 0x3F
                if size == 0:
                    size = 64
                data_addr = p + 2
                p += 2 + size
            else:
                # one-byte form: bits 0-5 = number, bit 6 = size (1 or 2)
                num = size_byte & 0x3F
                size = 2 if (size_byte & 0x40) else 1
                data_addr = p + 1
                p += 1 + size
            yield num, size, data_addr

    def get_prop_addr(self, obj, prop):
        for num, size, da in self._prop_list_iter(obj):
            if num == prop:
                return da
            if num < prop:
                break
        return 0

    def get_prop_len(self, prop_data_addr):
        if prop_data_addr == 0:
            return 0
        return self._prop_len_from_data(prop_data_addr)

    def _prop_len_from_data(self, data_addr):
        # The byte immediately before the data is the size byte; for the
        # two-byte form, that second byte always has bit 7 set, and for the
        # one-byte form the size byte has bit 7 clear.
        b = self.mem[data_addr - 1]
        if b & 0x80:
            size = b & 0x3F
            return size if size else 64
        return 2 if (b & 0x40) else 1

    def get_prop(self, obj, prop):
        a = self.get_prop_addr(obj, prop)
        if a == 0:
            # default property
            return self.word(self.obj_table + 2 * (prop - 1))
        size = self._prop_len_from_data(a)
        if size == 1:
            return self.mem[a]
        elif size == 2:
            return self.word(a)
        else:
            return self.word(a)  # spec: 2 bytes for size>2? Standard says return
            # the first 2 bytes for size 2; for size>2 undefined (Inform returns
            # word). We return word.

    def put_prop(self, obj, prop, value):
        a = self.get_prop_addr(obj, prop)
        if a == 0:
            return  # cannot put a default; spec ignores
        size = self._prop_len_from_data(a)
        if size == 1:
            self.set_byte(a, value & 0xFF)
        else:
            self.set_word(a, value & 0xFFFF)

    def get_next_prop(self, obj, prop):
        if prop == 0:
            # first property number
            for num, size, da in self._prop_list_iter(obj):
                return num
            return 0
        found = False
        for num, size, da in self._prop_list_iter(obj):
            if found:
                return num
            if num == prop:
                found = True
        return 0

    # ---- dictionary / tokenization ----
    def encode_word(self, word):
        """Encode a lowercased word into 6 bytes (3 words, 9 z-chars) for
        dictionary matching.  Returns bytes."""
        zchars = []
        for c in word:
            if 'a' <= c <= 'z':
                zchars.append(6 + (ord(c) - ord('a')))
            elif c == ' ':
                zchars.append(0)
            elif c in A2_MAP:
                idx = A2_MAP[c]
                if idx == 7:
                    # newline: encode via ZSCII escape
                    zchars.append(5)
                    zchars.append(6)
                    zchars.append(0)
                    zchars.append(13 & 0x1F)
                else:
                    zchars.append(5)
                    zchars.append(idx)
            else:
                # ZSCII escape (10-bit)
                zscii = ord(c) & 0xFF
                zchars.append(5)
                zchars.append(6)
                zchars.append((zscii >> 5) & 0x1F)
                zchars.append(zscii & 0x1F)
        zchars = zchars[:9]
        while len(zchars) < 9:
            zchars.append(5)  # pad
        words = []
        for i in range(0, 9, 3):
            w = (zchars[i] << 10) | (zchars[i + 1] << 5) | zchars[i + 2]
            words.append(w)
        words[-1] |= 0x8000
        return struct.pack(">HHH", *words)

    def dict_lookup(self, word):
        """Return the dictionary entry address for word, or 0 if not found.
        Uses binary search on the 6-byte encoded prefix."""
        if not word:
            return 0
        enc = self.encode_word(word.lower())
        lo, hi = 0, self.dict_n_entries - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            ea = self.dict_base + mid * self.dict_entry_len
            entry = bytes(self.mem[ea:ea + self.dict_encoded_len])
            if entry == enc:
                return ea
            elif entry < enc:
                lo = mid + 1
            else:
                hi = mid - 1
        return 0

    def tokenize(self, text_buf, parse_buf):
        """Read input line, store in text buffer (v5 format), tokenize into
        parse buffer."""
        # read command
        line = self.next_command()
        if line is None:
            raise Quit()
        line = line.lower()
        maxchars = self.mem[text_buf]  # buffer[0]
        # store chars at buffer[2..], truncated to maxchars
        chars = line[:maxchars]
        self.set_byte(text_buf + 1, len(chars))
        for k, ch in enumerate(chars):
            self.set_byte(text_buf + 2 + k, ord(ch) & 0xFF)
        # tokenize
        maxwords = self.mem[parse_buf]
        words = []
        i = 0
        # positions are byte offsets in text buffer; text starts at offset 2
        while i < len(chars):
            c = chars[i]
            if c == ' ':
                i += 1
                continue
            if ord(c) in self.dict_seps:
                words.append((c, 2 + i))
                i += 1
                continue
            start = i
            buf_start = 2 + i
            while i < len(chars) and chars[i] != ' ' and ord(chars[i]) not in self.dict_seps:
                i += 1
            words.append((chars[start:i], buf_start))
        n = min(len(words), maxwords)
        self.set_byte(parse_buf + 1, n)
        for idx in range(n):
            wtext, wpos = words[idx]
            base = parse_buf + 2 + idx * 4
            da = self.dict_lookup(wtext)
            self.set_word(base, da)
            self.set_byte(base + 2, len(wtext))
            self.set_byte(base + 3, wpos)

    def next_command(self):
        if self.cmd_idx < len(self.commands):
            cmd = self.commands[self.cmd_idx]
            self.cmd_idx += 1
            if self.mark:
                # emit marker into output
                self.out_buf.append("\n###CMD: %s\n" % cmd)
            return cmd
        return None

    # ---- routine calls ----
    def packed_addr(self, p):
        return p * self.pack_mult  # v5 byte addresses can exceed 0xffff

    def call_routine(self, packed, args, store_var, discard):
        if packed == 0:
            # calling address 0 returns false immediately
            if not discard and store_var is not None:
                self.write_var(store_var, 0)
            return
        addr = self.packed_addr(packed)
        nlocals = self.mem[addr]
        addr += 1
        # NOTE: the local Inform 6.44 build emits routines as
        # [nlocals byte][code] with NO local initial-value words (all locals
        # start at 0).  Standard Z-machine expects nlocals words here; this
        # compiler omits them, so we go straight to code.
        locals_ = [0] * nlocals
        # pass arguments into locals
        for i in range(min(len(args), nlocals)):
            locals_[i] = args[i] & 0xFFFF
        frame = Frame(return_pc=self.pc, locals_=locals_,
                      stack_base=len(self.stack), store_var=store_var,
                      discard=discard, num_args=len(args))
        self.frames.append(frame)
        self.current_frame = frame
        self.pc = addr

    def do_return(self, value):
        frame = self.frames.pop()
        # truncate eval stack to caller's base
        del self.stack[frame.stack_base:]
        if frame.return_pc is None:
            raise Quit()
        self.pc = frame.return_pc
        self.current_frame = self.frames[-1]
        if not frame.discard and frame.store_var is not None:
            self.write_var(frame.store_var, value & 0xFFFF)

    # ---- branch handling ----
    def read_branch(self):
        b1 = self.mem[self.pc]
        self.pc += 1
        on_true = (b1 & 0x80) != 0
        if b1 & 0x40:
            offset = b1 & 0x3F
        else:
            b2 = self.mem[self.pc]
            self.pc += 1
            offset = ((b1 & 0x3F) << 8) | b2
            if offset & 0x2000:
                offset -= 0x4000
        return on_true, offset

    def do_branch(self, condition):
        on_true, offset = self.read_branch()
        take = (condition == on_true)
        if not take:
            return
        if offset == 0:
            self.do_return(0)
        elif offset == 1:
            self.do_return(1)
        else:
            self.pc = self.pc + offset - 2

    def read_store(self):
        v = self.mem[self.pc]
        self.pc += 1
        return v

    # ---- operand reading ----
    def read_operand(self, op_type):
        if op_type == 0:  # large constant
            v = self.word(self.pc)
            self.pc += 2
            return v
        elif op_type == 1:  # small constant
            v = self.mem[self.pc]
            self.pc += 1
            return v
        elif op_type == 2:  # variable
            vnum = self.mem[self.pc]
            self.pc += 1
            return self.read_var(vnum)
        return 0

    # ---- main run loop ----
    def run(self):
        try:
            while self.running:
                self.step()
        except Quit:
            pass
        return "".join(self.out_buf)

    def step(self):
        op = self.mem[self.pc]
        self.pc += 1
        if op == 0xBE:
            self.exec_ext()
            return
        form = op >> 6
        if form in (0, 1):
            # long form -> 2OP
            t1 = 2 if (op & 0x40) else 1
            t2 = 2 if (op & 0x20) else 1
            opcode = op & 0x1F
            a = self.read_operand(t1)
            b = self.read_operand(t2)
            self.exec_2op(opcode, a, b)
        elif form == 2:
            # short form
            op_type = (op >> 4) & 0x03
            opcode = op & 0x0F
            if op_type == 3:
                # 0OP
                self.exec_0op(opcode)
            else:
                a = self.read_operand(op_type)
                self.exec_1op(opcode, a)
        else:
            # variable form (form == 3)
            is_var = (op & 0x20) != 0
            opcode = op & 0x1F
            if opcode in (12, 26) and is_var:
                # two operand-type bytes (call_vs2 / call_vn2)
                tb1 = self.mem[self.pc]; self.pc += 1
                tb2 = self.mem[self.pc]; self.pc += 1
                ops = []
                for shift in (6, 4, 2, 0):
                    t = (tb1 >> shift) & 3
                    if t == 3:
                        break
                    ops.append(self.read_operand(t))
                if len(ops) == 4:
                    for shift in (6, 4, 2, 0):
                        t = (tb2 >> shift) & 3
                        if t == 3:
                            break
                        ops.append(self.read_operand(t))
                if is_var:
                    self.exec_var(opcode, ops)
                else:
                    # 2OP with >2 operands (e.g. call_2s variants use VAR form)
                    self.exec_2op_var(opcode, ops)
            else:
                tb = self.mem[self.pc]; self.pc += 1
                ops = []
                for shift in (6, 4, 2, 0):
                    t = (tb >> shift) & 3
                    if t == 3:
                        break
                    ops.append(self.read_operand(t))
                if is_var:
                    self.exec_var(opcode, ops)
                else:
                    self.exec_2op_var(opcode, ops)

    # ---- 2OP ----
    def exec_2op(self, opcode, a, b):
        self.exec_2op_core(opcode, a, b)

    def exec_2op_var(self, opcode, ops):
        # variable-form 2OP: take first two operands
        a = ops[0] if len(ops) > 0 else 0
        b = ops[1] if len(ops) > 1 else 0
        self.exec_2op_core(opcode, a, b)

    def exec_2op_core(self, opcode, a, b):
        if opcode == 1:  # je
            # in VAR form, je can take up to 4 operands; but long form only 2.
            self.do_branch(a == b)
        elif opcode == 2:  # jl
            self.do_branch(signed16(a) < signed16(b))
        elif opcode == 3:  # jg
            self.do_branch(signed16(a) > signed16(b))
        elif opcode == 4:  # dec_chk
            val = signed16(self.peek_var(a))
            val -= 1
            self.poke_var(a, val & 0xFFFF)
            self.do_branch(val < signed16(b))
        elif opcode == 5:  # inc_chk
            val = signed16(self.peek_var(a))
            val += 1
            self.poke_var(a, val & 0xFFFF)
            self.do_branch(val > signed16(b))
        elif opcode == 6:  # jin
            self.do_branch(self.obj_parent(a) == b)
        elif opcode == 7:  # test
            self.do_branch((a & b) == b)
        elif opcode == 8:  # or
            self.write_var(self.read_store(), (a | b) & 0xFFFF)
        elif opcode == 9:  # and
            self.write_var(self.read_store(), (a & b) & 0xFFFF)
        elif opcode == 10:  # test_attr
            self.do_branch(self.get_attr(a, b) == 1)
        elif opcode == 11:  # set_attr
            self.set_attr(a, b)
        elif opcode == 12:  # clear_attr
            self.clear_attr(a, b)
        elif opcode == 13:  # store
            self.write_var(a, b)
        elif opcode == 14:  # insert_obj
            self.insert_obj(a, b)
        elif opcode == 15:  # loadw
            self.write_var(self.read_store(), self.word(a + 2 * b))
        elif opcode == 16:  # loadb
            self.write_var(self.read_store(), self.mem[a + b])
        elif opcode == 17:  # get_prop
            self.write_var(self.read_store(), self.get_prop(a, b))
        elif opcode == 18:  # get_prop_addr
            self.write_var(self.read_store(), self.get_prop_addr(a, b))
        elif opcode == 19:  # get_next_prop
            self.write_var(self.read_store(), self.get_next_prop(a, b))
        elif opcode == 20:  # add
            self.write_var(self.read_store(), (a + b) & 0xFFFF)
        elif opcode == 21:  # sub
            self.write_var(self.read_store(), (a - b) & 0xFFFF)
        elif opcode == 22:  # mul
            self.write_var(self.read_store(), (a * b) & 0xFFFF)
        elif opcode == 23:  # div
            sa, sb = signed16(a), signed16(b)
            if sb == 0:
                raise RuntimeError("div by zero")
            q = abs(sa) // abs(sb)
            if (sa < 0) != (sb < 0):
                q = -q
            self.write_var(self.read_store(), q & 0xFFFF)
        elif opcode == 24:  # mod
            sa, sb = signed16(a), signed16(b)
            if sb == 0:
                raise RuntimeError("mod by zero")
            r = abs(sa) % abs(sb)
            if sa < 0:
                r = -r
            self.write_var(self.read_store(), r & 0xFFFF)
        elif opcode == 25:  # call_2s (v4+)
            store = self.read_store()
            self.call_routine(a, [b], store, False)
        elif opcode == 26:  # call_2n (v5+)
            self.call_routine(a, [b], None, True)
        elif opcode == 27:  # set_colour (v5+)
            pass  # no-op (no colour support)
        elif opcode == 28:  # throw (v5+)
            token = b
            while len(self.frames) > token:
                f = self.frames.pop()
                del self.stack[f.stack_base:]
            self.do_return(a)
        else:
            raise RuntimeError("unknown 2OP opcode %d at pc=%x" % (opcode, self.pc))

    # ---- 1OP ----
    def exec_1op(self, opcode, a):
        if opcode == 0:  # jz
            self.do_branch(a == 0)
        elif opcode == 1:  # get_sibling
            store = self.read_store()
            sib = self.obj_sibling(a)
            self.write_var(store, sib)
            self.do_branch(sib != 0)
        elif opcode == 2:  # get_child
            store = self.read_store()
            ch = self.obj_child(a)
            self.write_var(store, ch)
            self.do_branch(ch != 0)
        elif opcode == 3:  # get_parent
            self.write_var(self.read_store(), self.obj_parent(a))
        elif opcode == 4:  # get_prop_len
            self.write_var(self.read_store(), self.get_prop_len(a))
        elif opcode == 5:  # inc
            val = (signed16(self.peek_var(a)) + 1) & 0xFFFF
            self.poke_var(a, val)
        elif opcode == 6:  # dec
            val = (signed16(self.peek_var(a)) - 1) & 0xFFFF
            self.poke_var(a, val)
        elif opcode == 7:  # print_addr
            self.decode_zstring(a)
        elif opcode == 8:  # call_1s (v4+)
            store = self.read_store()
            self.call_routine(a, [], store, False)
        elif opcode == 9:  # remove_obj
            self.remove_obj(a)
        elif opcode == 10:  # print_obj
            # print object's short name
            pa = self.obj_prop_table_addr(a)
            tlen = self.mem[pa]
            if tlen:
                self.decode_zstring(pa + 1)
        elif opcode == 11:  # ret
            self.do_return(a)
        elif opcode == 12:  # jump
            off = signed16(a)
            self.pc = self.pc + off - 2
        elif opcode == 13:  # print_paddr
            self.decode_zstring(a * self.pack_mult)
        elif opcode == 14:  # load
            store = self.read_store()
            self.write_var(store, self.read_var(a))
        elif opcode == 15:  # v5: call_1n
            self.call_routine(a, [], None, True)
        else:
            raise RuntimeError("unknown 1OP opcode %d" % opcode)

    # ---- 0OP ----
    def exec_0op(self, opcode):
        if opcode == 0:  # rtrue
            self.do_return(1)
        elif opcode == 1:  # rfalse
            self.do_return(0)
        elif opcode == 2:  # print (literal)
            self.pc = self.decode_zstring(self.pc)
        elif opcode == 3:  # print_ret
            self.pc = self.decode_zstring(self.pc)
            self.emit("\n")
            self.do_return(1)
        elif opcode == 4:  # nop
            pass
        elif opcode == 5:  # save (v5: store result)
            store = self.read_store()
            self.write_var(store, 0)  # failure
        elif opcode == 6:  # restore (v5: store result)
            store = self.read_store()
            self.write_var(store, 0)  # failure
        elif opcode == 7:  # restart
            self.mem = bytearray(self.original)
            self.pc = self.initial_pc
            self.stack = []
            self.frames = [Frame(None, [], 0, None, True, 0)]
            self.current_frame = self.frames[0]
            self.stream1_on = True
            self.stream3 = []
        elif opcode == 8:  # ret_popped
            self.do_return(self.pop())
        elif opcode == 9:  # catch (v5, store)
            store = self.read_store()
            self.write_var(store, len(self.frames))
        elif opcode == 10:  # quit
            raise Quit()
        elif opcode == 11:  # new_line
            self.emit("\n")
        elif opcode == 12:  # show_status (v3 only; no-op in v5)
            pass
        elif opcode == 13:  # verify
            self.do_branch(True)
        elif opcode == 15:  # piracy (v5)
            self.do_branch(True)
        else:
            raise RuntimeError("unknown 0OP opcode %d" % opcode)

    # ---- VAR ----
    def exec_var(self, opcode, ops):
        if opcode == 0:  # call (call_vs)
            store = self.read_store()
            self.call_routine(ops[0], ops[1:], store, False)
        elif opcode == 1:  # storew
            self.set_word(ops[0] + 2 * ops[1], ops[2])
        elif opcode == 2:  # storeb
            self.set_byte(ops[0] + ops[1], ops[2])
        elif opcode == 3:  # put_prop
            self.put_prop(ops[0], ops[1], ops[2])
        elif opcode == 4:  # aread (v5)
            store = self.read_store()
            text_buf = ops[0]
            parse_buf = ops[1] if len(ops) > 1 else 0
            self.tokenize(text_buf, parse_buf)
            self.write_var(store, 10)  # terminator = newline
        elif opcode == 5:  # print_char
            self.emit_zscii(ops[0])
        elif opcode == 6:  # print_num
            self.emit(str(signed16(ops[0])))
        elif opcode == 7:  # random
            r = signed16(ops[0])
            store = self.read_store()
            if r > 0:
                self.write_var(store, random.randint(1, r))
            elif r < 0:
                random.seed(-r)
                self.write_var(store, 0)
            else:
                random.seed()
                self.write_var(store, 0)
        elif opcode == 8:  # push
            self.push(ops[0])
        elif opcode == 9:  # pull
            val = self.pop()
            self.write_var(ops[0], val)
        elif opcode == 10:  # split_window
            pass
        elif opcode == 11:  # set_window
            self.cur_window = ops[0]
        elif opcode == 12:  # call_vs2
            store = self.read_store()
            self.call_routine(ops[0], ops[1:], store, False)
        elif opcode == 13:  # erase_window
            pass
        elif opcode == 14:  # erase_line
            pass
        elif opcode == 15:  # set_cursor
            pass
        elif opcode == 16:  # get_cursor
            pass
        elif opcode == 17:  # set_text_style
            pass
        elif opcode == 18:  # buffer_mode
            pass
        elif opcode == 19:  # output_stream
            self.output_stream(ops)
        elif opcode == 20:  # input_stream
            pass
        elif opcode == 21:  # sound_effect
            pass
        elif opcode == 22:  # read_char (v4+)
            store = self.read_store()
            # consume next command's first char? We just return newline.
            self.write_var(store, 10)
        elif opcode == 23:  # scan_table
            store = self.read_store()
            x = ops[0]
            table = ops[1]
            length = ops[2]
            field_size = ops[3] if len(ops) > 3 else 2
            form = ops[4] if len(ops) > 4 else 0  # 0=word, 0x82=byte
            addr = 0
            for i in range(length):
                ea = table + i * field_size
                if form == 0x82:
                    val = self.mem[ea]
                else:
                    val = self.word(ea)
                if val == x:
                    addr = ea
                    break
            self.write_var(store, addr)
            self.do_branch(addr != 0)
        elif opcode == 24:  # not (v5+)
            self.write_var(self.read_store(), (~ops[0]) & 0xFFFF)
        elif opcode == 25:  # call_vn (v5+)
            self.call_routine(ops[0], ops[1:], None, True)
        elif opcode == 26:  # call_vn2 (v5+)
            self.call_routine(ops[0], ops[1:], None, True)
        elif opcode == 27:  # tokenise (v5+)
            # tokenise text parse dictionary flag
            self._tokenise_into(ops)
        elif opcode == 28:  # encode_text (v5+)
            # encode_text zscii-text length from to
            # store encoded form at 'to'
            ztext = ops[0]
            length = ops[1]
            to = ops[2]
            # read ZSCII chars from ztext for 'length' chars, encode, write to 'to'
            word = "".join(chr(self.mem[ztext + i]) for i in range(length))
            enc = self.encode_word(word.lower())
            for k, byte in enumerate(enc):
                self.set_byte(to + k, byte)
        elif opcode == 29:  # copy_table (v5+)
            first = ops[0]
            second = ops[1]
            size = signed16(ops[2])
            n = size if size >= 0 else -size
            if second == 0:
                for i in range(n):
                    self.set_byte(first + i, 0)
            else:
                if size < 0 or second > first:
                    for i in range(n - 1, -1, -1):
                        self.set_byte(second + i, self.mem[first + i])
                else:
                    for i in range(n):
                        self.set_byte(second + i, self.mem[first + i])
        elif opcode == 30:  # print_table (v5+)
            text = ops[0]
            width = ops[1]
            height = ops[2] if len(ops) > 2 else 1
            skip = ops[3] if len(ops) > 3 else 0
            if height == 0:
                height = 1
            addr = text
            for _r in range(height):
                for _c in range(width):
                    self.emit_zscii(self.mem[addr])
                    addr += 1
                addr += skip
                self.emit("\n")
        elif opcode == 31:  # check_arg_count (v5+)
            self.do_branch(self.current_frame.num_args >= ops[0])
        else:
            raise RuntimeError("unknown VAR opcode %d" % opcode)

    def _tokenise_into(self, ops):
        text_buf = ops[0]
        parse_buf = ops[1]
        # re-tokenise the existing text buffer contents
        maxchars = self.mem[text_buf]
        nchars = self.mem[text_buf + 1]
        chars = "".join(chr(self.mem[text_buf + 2 + k]) for k in range(nchars))
        maxwords = self.mem[parse_buf]
        words = []
        i = 0
        while i < len(chars):
            c = chars[i]
            if c == ' ':
                i += 1
                continue
            if ord(c) in self.dict_seps:
                words.append((c, 2 + i))
                i += 1
                continue
            start = i
            buf_start = 2 + i
            while i < len(chars) and chars[i] != ' ' and ord(chars[i]) not in self.dict_seps:
                i += 1
            words.append((chars[start:i], buf_start))
        n = min(len(words), maxwords)
        self.set_byte(parse_buf + 1, n)
        for idx in range(n):
            wtext, wpos = words[idx]
            base = parse_buf + 2 + idx * 4
            da = self.dict_lookup(wtext)
            self.set_word(base, da)
            self.set_byte(base + 2, len(wtext))
            self.set_byte(base + 3, wpos)

    def output_stream(self, ops):
        s = signed16(ops[0])
        table = ops[1] if len(ops) > 1 else 0
        a = abs(s)
        if a == 1:
            self.stream1_on = (s > 0)
        elif a == 2:
            pass  # transcript to file: ignore
        elif a == 3:
            if s > 0:
                self.stream3.append([table, 2])
            elif self.stream3:
                table_addr, off = self.stream3.pop()
                self.set_word(table_addr, off - 2)
        elif a == 4:
            pass

    # ---- extended opcodes ----
    def exec_ext(self):
        op = self.mem[self.pc]
        self.pc += 1
        tb = self.mem[self.pc]
        self.pc += 1
        ops = []
        for shift in (6, 4, 2, 0):
            t = (tb >> shift) & 3
            if t == 3:
                break
            ops.append(self.read_operand(t))
        if op == 0:  # save
            store = self.read_store()
            self.write_var(store, 0)
        elif op == 1:  # restore
            store = self.read_store()
            self.write_var(store, 0)
        elif op == 2:  # log_shift
            store = self.read_store()
            x, n = ops[0] & 0xFFFF, ops[1]
            r = (x << n) & 0xFFFF if n >= 0 else (x >> -n)
            self.write_var(store, r)
        elif op == 3:  # ashift
            store = self.read_store()
            x, n = signed16(ops[0]), ops[1]
            r = (x << n) & 0xFFFF if n >= 0 else (x >> -n)
            self.write_var(store, r & 0xFFFF)
        elif op == 4:  # set_font
            store = self.read_store()
            self.write_var(store, 1)  # previous font (pretend)
        elif op == 5:  # draw_picture
            pass
        elif op == 6:  # picture_data
            self.do_branch(False)
        elif op == 7:  # erase_picture
            pass
        elif op == 8:  # set_margins
            pass
        elif op == 9:  # save_undo
            store = self.read_store()
            # Snapshot state BEFORE storing the result; on a successful
            # restore_undo execution resumes here and we set 'store' to 2
            # (the Inform "undo restored" sentinel).  A fresh save stores 1.
            self.undo_snapshot = (bytes(self.mem), list(self.stack),
                                  [(f.return_pc, list(f.locals), f.stack_base,
                                    f.store_var, f.discard, f.num_args)
                                   for f in self.frames], self.pc, store)
            self.undo_seq += 1
            self.write_var(store, 1)
        elif op == 10:  # restore_undo
            store = self.read_store()
            if self.undo_snapshot is None:
                # No undo available: store 0 (failure); execution continues here.
                self.write_var(store, 0)
            else:
                mem, stack, frames, pc, save_store = self.undo_snapshot
                self.mem = bytearray(mem)
                self.stack = list(stack)
                self.frames = [Frame(*f) for f in frames]
                self.current_frame = self.frames[-1]
                self.pc = pc
                # Make the matching save_undo "return" 2 = restored sentinel.
                # Execution resumes there; the restore_undo's own store is unused.
                self.write_var(save_store, 2)
        elif op == 11:  # print_unicode
            self.emit(chr(ops[0] & 0xFFFF) if ops[0] < 0x10000 else "?")
        elif op == 12:  # check_unicode
            store = self.read_store()
            self.write_var(store, 3)  # can print & input
        else:
            # unknown ext: no-op (avoid crashing on obscure opcodes)
            pass


def main():
    ap = argparse.ArgumentParser(description="Headless Z-machine v5 tester")
    here = os.path.dirname(os.path.abspath(__file__))
    default_story = os.path.join(here, "adventure_lovecraft.z5")
    ap.add_argument("--story", default=default_story)
    ap.add_argument("--script", help="file of commands, one per line")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--mark", action="store_true",
                    help="print ###CMD: markers before each command")
    ap.add_argument("commands", nargs="*", help="inline commands")
    args = ap.parse_args()

    commands = []
    if args.script:
        with open(args.script, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n").rstrip("\r")
                if line.startswith("#") or line.strip() == "":
                    continue
                commands.append(line)
    commands.extend(args.commands)

    if not commands:
        # interactive: read from stdin
        print("Reading commands from stdin (Ctrl-D/Ctrl-Z to end):",
              file=sys.stderr)
        for line in sys.stdin:
            commands.append(line.rstrip("\n").rstrip("\r"))

    z = ZMachine(args.story, commands, mark=args.mark, seed=args.seed)
    output = z.run()
    sys.stdout.write(output)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
