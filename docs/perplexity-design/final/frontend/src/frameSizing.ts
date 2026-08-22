import { FrameDimensions } from './types';

export const DEFAULT_FRAME: FrameDimensions = {
  width: 1.0,
  height: 1.0,
  depth: 1.0,
};

export function validateFrame(f: FrameDimensions): string | null {
  if (f.width  < 0.3 || f.width  > 10) return 'Width must be 0.3-10 m';
  if (f.height < 0.3 || f.height > 5)  return 'Height must be 0.3-5 m';
  if (f.depth  < 0.3 || f.depth  > 10) return 'Depth must be 0.3-10 m';
  return null;
}
