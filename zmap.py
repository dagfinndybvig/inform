#!/usr/bin/env python3
"""
zmap.py - Generate a map from an Inform 6 source file.

Parses room objects and their directional properties (n_to, s_to, e_to, w_to,
u_to, d_to, in_to, out_to) and emits a Graphviz DOT graph. Dynamic connections
(set via before routines or Initialise, like the clock teleport) are not
detected; see the manual edge option below.

Usage:
    python zmap.py adventure_lovecraft.inf              # prints DOT to stdout
    python zmap.py adventure_lovecraft.inf -o map.dot    # writes DOT file
    python zmap.py adventure_lovecraft.inf --png map.png # renders via dot
    python zmap.py adventure_lovecraft.inf --svg map.svg # renders via dot

Manual edges (for dynamic connections the parser can't see):
    python zmap.py adventure.inf --edge "Cellar:Alien World:enter clock:dashed,blue"
    Format: From:To:Label:style (style is comma-sep: dashed,blue,etc.)

Requires Graphviz 'dot' only if --png or --svg is used.
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict

DIRECTIONS = [
    ("n_to", "n"),
    ("s_to", "s"),
    ("e_to", "e"),
    ("w_to", "w"),
    ("u_to", "u"),
    ("d_to", "d"),
    ("in_to", "in"),
    ("out_to", "out"),
]

DIR_LABEL = {
    "n": "N", "s": "S", "e": "E", "w": "W",
    "u": "U", "d": "D", "in": "In", "out": "Out",
}

DIR_RANKDIR = {
    ("n", "s"): "TB",
    ("e", "w"): "LR",
}


def parse_inf(source):
    """Parse an .inf file, returning (rooms, edges).

    rooms: dict of internal_name -> {label, directions: {dir_prop: target_name}}
    edges: list of (from_label, to_label, label, style)
    """
    text = source.read()

    # Match Object declarations. Object Name "Label" or Object -> Name "Label"
    # We need to track the object's internal name and its short name (label).
    # Properties like n_to, s_to etc. follow.
    obj_pattern = re.compile(
        r'Object\s+(?:->\s+)?(\w+)\s+"([^"]*)"',
        re.MULTILINE,
    )

    # Find all object declarations with their positions
    objects = {}  # internal_name -> label
    for m in obj_pattern.finditer(text):
        internal = m.group(1)
        label = m.group(2)
        objects[internal] = label

    # Now find room objects (those that have directional properties or light/dark)
    # We'll scan each Object block for directional properties.
    # An Object block starts at "Object ... " and ends at the next "Object" or
    # at the next top-level "Include" or end of file.

    # Split into blocks by Object declarations
    lines = text.split("\n")
    blocks = []
    current_block_lines = []
    current_block_header = None
    brace_depth = 0
    in_routine = False

    for line in lines:
        stripped = line.strip()
        if re.match(r'^Object\s+', stripped) and not in_routine:
            if current_block_header is not None:
                blocks.append((current_block_header, current_block_lines))
            current_block_header = stripped
            current_block_lines = []
            brace_depth = 0
            in_routine = False
        elif current_block_header is not None:
            # Track routines (bracketed code blocks) to avoid false matches
            opens = stripped.count("[")
            closes = stripped.count("]")
            # Simple heuristic: if we see [; or [ routine, we're in a routine
            if opens > closes and "[" in stripped:
                in_routine = True
                brace_depth += opens - closes
            elif in_routine:
                brace_depth += opens - closes
                if brace_depth <= 0:
                    in_routine = False
                    brace_depth = 0

            if not in_routine:
                current_block_lines.append(stripped)

    if current_block_header is not None:
        blocks.append((current_block_header, current_block_lines))

    # Parse each block for room properties
    rooms = {}
    edges = []

    for header, body_lines in blocks:
        m = re.match(r'Object\s+(?:->\s+)?(\w+)\s+"([^"]*)"', header)
        if not m:
            continue
        internal = m.group(1)
        label = m.group(2)

        # A room is an object with at least one directional property, OR an
        # object with has light/has scored but no item-specific properties
        # (name '...', initial, etc.). This catches dead-end rooms like
        # AlienWorld that have no exits.
        body = "\n".join(body_lines)
        has_direction = any(
            re.search(rf'\b{prop}\s+(\w+)', body) for prop, _ in DIRECTIONS
        )
        has_room_attr = bool(re.search(r'\bhas\b.*\b(light|scored)\b', body))
        has_item_prop = bool(re.search(r"\bname\s+'", body)) or "initial" in body

        if not has_direction:
            if not (has_room_attr and not has_item_prop):
                continue

        room = {"label": label, "directions": {}}
        for prop, short in DIRECTIONS:
            # Match: prop Target, or prop Target; at end of line
            pm = re.search(rf'\b{prop}\s+(\w+)', body)
            if pm:
                target_internal = pm.group(1)
                target_label = objects.get(target_internal, target_internal)
                room["directions"][prop] = target_label
                edges.append((label, target_label, DIR_LABEL[short], "solid"))

        rooms[internal] = room

    return rooms, edges


def parse_manual_edges(edge_args):
    """Parse --edge arguments: From:To:Label:style"""
    edges = []
    for e in edge_args or []:
        parts = e.split(":")
        if len(parts) < 3:
            print(f"Warning: ignoring bad edge '{e}' (need From:To:Label[:style])", file=sys.stderr)
            continue
        frm, to, label = parts[0], parts[1], parts[2]
        style = parts[3] if len(parts) > 3 else "dashed"
        edges.append((frm, to, label, style))
    return edges


def generate_dot(rooms, edges):
    lines = []
    lines.append("digraph game_map {")
    lines.append("    rankdir=TB;")
    lines.append("    node [shape=box, style=rounded, fontname=\"Helvetica\"];")
    lines.append("    edge [fontname=\"Helvetica\", fontsize=10];")
    lines.append("")

    # Node definitions
    for internal, room in rooms.items():
        label = room["label"]
        lines.append(f'    {dot_id(internal)} [label="{escape(label)}"];')

    lines.append("")

    # Edges
    # Deduplicate: if A->B and B->A with opposite directions, draw as single edge with both labels
    # Build a map of (frm, to) -> list of (label, style)
    edge_map = defaultdict(list)
    for frm, to, label, style in edges:
        # Use internal names for nodes, so we need to find internal by label
        # Actually edges store labels; convert to internal names
        frm_int = label_to_internal(rooms, frm) or frm
        to_int = label_to_internal(rooms, to) or to
        edge_map[(frm_int, to_int)].append((label, style))

    # Find bidirectional pairs
    drawn = set()
    for (frm, to), labels in list(edge_map.items()):
        if (frm, to) in drawn:
            continue
        rev = (to, frm)
        if rev in edge_map and rev not in drawn:
            # Bidirectional
            combined_label = ", ".join(l for l, s in labels)
            rev_labels = edge_map[rev]
            combined_label += " / " + ", ".join(l for l, s in rev_labels)
            # Use the style from the first edge
            style = labels[0][1]
            lines.append(f'    {dot_id(frm)} -> {dot_id(to)} [label="{escape(combined_label)}", dir=both, style={style}];')
            drawn.add((frm, to))
            drawn.add(rev)
        else:
            for label, style in labels:
                lines.append(f'    {dot_id(frm)} -> {dot_id(to)} [label="{escape(label)}", style={style}];')
            drawn.add((frm, to))

    lines.append("}")
    return "\n".join(lines) + "\n"


def label_to_internal(rooms, label):
    for internal, room in rooms.items():
        if room["label"] == label:
            return internal
    return None


def dot_id(name):
    # DOT IDs can be bare if they match [a-zA-Z_][a-zA-Z0-9_]*
    if re.match(r'^[a-zA-Z_]\w*$', name):
        return name
    return f'"{name}"'


def escape(s):
    return s.replace('"', '\\"')


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Graphviz DOT map from an Inform 6 source file."
    )
    parser.add_argument("source", type=argparse.FileType("r"), help="Inform 6 .inf source file")
    parser.add_argument("-o", "--output", help="Write DOT to this file (default: stdout)")
    parser.add_argument("--png", metavar="FILE", help="Render PNG via Graphviz dot")
    parser.add_argument("--svg", metavar="FILE", help="Render SVG via Graphviz dot")
    parser.add_argument("--edge", action="append", help="Manual edge: From:To:Label[:style]")
    args = parser.parse_args()

    rooms, edges = parse_inf(args.source)
    args.source.close()

    if not rooms:
        print("No rooms found in source.", file=sys.stderr)
        sys.exit(1)

    manual_edges = parse_manual_edges(args.edge)
    edges.extend(manual_edges)

    dot = generate_dot(rooms, edges)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(dot)
        print(f"DOT written to {args.output}", file=sys.stderr)
    else:
        print(dot)

    if args.png or args.svg:
        if args.png:
            out_file = args.png
            out_format = "png"
        else:
            out_file = args.svg
            out_format = "svg"

        # Write DOT to a temp file for dot to consume
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False, encoding="utf-8") as tmp:
            tmp.write(dot)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                ["dot", f"-T{out_format}", "-o", out_file, tmp_path],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f"dot failed: {result.stderr}", file=sys.stderr)
                sys.exit(1)
            print(f"{out_format.upper()} written to {out_file}", file=sys.stderr)
        except FileNotFoundError:
            print("Error: 'dot' (Graphviz) not found. Install Graphviz to render images.", file=sys.stderr)
            sys.exit(1)
        finally:
            import os
            os.unlink(tmp_path)


if __name__ == "__main__":
    main()
