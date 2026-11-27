// news-image-20261126 (rebuild): copies the pre-rendered front page to /output/entry.png.
// The image itself (entry.png, in this repository) was rendered by render.py
// with real serif fonts (Liberation Serif); this program only copies its exact
// bytes, so both runs write identical output.
import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Resolve the image next to this file, not from the working directory,
// so the copy works wherever the harness runs it from.
const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, 'entry.png');
const out = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(out, { recursive: true });
copyFileSync(src, join(out, 'entry.png'));

// Guard: the bounty allows at most 1 MiB.
const bytes = statSync(join(out, 'entry.png')).size;
if (bytes > 1048576) throw new Error('entry.png exceeds 1 MiB: ' + bytes);
