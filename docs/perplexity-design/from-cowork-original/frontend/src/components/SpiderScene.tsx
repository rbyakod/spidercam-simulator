import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html, Line, Grid } from "@react-three/drei";
import { SpiderState } from "../types";

function AnchorCube({ pos, label }: { pos: [number, number, number]; label: string }) {
  return (
    <mesh position={pos}>
      <boxGeometry args={[0.08, 0.08, 0.08]} />
      <meshStandardMaterial color="#94a3b8" />
      <Html distanceFactor={8}>
        <span style={{ color: "#e2e8f0", fontSize: 11, background: "rgba(0,0,0,0.6)", padding: "1px 4px", borderRadius: 4 }}>{label}</span>
      </Html>
    </mesh>
  );
}

function Cable({ from, to, color }: { from: [number, number, number]; to: [number, number, number]; color: string }) {
  return <Line points={[from, to]} color={color} lineWidth={1.5} />;
}

function Trail({ points }: { points: { x: number; y: number; z: number }[] }) {
  if (!points.length) return null;
  const pts = points.map((p) => [p.x, p.z, p.y] as [number, number, number]);
  return <Line points={pts} color="#f59e0b" lineWidth={1} opacity={0.5} transparent />;
}

function Frame({ state }: { state: SpiderState }) {
  const { anchors, position, physics } = state;
  const p: [number, number, number] = [position.x, position.z, position.y];
  const A: [number, number, number] = [anchors.A[0], anchors.A[2], anchors.A[1]];
  const B: [number, number, number] = [anchors.B[0], anchors.B[2], anchors.B[1]];
  const C: [number, number, number] = [anchors.C[0], anchors.C[2], anchors.C[1]];
  const D: [number, number, number] = [anchors.D[0], anchors.D[2], anchors.D[1]];
  const hot = physics?.overload ? "#dc2626" : state.estop ? "#dc2626" : "#f59e0b";
  return (
    <>
      <AnchorCube pos={A} label="A" />
      <AnchorCube pos={B} label="B" />
      <AnchorCube pos={C} label="C" />
      <AnchorCube pos={D} label="D" />
      <Cable from={A} to={p} color="#60a5fa" />
      <Cable from={B} to={p} color="#60a5fa" />
      <Cable from={C} to={p} color="#60a5fa" />
      <Cable from={D} to={p} color="#60a5fa" />
      <mesh position={p}>
        <sphereGeometry args={[0.06, 16, 16]} />
        <meshStandardMaterial color={hot} emissive={hot} emissiveIntensity={0.3} />
        <Html distanceFactor={6}>
          <div style={{ color: "#fff", background: "rgba(0,0,0,0.7)", borderRadius: 6, padding: "2px 6px", fontSize: 11 }}>
            X {position.x.toFixed(2)} | Y {position.y.toFixed(2)} | Z {position.z.toFixed(2)}
          </div>
        </Html>
      </mesh>
      {state.trail && <Trail points={state.trail} />}
    </>
  );
}

export function SpiderScene({ state }: { state: SpiderState | null }) {
  if (!state) return <div className="sceneFallback"><p>Loading 3D scene...</p></div>;
  return (
    <Canvas camera={{ position: [3, 3, 3], fov: 50 }} style={{ background: "#0b1020" }}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} />
      <Grid args={[4, 4]} cellColor="#334155" sectionColor="#334155" position={[1, 0, 1]} />
      <Frame state={state} />
      <OrbitControls makeDefault />
    </Canvas>
  );
}
