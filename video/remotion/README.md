# Remotion edition

This edition renders the existing 720×1280 scene artwork and subtitles at exact frame times. It uses `../timings.json` and `../voice.wav` from the local audio pipeline.

```powershell
cd video/remotion
pnpm install
.\render.ps1
```

The final output is `../MinMuse_最小邮件Agent_Remotion.mp4`. The scenes are mostly static, so Remotion renders at 10 fps to keep local rendering practical, then FFmpeg packages a 30 fps MP4 by duplicating frames. You need FFmpeg on PATH, or the existing local MOSS TTS environment with `imageio-ffmpeg` installed. `sync_scene.py` copies the scene artwork from `../editor.html` into the Remotion source before rendering. The voice file is copied into `public/` locally and is not committed.
