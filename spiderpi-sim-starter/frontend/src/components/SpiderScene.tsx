import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Html, Environment, Sky } from "@react-three/drei";
import { SpiderState } from "../types";
import * as THREE from "three";

function circlePoints(
  radius: number,
  y: number,
  center: [number, number, number],
  segments = 72,
) {
  return Array.from({ length: segments + 1 }, (_, index) => {
    const theta = (index / segments) * Math.PI * 2;
    return [
      center[0] + Math.cos(theta) * radius,
      y,
      center[2] + Math.sin(theta) * radius,
    ] as [number, number, number];
  });
}

function Trail({ points }: { points: { x: number; y: number; z: number }[] }) {
  if (!points.length) return null;
  const pts = points.map((p) => [p.x, p.z, p.y] as [number, number, number]);
  return <Line points={pts} color="#22c55e" lineWidth={1} dashed />;
}

function CornerTower({ position }: { position: [number, number, number] }) {
  const [x, y, z] = position;
  return (
    <group position={[x, 0, z]}>
      <mesh position={[0, 0.02, 0]} receiveShadow>
        <cylinderGeometry args={[0.12, 0.16, 0.04, 16]} />
        <meshStandardMaterial color="#3f4c64" metalness={0.25} roughness={0.85} />
      </mesh>
      <mesh position={[0, y / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.035, 0.05, y, 12]} />
        <meshStandardMaterial color="#64748b" metalness={0.45} roughness={0.4} />
      </mesh>
      <mesh position={[0, y + 0.06, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.2, 0.12, 0.2]} />
        <meshStandardMaterial color="#7dd3fc" emissive="#164e63" emissiveIntensity={0.45} />
      </mesh>
      <mesh position={[0, y + 0.13, 0]} castShadow>
        <boxGeometry args={[0.32, 0.03, 0.12]} />
        <meshStandardMaterial color="#cbd5e1" metalness={0.2} roughness={0.55} />
      </mesh>
    </group>
  );
}

function StadiumGround({ center }: { center: [number, number, number] }) {
  const boundary = circlePoints(2.28, 0.02, center, 96);
  const innerRing = circlePoints(1.48, 0.02, center, 96);
  const pitchGuide = circlePoints(0.58, 0.018, center, 96);

  return (
    <group>
      <mesh position={[center[0], -0.08, center[2]]} receiveShadow>
        <cylinderGeometry args={[4.8, 5.2, 0.18, 80]} />
        <meshStandardMaterial color="#334155" roughness={0.92} />
      </mesh>

      <mesh position={[center[0], 0, center[2]]} receiveShadow>
        <cylinderGeometry args={[4.2, 4.2, 0.06, 96]} />
        <meshStandardMaterial color="#437057" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.012, center[2]]} receiveShadow>
        <circleGeometry args={[2.42, 96]} />
        <meshStandardMaterial color="#51a653" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.018, center[2]]} receiveShadow>
        <circleGeometry args={[1.08, 96]} />
        <meshStandardMaterial color="#63b95d" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.024, center[2]]} receiveShadow>
        <planeGeometry args={[0.34, 1.1]} />
        <meshStandardMaterial color="#cdb994" roughness={0.98} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.026, center[2] - 0.32]} receiveShadow>
        <planeGeometry args={[0.22, 0.08]} />
        <meshStandardMaterial color="#efe4c5" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.026, center[2] + 0.32]} receiveShadow>
        <planeGeometry args={[0.22, 0.08]} />
        <meshStandardMaterial color="#efe4c5" roughness={1} />
      </mesh>

      <Line points={boundary} color="#f8fafc" lineWidth={1.3} />
      <Line points={innerRing} color="#d9f99d" lineWidth={0.9} dashed dashSize={0.08} gapSize={0.06} />
      <Line points={pitchGuide} color="#86efac" lineWidth={0.7} dashed dashSize={0.05} gapSize={0.05} />

      <mesh position={[center[0], 0.55, center[2]]} receiveShadow>
        <cylinderGeometry args={[3.55, 4.15, 1.1, 72, 1, true]} />
        <meshStandardMaterial
          color="#cbd5e1"
          metalness={0.08}
          roughness={0.82}
          side={THREE.DoubleSide}
        />
      </mesh>

      <mesh position={[center[0], 0.98, center[2]]} receiveShadow>
        <cylinderGeometry args={[3.85, 4.45, 0.28, 72, 1, true]} />
        <meshStandardMaterial
          color="#94a3b8"
          metalness={0.06}
          roughness={0.88}
          side={THREE.DoubleSide}
        />
      </mesh>

      <mesh position={[center[0], 0.94, center[2]]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[4.02, 0.06, 16, 96]} />
        <meshStandardMaterial color="#e2e8f0" metalness={0.12} roughness={0.62} />
      </mesh>

      <mesh position={[center[0], 0.45, center[2]]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3.52, 0.08, 16, 96]} />
        <meshStandardMaterial color="#64748b" metalness={0.12} roughness={0.58} />
      </mesh>
    </group>
  );
}

export function SpiderScene({ state }: { state: SpiderState | null }) {
  if (!state) return <div className="sceneFallback">Loading 3D scene...</div>;
  const anchors = Object.entries(state.anchors)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, [x, y, z]]) => [x, z, y] as [number, number, number]);
  const centerX = anchors.reduce((sum, anchor) => sum + anchor[0], 0) / anchors.length;
  const centerZ = anchors.reduce((sum, anchor) => sum + anchor[2], 0) / anchors.length;
  const center: [number, number, number] = [centerX, 0, centerZ];
  const P: [number, number, number] = [state.position.x, state.position.z, state.position.y];

  return (
    <div className="sceneWrap">
      <Canvas shadows camera={{ position: [4.9, 2.6, 4.8], fov: 40 }}>
        <color attach="background" args={["#b7d8ff"]} />
        <fog attach="fog" args={["#b7d8ff", 8, 20]} />
        <ambientLight intensity={1} />
        <hemisphereLight args={["#f0f9ff", "#365314", 1.15]} />
        <directionalLight
          position={[5, 6, 2]}
          intensity={2.1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <Sky sunPosition={[6, 3, 2]} turbidity={7} rayleigh={2.2} />
        <StadiumGround center={center} />
        <Line points={[...anchors, anchors[0]]} color="#94a3b8" lineWidth={1.6} />
        {anchors.map((anchor, index) => (
          <Line key={`cable-${index}`} points={[anchor, P]} color="#ef4444" lineWidth={2.1} />
        ))}
        <Trail points={state.trail} />
        {anchors.map((anchor, index) => (
          <CornerTower key={`tower-${index}`} position={anchor} />
        ))}
        <mesh position={P} castShadow>
          <sphereGeometry args={[0.06, 24, 24]} />
          <meshStandardMaterial color={state.estop ? "#dc2626" : "#f59e0b"} />
        </mesh>
        <mesh position={[P[0], P[1] - 0.05, P[2]]} castShadow receiveShadow>
          <boxGeometry args={[0.22, 0.04, 0.12]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.15} roughness={0.62} />
        </mesh>
        <Html position={[P[0], P[1] + 0.18, P[2]]} center transform sprite distanceFactor={6}>
          <div className="cameraBadge">
            <img
              className="cameraPreview"
              src="/spidercam-reference.png"
              alt="Spidercam camera"
            />
          </div>
        </Html>
        <OrbitControls
          makeDefault
          target={new THREE.Vector3(center[0], 0.65, center[2])}
          minPolarAngle={0.45}
          maxPolarAngle={1.35}
          minDistance={3.6}
          maxDistance={8.5}
        />
        <Environment preset="park" />
      </Canvas>
    </div>
  );
}
