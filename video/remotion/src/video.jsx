import {useLayoutEffect, useRef} from 'react';
import {Audio} from '@remotion/media';
import {AbsoluteFill, staticFile, useCurrentFrame} from 'remotion';
import timings from '../../timings.json';
import {renderAtTime} from './scene';
import {FPS} from './config';

export const MinMuseVideo = () => {
  const frame = useCurrentFrame();
  const canvas = useRef(null);
  useLayoutEffect(() => {
    if (canvas.current) renderAtTime(canvas.current, frame / FPS, timings.cues, timings.duration);
  }, [frame]);
  return (
    <AbsoluteFill style={{backgroundColor: '#090d14'}}>
      <canvas ref={canvas} width={720} height={1280} style={{width: 720, height: 1280}} />
      <Audio src={staticFile('voice.wav')} />
    </AbsoluteFill>
  );
};
