"""Reuse the existing scene artwork in the deterministic Remotion renderer."""
from pathlib import Path

here = Path(__file__).resolve().parent
source = (here.parent / "editor.html").read_text(encoding="utf-8")
start = source.index("function rounded(")
end = source.index("function draw(", start)
helpers = source[start:end]
tail = r'''
const pad = n => String(Math.floor(n)).padStart(2, '0');
const fmt = t => `${pad(t / 60)}:${pad(t % 60)}`;

export function renderAtTime(canvas, t, cues, duration) {
  ctx = canvas.getContext('2d');
  const cue = cues.find(c => t >= c.start && t < c.end)
    || [...cues].reverse().find(c => c.start <= t)
    || cues[0];
  scene(cue?.scene || 'hook', t);
  const lines = wrap(cue?.text || '', 600, 'bold 34px "Microsoft YaHei UI",sans-serif');
  const boxY = 870, boxH = 310;
  rounded(36, boxY, 648, boxH, 20, 'rgba(7,12,18,.91)', '#34414c');
  const startY = boxY + (boxH - (lines.length * 52)) / 2 + 36;
  lines.forEach((line, i) => text(line, 360, startY + i * 52, 34, '#fff', 800, 'center'));
  ctx.fillStyle = '#293643';
  ctx.fillRect(48, 1220, 624, 4);
  ctx.fillStyle = '#6dd8c1';
  ctx.fillRect(48, 1220, 624 * Math.min(1, t / duration), 4);
  text(fmt(t) + ' / ' + fmt(duration), 672, 1190, 15, '#afbbc7', 500, 'right');
}
'''
target = here / "src" / "scene.js"
target.write_text("let ctx;\n" + helpers + tail, encoding="utf-8")
print(f"Updated {target}")
