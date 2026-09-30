import {Composition} from 'remotion';
import timings from '../../timings.json';
import {MinMuseVideo} from './video';
import {FPS} from './config';

export const Root = () => (
  <Composition
    id="MinMuse"
    component={MinMuseVideo}
    durationInFrames={Math.ceil(timings.duration * FPS)}
    fps={FPS}
    width={720}
    height={1280}
  />
);
