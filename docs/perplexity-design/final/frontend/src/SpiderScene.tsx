import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Grid } from '@react-three/drei';
import * as THREE from 'three';
import { TelemetryState } from './types';
import { getAnchors } from './kinematics';
import { DEFAULT_FRAME } from './frameSizing';

interface Props {
  telemetry: TelemetryState | null;
}

function SpiderMesh({ pos }: { pos: [number, number, number] }) {
  return (
    <mesh position={pos}>
      <sphereGeometry args={[0.04, 16, 16]} />
      <meshStandardMaterial color="#58a6ff" emissive="#1a3a5c" />
    </mesh>
  );
}

function CableLines({ pos }: { pos: [number, number, number] }) {
  const anchors = getAnchors(DEFAULT_FRAME);
  return (
    <>
      {anchors.map((a, i) => (
        <Line
          key={i}
          points={[
            new THREE.Vector3(a.x, a.y, a.z),
            new THREE.Vector3(...pos),
          ]}
          color="#4a9eff"
          lineWidth={1.5}
        />
      ))}
    </>
  );
}

function FrameBox() {
  const { width, height, depth } = DEFAULT_FRAME;
  const corners: [number, number, number][] = [
    [0, height, 0], [width, height, 0],
    [width, height, depth], [0, height, depth],
    [0, 0, 0], [width, 0, 0],
    [width, 0, depth], [0, 0, depth],
  ];
  const edges: number[][] = [
    [0,1],[1,2],[2,3],[3,0],
    [4,5],[5,6],[6,7],[7,4],
    [0,4],[1,5],[2,6],[3,7],
  ];
  return (
    <>
      {edges.map(([a, b], i) => (
        <Line
          key={i}
          points={[new THREE.Vector3(...corners[a]), new THREE.Vector3(...corners[b])]}
          color="#30363d"
          lineWidth={1}
        />
      ))}
      {corners.slice(0, 4).map((c, i) => (
        <mesh key={i} position={c}>
          <sphereGeometry args={[0.02, 8, 8]} />
          <meshStandardMaterial color="#f85149" />
        </mesh>
      ))}
    </>
  );
}

export default function SpiderScene({ telemetry }: Props) {
  const pos: [number, number, number] = telemetry
    ? [telemetry.position[0], telemetry.position[1], telemetry.position[2]]
    : [DEFAULT_FRAME.width/2, DEFAULT_FRAME.height*0.8, DEFAULT_FRAME.depth/2];

  return (
    <Canvas camera={{ position: [2, 1.5, 2], fov: 45 }} style={{ background: '#0d1117' }}>
      <ambientLight intensity={0.6} />
      <pointLight position={[2, 3, 2]} intensity={1} />
      <FrameBox />
      <CableLines pos={pos} />
      <SpiderMesh pos={pos} />
      <Grid
        args={[4, 4]}
        position={[0.5, 0, 0.5]}
        cellColor="#21262d"
        sectionColor="#30363d"
        cellSize={0.1}
        sectionSize={0.5}
      />
      <OrbitControls makeDefault />
    </Canvas>
  );
}
