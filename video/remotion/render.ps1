$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
python .\sync_scene.py
New-Item -ItemType Directory -Path .\public -Force | Out-Null
Copy-Item -LiteralPath ..\voice.wav -Destination .\public\voice.wav -Force
$renderArgs = @('exec', 'remotion', 'render', 'src\index.jsx', 'MinMuse', '..\MinMuse_最小邮件Agent_Remotion_10fps.mp4', '--codec', 'h264', '--crf', '24', '--x264-preset', 'veryfast', '--concurrency', '4')
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (Test-Path -LiteralPath $edge) { $renderArgs += @('--browser-executable', $edge) }
pnpm @renderArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$ffmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
if (-not $ffmpeg) {
  $ttsRepo = if ($env:MOSS_TTS_REPO) { $env:MOSS_TTS_REPO } else { Join-Path $here '..\..\..\moss-tts-nano' }
  $ttsPython = Join-Path $ttsRepo '.venv\Scripts\python.exe'
  if (Test-Path -LiteralPath $ttsPython) {
    $ffmpeg = & $ttsPython -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'
  }
}
if (-not $ffmpeg) { throw 'FFmpeg is needed to package the final 30 fps MP4.' }
& $ffmpeg -y -i '..\MinMuse_最小邮件Agent_Remotion_10fps.mp4' -vf fps=30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a copy -movflags +faststart '..\MinMuse_最小邮件Agent_Remotion.mp4' -loglevel error
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
