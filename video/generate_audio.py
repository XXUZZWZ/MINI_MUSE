import ast, os, sys
from pathlib import Path
import onnxruntime as ort
ort.preload_dlls(directory='')
video=Path(__file__).resolve().parent
repo=Path(os.environ.get('MOSS_TTS_REPO',str(video.parent.parent/'moss-tts-nano'))).resolve()
sys.path.insert(0,str(repo))
from onnx_tts_runtime import OnnxTtsRuntime
module=ast.parse((video/'assemble_audio.py').read_text(encoding='utf-8-sig'))
lines=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LINES' for t in n.targets))
outdir=video/'voice_parts';outdir.mkdir(parents=True,exist_ok=True)
runtime=OnnxTtsRuntime(model_dir=repo/'models',thread_count=4,max_new_frames=450,execution_provider='cuda')
for i,(line,_) in enumerate(lines,1):
 out=outdir/f'{i:02d}.wav'
 result=runtime.synthesize(text=line,voice='Zhiming',prompt_audio_path=None,output_audio_path=out,sample_mode='fixed',do_sample=True,streaming=True,max_new_frames=450,voice_clone_max_text_tokens=75,enable_wetext=False,enable_normalize_tts_text=True,seed=20260930+i)
 print(f'{i}/{len(lines)} frames={result["audio_token_ids"].shape[0]} bytes={out.stat().st_size}',flush=True)
