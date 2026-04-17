import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Grid, Html, Environment } from "@react-three/drei";
import { SpiderState } from "../types";
import * as THREE from "three";

function Trail({ points }: { points: { x: number; y: number; z: number }[] }) {
  if (!points.length) return null;
  const pts = points.map((p) => [p.x, p.z, p.y] as [number, number, number]);
  return <Line points={pts} color="#22c55e" lineWidth={1} dashed />;
}

export function SpiderScene({ state }: { state: SpiderState | null }) {
  if (!state) return <div className="sceneFallback">Loading 3D scene...</div>;
  const A: [number, number, number] = [0, 1.5, 0];
  const B: [number, number, number] = [2, 1.5, 0];
  const C: [number, number, number] = [2, 1.5, 2];
  const D: [number, number, number] = [0, 1.5, 2];
  const P: [number, number, number] = [state.position.x, state.position.z, state.position.y];
  return (
    <div className="sceneWrap">
      <Canvas shadows camera={{ position: [3.1, 2.4, 3.1], fov: 45 }}>
        <color attach="background" args={["#0b1020"]} />
        <ambientLight intensity={0.8} />
        <directionalLight position={[3, 4, 2]} intensity={1.6} castShadow />
        <Grid args={[4, 4]} position={[1, 0, 1]} cellColor={"#334155"} sectionColor={"#475569"} />
        <Line points={[A, B, C, D, A]} color="#64748b" lineWidth={2} />
        <Line points={[A, P]} color="#ef4444" lineWidth={2} />
        <Line points={[B, P]} color="#ef4444" lineWidth={2} />
        <Line points={[C, P]} color="#ef4444" lineWidth={2} />
        <Line points={[D, P]} color="#ef4444" lineWidth={2} />
        <Trail points={state.trail} />
        {[A, B, C, D].map((pos, i) => (
          <mesh key={i} position={pos}><boxGeometry args={[0.08,0.08,0.08]} /><meshStandardMaterial color="#38bdf8" /></mesh>
        ))}
        <mesh position={P}><sphereGeometry args={[0.06, 24, 24]} /><meshStandardMaterial color={state.estop ? "#dc2626" : "#f59e0b"} /></mesh>
        <mesh position={[P[0], P[1]-0.05, P[2]]}><boxGeometry args={[0.22,0.04,0.12]} /><meshStandardMaterial color="#f8fafc" /></mesh>
        <Html position={[P[0], P[1]+0.16, P[2]]} center distanceFactor={10}><div className="tele3d">X {state.position.x.toFixed(2)} Y {state.position.y.toFixed(2)} Z {state.position.z.toFixed(2)}</div></Html>
        <OrbitControls makeDefault target={new THREE.Vector3(1, 0.8, 1)} />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}
