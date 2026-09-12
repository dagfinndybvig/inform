# Self-Hosted Parchment on GitHub Pages — a Serving Tool

This repository serves the compiled game directly from GitHub Pages using a
self-hosted copy of [Parchment](https://github.com/curiousdannii/parchment),
the JavaScript Z-machine interpreter. No external service (iplayif.com) is
involved. The serving setup is three files plus the CI workflow that keeps
the compiled story file in sync with the source.

## Files

```
inform/
├── parchment.html            # Parchment single-file build (2026.8.23)
├── index.html                # Landing page, redirects to parchment.html
├── adventure_lovecraft.z5     # Compiled game (Z-machine v5)
└── .github/workflows/compile-inform.yml  # CI: compile .inf → .z5, commit
```

## How it works

```
push .inf to main
  → GitHub Actions triggers
    → builds Inform 6.44 compiler from source
    → compiles adventure_lovecraft.inf → adventure_lovecraft.z5
    → commits .z5 back to main
      → GitHub Pages redeploys
        → index.html redirects to parchment.html
          → Parchment loads adventure_lovecraft.z5 (same domain)
```

Both `parchment.html` and `adventure_lovecraft.z5` are served from the same
GitHub Pages domain (`dagfinndybvig.github.io`), so there are no CORS issues.
Parchment's proxy is disabled — the story file is fetched directly.

### `parchment.html`

The Parchment single-file build from
<https://github.com/curiousdannii/parchment/releases>. Everything (jQuery,
WebGlkOte, Bocfel interpreter, etc.) is inlined into one ~4 MB HTML file.

The `parchment_options` block at the top is configured for self-hosting:

```html
<script>parchment_options = {
  "single_file": 1,
  "story": { "url": "./adventure_lovecraft.z5", "title": "The Goddess in the Cellar" },
  "use_proxy": 0
}</script>
```

| Option | Value | Why |
|--------|-------|-----|
| `single_file` | `1` | Parchment is a single inlined HTML file, no external JS/CSS assets |
| `story` | `{ url, title }` object | Tells Parchment which story file to load. Must be an object with `url` and `title` — see "Pitfalls" below |
| `use_proxy` | `0` | Disables the iplayif.com proxy. The story file is on the same domain, so direct fetch works |

The story `url` is relative (`./adventure_lovecraft.z5`), which resolves to
the same GitHub Pages directory as `parchment.html`.

### `index.html`

A minimal landing page that immediately redirects to `parchment.html`:

```html
<script>
    window.location.href = 'parchment.html?story=adventure_lovecraft.z5';
</script>
```

Includes a visible "Click here to play" link as a fallback for users with
JavaScript disabled.

### CI workflow (`.github/workflows/compile-inform.yml`)

Triggers on push to `*.inf` or the workflow file itself, on `main`. Three
steps:

1. **Build the Inform 6 compiler from source** — clones
   `DavidKinder/Inform6` and compiles with `cc -O2 --std=c11 -DUNIX`. This
   ensures the CI uses the same compiler version as the bundled Windows
   binary (`inform6_compiler/inform6.exe`), rather than the stale Ubuntu
   `inform` apt package (v6.31, Library 6/11).

2. **Compile the game** — creates case-sensitivity symlinks for the library
   headers (see "Pitfalls" below), then compiles with the repo's bundled
   library via `+inform6lib/inform6lib-master`.

3. **Commit and push the `.z5`** — if the compiled file changed, the bot
   commits it as `github-actions[bot]` with `[skip ci]` to avoid a loop.

## Updating Parchment

To upgrade Parchment to a newer release:

```bash
# Download the latest single-file build
curl -sL "https://github.com/curiousdannii/parchment/releases/latest/download/parchment-single-file-$(date +%Y-%m-%d).zip" -o /tmp/parchment.zip
# (Or find the exact filename from the release assets on the releases page.)

# Extract and copy
mkdir -p /tmp/parchment-extracted && cd /tmp/parchment-extracted
unzip -o /tmp/parchment.zip
cp parchment.html /path/to/inform/parchment.html
```

Then re-apply the `parchment_options` block at the top of the file:

```html
<script>parchment_options = {
  "single_file": 1,
  "story": { "url": "./adventure_lovecraft.z5", "title": "The Goddess in the Cellar" },
  "use_proxy": 0
}</script>
```

Commit and push. GitHub Pages redeploys within ~1 minute.

## Pitfalls

### CI compiler version mismatch

The Ubuntu `inform` apt package is Inform v6.31 with Library 6/11 — much
older than the repo's bundled Inform 6.44 with Library v6.12.2. Using the
apt package produces a different binary (78,848 bytes vs 88,576 bytes) with
a different library version embedded in the story file header. The
workflow builds the compiler from source to match the bundled version.

### Case-sensitive library filenames

The Inform 6 library files are lowercase: `parser.h`, `verblib.h`,
`grammar.h`, `english.h`. The game source uses mixed-case includes:
`Include "Parser"`, `Include "VerbLib"`, `Include "Grammar"`. The compiler's
default language is `"English"` (capital E), which triggers an include of
`english.h` — but as `English.h`.

On Windows (case-insensitive) this works. On Linux (case-sensitive, as in
CI) it fails. The workflow creates symlinks before compiling:

```bash
cd inform6lib/inform6lib-master
ln -s parser.h Parser.h
ln -s verblib.h VerbLib.h
ln -s grammar.h Grammar.h
ln -s english.h English.h
```

### Parchment `story` option must be an object

Parchment's `preload()` method extracts the title from the story URL using
a regex:

```js
title: e.title ?? /([/=])([^/=]+)$/.exec(e.path || e.url)[2]
```

If the story is a bare filename string like `"adventure_lovecraft.z5"`, the
regex finds no `/` or `=` in the string, `.exec()` returns `null`, and
`null[2]` throws:

```
TypeError: Cannot read properties of null (reading '2')
```

Fix: pass the story as an object with an explicit `title`, so the regex
fallback is never reached:

```js
"story": { "url": "./adventure_lovecraft.z5", "title": "The Goddess in the Cellar" }
```

The `url` should contain a `/` (e.g. `./`) even if the title is provided, so
that `new URL(url, document.URL)` resolves correctly.

### Parchment proxy must be disabled

Parchment's defaults include `use_proxy: 1` and
`proxy_url: "https://iplayif.com/proxy/"`. Even when self-hosting, Parchment
routes story file fetches through the iplayif.com proxy unless the domain
matches `direct_domains` (which is limited to ifarchive.org). Since we serve
both the HTML and the `.z5` from the same GitHub Pages domain, set
`"use_proxy": 0` to fetch directly.

### iplayif.com server-side cache

The previous setup redirected to
`https://iplayif.com/?story=https://raw.githubusercontent.com/.../adventure_lovecraft.z5`.
iplayif.com caches story files server-side with an uncontrolled TTL. After
recompiling, the cached old version could persist for hours. Self-hosting
eliminates this — GitHub Pages serves the file directly with a 5-minute
`Cache-Control: max-age=300`, and a push always replaces the file
immediately.
