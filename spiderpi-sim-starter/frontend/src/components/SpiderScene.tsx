import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls, Line, Html, Environment, Sky } from "@react-three/drei";
import { SpiderState } from "../types";
import * as THREE from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";

type LightingMode = "day" | "night";
type SceneMode = "engineering" | "stadium";
type ViewPreset = "side" | "top" | "front";
const SIDE_VIEW_OFFSET = new THREE.Vector3(3.9, 1.95, 3.8);
const TOP_VIEW_OFFSET = new THREE.Vector3(0, 5.4, 0.45);
const FRONT_VIEW_OFFSET = new THREE.Vector3(0, 1.25, 5.3);

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

function WicketSet({ position }: { position: [number, number, number] }) {
  const stumpOffsets = [-0.028, 0, 0.028];
  return (
    <group position={position}>
      {stumpOffsets.map((offset, index) => (
        <mesh key={`stump-${index}`} position={[offset, 0.045, 0]} castShadow>
          <cylinderGeometry args={[0.004, 0.004, 0.09, 10]} />
          <meshStandardMaterial color="#fff7ed" roughness={0.9} />
        </mesh>
      ))}
      <mesh position={[-0.014, 0.092, 0]} castShadow>
        <boxGeometry args={[0.022, 0.006, 0.006]} />
        <meshStandardMaterial color="#f8fafc" roughness={0.9} />
      </mesh>
      <mesh position={[0.014, 0.092, 0]} castShadow>
        <boxGeometry args={[0.022, 0.006, 0.006]} />
        <meshStandardMaterial color="#f8fafc" roughness={0.9} />
      </mesh>
    </group>
  );
}

function SeatRows({ center, isNight }: { center: [number, number, number]; isNight: boolean }) {
  const rows = [
    { radius: 3.52, y: 0.34, color: isNight ? "#1d4ed8" : "#1e40af", seats: 56 },
    { radius: 3.76, y: 0.58, color: isNight ? "#dc2626" : "#ef4444", seats: 64 },
    { radius: 4.02, y: 0.86, color: isNight ? "#f59e0b" : "#f59e0b", seats: 72 },
  ];

  return (
    <group>
      {rows.map((row) =>
        Array.from({ length: row.seats }, (_, index) => {
          const theta = (index / row.seats) * Math.PI * 2;
          const x = center[0] + Math.cos(theta) * row.radius;
          const z = center[2] + Math.sin(theta) * row.radius;
          const inwardYaw = Math.atan2(center[0] - x, center[2] - z);
          return (
            <group key={`${row.radius}-${index}`} position={[x, row.y, z]} rotation={[0, inwardYaw, 0]}>
              <mesh receiveShadow>
                <boxGeometry args={[0.12, 0.03, 0.08]} />
                <meshStandardMaterial color={row.color} roughness={0.72} />
              </mesh>
              <mesh position={[0, 0.04, -0.026]} receiveShadow>
                <boxGeometry args={[0.12, 0.08, 0.02]} />
                <meshStandardMaterial color={row.color} roughness={0.72} />
              </mesh>
            </group>
          );
        }),
      )}
    </group>
  );
}

function CornerTower({
  position,
  lightingMode,
  structuralScale = 1,
}: {
  position: [number, number, number];
  lightingMode: LightingMode;
  structuralScale?: number;
}) {
  const [x, y, z] = position;
  const isNight = lightingMode === "night";
  const legRadius = 0.14 * structuralScale;
  const legOffsets: [number, number][] = [
    [-legRadius, -legRadius],
    [legRadius, -legRadius],
    [legRadius, legRadius],
    [-legRadius, legRadius],
  ];
  const baseRadius = 0.22 * structuralScale;
  const ringSpan = 0.3 * structuralScale;
  const braceSpan = 0.24 * structuralScale;
  const topWidth = 0.42 * structuralScale;
  const topDepth = 0.3 * structuralScale;

  return (
    <group position={[x, 0, z]}>
      <mesh position={[0, 0.02, 0]} receiveShadow>
        <cylinderGeometry args={[baseRadius, baseRadius + 0.04, 0.07, 18]} />
        <meshStandardMaterial color="#475569" metalness={0.25} roughness={0.85} />
      </mesh>
      {legOffsets.map(([dx, dz], index) => (
        <mesh key={`leg-${index}`} position={[dx, y / 2, dz]} castShadow receiveShadow>
          <cylinderGeometry args={[0.015, 0.019, y, 10]} />
          <meshStandardMaterial color="#5b6b80" metalness={0.5} roughness={0.38} />
        </mesh>
      ))}
      {[0.24, 0.5, 0.76].map((fraction) => (
        <mesh key={`ring-${fraction}`} position={[0, y * fraction, 0]} castShadow receiveShadow>
          <boxGeometry args={[ringSpan, 0.022, ringSpan]} />
          <meshStandardMaterial color="#94a3b8" metalness={0.28} roughness={0.55} />
        </mesh>
      ))}
      {[
        { position: [0, y * 0.18, 0], rotation: [0, 0, Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
        { position: [0, y * 0.18, 0], rotation: [0, 0, -Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
        { position: [0, y * 0.44, 0], rotation: [0, 0, Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
        { position: [0, y * 0.44, 0], rotation: [0, 0, -Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
        { position: [0, y * 0.7, 0], rotation: [0, 0, Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
        { position: [0, y * 0.7, 0], rotation: [0, 0, -Math.PI / 4], size: [braceSpan, 0.012, 0.012] },
      ].map((brace, index) => (
        <mesh
          key={`brace-${index}`}
          position={brace.position as [number, number, number]}
          rotation={brace.rotation as [number, number, number]}
          castShadow
        >
          <boxGeometry args={brace.size as [number, number, number]} />
          <meshStandardMaterial color="#7c8ba1" metalness={0.38} roughness={0.42} />
        </mesh>
      ))}
      <mesh position={[0, y + 0.08, 0]} castShadow receiveShadow>
        <boxGeometry args={[topWidth, 0.05, topDepth]} />
        <meshStandardMaterial color="#1e293b" metalness={0.35} roughness={0.45} />
      </mesh>
      {isNight ? (
        <>
          <pointLight position={[0, y + 0.2, 0]} intensity={12} distance={6.5} decay={2} color="#fff7d6" />
          <pointLight position={[0, y + 0.16, 0]} intensity={6} distance={3.2} decay={2} color="#cbd5ff" />
        </>
      ) : null}
    </group>
  );
}

function EngineeringGround({ center }: { center: [number, number, number] }) {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], -0.01, center[2]]} receiveShadow>
        <planeGeometry args={[7.2, 7.2]} />
        <meshStandardMaterial color="#0b1120" roughness={1} />
      </mesh>
      <gridHelper
        args={[7, 14, "#60a5fa", "#1e3a8a"]}
        position={[center[0], 0.001, center[2]]}
      />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.002, center[2]]} receiveShadow>
        <ringGeometry args={[1.55, 1.58, 96]} />
        <meshStandardMaterial color="#38bdf8" emissive="#0ea5e9" emissiveIntensity={0.12} roughness={0.5} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.003, center[2]]} receiveShadow>
        <planeGeometry args={[0.42, 1.48]} />
        <meshStandardMaterial color="#1e293b" roughness={0.9} />
      </mesh>
      <Line
        points={[
          [center[0] - 0.5, 0.004, center[2]],
          [center[0] + 0.5, 0.004, center[2]],
        ]}
        color="#22d3ee"
        lineWidth={1}
      />
      <Line
        points={[
          [center[0], 0.004, center[2] - 0.8],
          [center[0], 0.004, center[2] + 0.8],
        ]}
        color="#22d3ee"
        lineWidth={1}
      />
    </group>
  );
}

function StadiumGround({
  center,
  lightingMode,
}: {
  center: [number, number, number];
  lightingMode: LightingMode;
}) {
  const isNight = lightingMode === "night";
  const boundary = circlePoints(2.28, 0.02, center, 96);
  const innerRing = circlePoints(1.48, 0.02, center, 96);
  const pitchGuide = circlePoints(0.58, 0.018, center, 96);
  const grassBands = [
    { radius: 2.42, color: isNight ? "#2d7f3a" : "#51a653", y: 0.012 },
    { radius: 1.98, color: isNight ? "#256f34" : "#4a9e4e", y: 0.014 },
    { radius: 1.54, color: isNight ? "#2d7f3a" : "#58ad58", y: 0.016 },
    { radius: 1.08, color: isNight ? "#327f3f" : "#63b95d", y: 0.018 },
  ];
  const seatBands = [
    { y: 0.42, inner: 3.15, outer: 4.12, color: isNight ? "#475569" : "#94a3b8" },
    { y: 0.78, inner: 3.42, outer: 4.36, color: isNight ? "#334155" : "#cbd5e1" },
    { y: 1.18, inner: 3.7, outer: 4.7, color: isNight ? "#1e293b" : "#e2e8f0" },
  ];

  return (
    <group>
      <mesh position={[center[0], -0.08, center[2]]} receiveShadow>
        <cylinderGeometry args={[4.8, 5.2, 0.18, 80]} />
        <meshStandardMaterial color={isNight ? "#111827" : "#334155"} roughness={0.92} />
      </mesh>

      <mesh position={[center[0], 0, center[2]]} receiveShadow>
        <cylinderGeometry args={[4.2, 4.2, 0.06, 96]} />
        <meshStandardMaterial color={isNight ? "#1f4f2c" : "#437057"} roughness={1} />
      </mesh>

      {grassBands.map((band) => (
        <mesh
          key={`grass-${band.radius}`}
          rotation={[-Math.PI / 2, 0, 0]}
          position={[center[0], band.y, center[2]]}
          receiveShadow
        >
          <circleGeometry args={[band.radius, 96]} />
          <meshStandardMaterial color={band.color} roughness={1} />
        </mesh>
      ))}

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.021, center[2]]} receiveShadow>
        <circleGeometry args={[0.92, 96]} />
        <meshStandardMaterial color={isNight ? "#7fbf6a" : "#93d277"} roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.024, center[2]]} receiveShadow>
        <planeGeometry args={[0.98, 2.08]} />
        <meshStandardMaterial color="#4a2813" roughness={0.98} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.026, center[2]]} receiveShadow>
        <planeGeometry args={[0.82, 1.92]} />
        <meshStandardMaterial color="#6b3a19" roughness={0.95} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.029, center[2] - 0.58]} receiveShadow>
        <planeGeometry args={[0.48, 0.12]} />
        <meshStandardMaterial color="#efe4c5" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.029, center[2] + 0.58]} receiveShadow>
        <planeGeometry args={[0.48, 0.12]} />
        <meshStandardMaterial color="#efe4c5" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.03, center[2] - 0.78]} receiveShadow>
        <planeGeometry args={[0.58, 0.04]} />
        <meshStandardMaterial color="#f8fafc" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.03, center[2] + 0.78]} receiveShadow>
        <planeGeometry args={[0.58, 0.04]} />
        <meshStandardMaterial color="#f8fafc" roughness={1} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[center[0], 0.031, center[2]]} receiveShadow>
        <planeGeometry args={[0.2, 1.94]} />
        <meshStandardMaterial color="#2b1509" roughness={1} />
      </mesh>

      <WicketSet position={[center[0], 0.031, center[2] - 0.68]} />
      <WicketSet position={[center[0], 0.031, center[2] + 0.68]} />

      <Line points={boundary} color="#f8fafc" lineWidth={1.3} />
      <Line points={innerRing} color="#d9f99d" lineWidth={0.9} dashed dashSize={0.08} gapSize={0.06} />
      <Line points={pitchGuide} color="#86efac" lineWidth={0.7} dashed dashSize={0.05} gapSize={0.05} />

      {seatBands.map((band) => (
        <mesh key={`seat-${band.y}`} position={[center[0], band.y, center[2]]} receiveShadow>
          <cylinderGeometry args={[band.inner, band.outer, 0.3, 72, 1, true]} />
          <meshStandardMaterial
            color={band.color}
            metalness={0.06}
            roughness={0.88}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}

      <SeatRows center={center} isNight={isNight} />

      <mesh position={[center[0], 0.98, center[2]]} receiveShadow>
        <cylinderGeometry args={[4.02, 4.62, 0.18, 72, 1, true]} />
        <meshStandardMaterial
          color={isNight ? "#0f172a" : "#64748b"}
          metalness={0.08}
          roughness={0.82}
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

function SceneCameraControls({
  center,
  viewPreset,
  resetSignal,
}: {
  center: [number, number, number];
  viewPreset: ViewPreset;
  resetSignal: number;
}) {
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const { camera } = useThree();
  const target = useMemo(
    () => new THREE.Vector3(center[0], 0.65, center[2]),
    [center[0], center[2]],
  );
  const offset = viewPreset === "top"
    ? TOP_VIEW_OFFSET
    : viewPreset === "front"
      ? FRONT_VIEW_OFFSET
      : SIDE_VIEW_OFFSET;

  useEffect(() => {
    const controls = controlsRef.current;
    if (!controls) return;
    camera.position.set(
      target.x + offset.x,
      target.y + offset.y,
      target.z + offset.z,
    );
    controls.target.copy(target);
    controls.update();
  }, [camera, offset, target, resetSignal]);

  return (
    <OrbitControls
      ref={(instance) => {
        controlsRef.current = instance;
      }}
      makeDefault
      target={target}
      minPolarAngle={0.1}
      maxPolarAngle={1.5}
      minDistance={3.6}
      maxDistance={8.5}
    />
  );
}

export function SpiderScene({
  state,
  lightingMode,
  sceneMode,
}: {
  state: SpiderState | null;
  lightingMode: LightingMode;
  sceneMode: SceneMode;
}) {
  const [resetSignal, setResetSignal] = useState(0);
  const [viewPreset, setViewPreset] = useState<ViewPreset>("side");
  const isNight = lightingMode === "night";
  const isEngineering = sceneMode === "engineering";
  const anchorEntries = Object.entries(state?.anchors ?? {
    A: [0, 0, 1.5],
    B: [2, 0, 1.5],
    C: [2, 2, 1.5],
    D: [0, 2, 1.5],
  });
  const anchors = anchorEntries
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, [x, y, z]]) => [x, z, y] as [number, number, number]);
  const centerX = anchors.reduce((sum, anchor) => sum + anchor[0], 0) / anchors.length;
  const centerZ = anchors.reduce((sum, anchor) => sum + anchor[2], 0) / anchors.length;
  const center: [number, number, number] = [centerX, 0, centerZ];
  const displayAnchors = anchors.map(([x, y, z]) => {
    const dx = x - centerX;
    const dz = z - centerZ;
    return [centerX + dx * 1.62, y, centerZ + dz * 1.62] as [number, number, number];
  });
  const activeAnchors = isEngineering ? anchors : displayAnchors;
  const P: [number, number, number] = state
    ? [state.position.x, state.position.z, state.position.y]
    : [centerX, 0.9, centerZ];

  if (!state) return <div className="sceneFallback">Loading 3D scene...</div>;

  return (
    <div className="sceneWrap">
      <div className="sceneControls">
        <div className="sceneBadge">{isEngineering ? "Engineering View" : "Stadium View"}</div>
        <button
          className={`sceneButton ${viewPreset === "side" ? "active" : ""}`}
          onClick={() => {
            setViewPreset("side");
            setResetSignal((value) => value + 1);
          }}
          type="button"
        >
          Side View
        </button>
        <button
          className={`sceneButton ${viewPreset === "top" ? "active" : ""}`}
          onClick={() => {
            setViewPreset("top");
            setResetSignal((value) => value + 1);
          }}
          type="button"
        >
          Top View
        </button>
        <button
          className={`sceneButton ${viewPreset === "front" ? "active" : ""}`}
          onClick={() => {
            setViewPreset("front");
            setResetSignal((value) => value + 1);
          }}
          type="button"
        >
          Front View
        </button>
      </div>
      <Canvas shadows camera={{ position: [4.9, 2.6, 4.8], fov: 40 }}>
        <color attach="background" args={[isEngineering ? "#09101d" : isNight ? "#08111f" : "#b7d8ff"]} />
        <fog attach="fog" args={[isEngineering ? "#09101d" : isNight ? "#08111f" : "#b7d8ff", 8, 20]} />
        <ambientLight intensity={isEngineering ? 0.75 : isNight ? 0.28 : 1} color={isNight ? "#9db4ff" : "#ffffff"} />
        <hemisphereLight
          args={[
            isEngineering ? "#0f172a" : isNight ? "#19325f" : "#f0f9ff",
            isEngineering ? "#111827" : isNight ? "#0b1f0f" : "#365314",
            isEngineering ? 0.85 : isNight ? 0.45 : 1.15,
          ]}
        />
        <directionalLight
          position={isEngineering ? [4, 5.5, 3] : isNight ? [2.5, 5, -1] : [5, 6, 2]}
          intensity={isEngineering ? 1.35 : isNight ? 0.35 : 2.1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        {isEngineering ? null : (
          <Sky
            sunPosition={isNight ? [-4, 1, -2] : [6, 3, 2]}
            turbidity={isNight ? 12 : 7}
            rayleigh={isNight ? 0.4 : 2.2}
            mieCoefficient={isNight ? 0.02 : 0.005}
          />
        )}
        {isEngineering ? <EngineeringGround center={center} /> : <StadiumGround center={center} lightingMode={lightingMode} />}
        <Line
          points={[...activeAnchors, activeAnchors[0]]}
          color={isEngineering ? "#38bdf8" : isNight ? "#64748b" : "#94a3b8"}
          lineWidth={1.6}
        />
        {activeAnchors.map((anchor, index) => (
          <Line key={`cable-${index}`} points={[anchor, P]} color={isEngineering ? "#22d3ee" : "#ef4444"} lineWidth={2.1} />
        ))}
        <Trail points={state.trail} />
        {activeAnchors.map((anchor, index) => (
          <CornerTower
            key={`tower-${index}`}
            position={anchor}
            lightingMode={lightingMode}
            structuralScale={isEngineering ? 0.88 : 1}
          />
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
        <SceneCameraControls center={center} viewPreset={viewPreset} resetSignal={resetSignal} />
        <Environment preset={isEngineering ? "warehouse" : isNight ? "city" : "park"} />
      </Canvas>
    </div>
  );
}
