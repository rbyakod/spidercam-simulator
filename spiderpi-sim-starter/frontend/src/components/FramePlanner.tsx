import { useMemo, useState } from "react";
import { SpiderState } from "../types";

type PlannerInputs = {
  frameWidth: number;
  frameLength: number;
  anchorHeight: number;
  marginX: number;
  marginY: number;
  minZ: number;
  maxZ: number;
  spoolRadius: number;
  motorStepsPerRev: number;
  microsteps: number;
  carriageMass: number;
  payloadMass: number;
  maxSpeed: number;
  maxAccel: number;
};

const DEFAULTS: PlannerInputs = {
  frameWidth: 2,
  frameLength: 2,
  anchorHeight: 1.5,
  marginX: 0.2,
  marginY: 0.2,
  minZ: 0.3,
  maxZ: 1.3,
  spoolRadius: 0.011,
  motorStepsPerRev: 200,
  microsteps: 16,
  carriageMass: 0.4,
  payloadMass: 0.08,
  maxSpeed: 0.7,
  maxAccel: 0.9,
};

function num(value: number, digits = 3) {
  return value.toFixed(digits);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function plannerFromState(state: SpiderState): PlannerInputs {
  const anchors = Object.values(state.anchors);
  const xs = anchors.map(([x]) => x);
  const ys = anchors.map(([, y]) => y);
  const zs = anchors.map(([, , z]) => z);
  const frameWidth = Math.max(...xs) - Math.min(...xs);
  const frameLength = Math.max(...ys) - Math.min(...ys);
  const anchorHeight = zs.reduce((sum, z) => sum + z, 0) / zs.length;
  return {
    ...DEFAULTS,
    frameWidth,
    frameLength,
    anchorHeight,
    marginX: state.bounds.x[0] - Math.min(...xs),
    marginY: state.bounds.y[0] - Math.min(...ys),
    minZ: state.bounds.z[0],
    maxZ: state.bounds.z[1],
  };
}

function InputField({
  label,
  value,
  step,
  onChange,
}: {
  label: string;
  value: number;
  step: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="plannerField">
      <span>{label}</span>
      <input
        className="plannerInput"
        type="number"
        step={step}
        value={Number.isFinite(value) ? value : 0}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

export function FramePlanner({ state }: { state: SpiderState | null }) {
  const [inputs, setInputs] = useState<PlannerInputs>(DEFAULTS);

  const derived = useMemo(() => {
    const frameWidth = Math.max(0.4, inputs.frameWidth);
    const frameLength = Math.max(0.4, inputs.frameLength);
    const anchorHeight = Math.max(0.3, inputs.anchorHeight);
    const marginX = clamp(inputs.marginX, 0.02, frameWidth / 2 - 0.02);
    const marginY = clamp(inputs.marginY, 0.02, frameLength / 2 - 0.02);
    const safeMaxZ = clamp(inputs.maxZ, 0.1, anchorHeight - 0.08);
    const safeMinZ = clamp(inputs.minZ, 0.05, safeMaxZ - 0.05);
    const bounds = {
      x: [marginX, frameWidth - marginX] as [number, number],
      y: [marginY, frameLength - marginY] as [number, number],
      z: [safeMinZ, safeMaxZ] as [number, number],
    };
    const anchors = {
      A: [0, 0, anchorHeight] as [number, number, number],
      B: [frameWidth, 0, anchorHeight] as [number, number, number],
      C: [frameWidth, frameLength, anchorHeight] as [number, number, number],
      D: [0, frameLength, anchorHeight] as [number, number, number],
    };
    const center = {
      x: frameWidth / 2,
      y: frameLength / 2,
      z: (safeMinZ + safeMaxZ) / 2,
    };
    const workspace = {
      width: bounds.x[1] - bounds.x[0],
      length: bounds.y[1] - bounds.y[0],
      height: bounds.z[1] - bounds.z[0],
    };
    const stepsPerMeter =
      (Math.max(1, inputs.motorStepsPerRev) * Math.max(1, inputs.microsteps)) /
      (2 * Math.PI * Math.max(0.001, inputs.spoolRadius));
    const turnsPerMeter = 1 / (2 * Math.PI * Math.max(0.001, inputs.spoolRadius));

    const samplePoints = [
      { name: "Home", x: center.x, y: center.y, z: center.z },
      { name: "Center Low", x: center.x, y: center.y, z: safeMinZ },
      { name: "Center High", x: center.x, y: center.y, z: safeMaxZ },
      { name: "SW", x: bounds.x[0], y: bounds.y[0], z: safeMinZ },
      { name: "SE", x: bounds.x[1], y: bounds.y[0], z: safeMinZ },
      { name: "NE", x: bounds.x[1], y: bounds.y[1], z: safeMinZ },
      { name: "NW", x: bounds.x[0], y: bounds.y[1], z: safeMinZ },
    ];

    const lengthsFor = (point: { x: number; y: number; z: number }) =>
      Object.fromEntries(
        Object.entries(anchors).map(([name, [ax, ay, az]]) => [
          name,
          Math.sqrt((point.x - ax) ** 2 + (point.y - ay) ** 2 + (point.z - az) ** 2),
        ]),
      ) as Record<keyof typeof anchors, number>;

    const angleFromVertical = (point: { x: number; y: number; z: number }) =>
      Math.max(
        ...Object.values(anchors).map(([ax, ay, az]) => {
          const horizontal = Math.hypot(point.x - ax, point.y - ay);
          const verticalDrop = Math.max(0.001, az - point.z);
          return (Math.atan(horizontal / verticalDrop) * 180) / Math.PI;
        }),
      );

    const samples = samplePoints.map((point) => ({
      ...point,
      lengths: lengthsFor(point),
      worstAngleDeg: angleFromVertical(point),
    }));

    const anchorTravel = (["A", "B", "C", "D"] as const).map((name) => {
      const values = samples.map((sample) => sample.lengths[name]);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const travel = max - min;
      return {
        name,
        min,
        max,
        travel,
        turns: travel * turnsPerMeter,
        steps: travel * stepsPerMeter,
      };
    });

    const warnings: string[] = [];
    if (workspace.width < frameWidth * 0.45) warnings.push("X margin is large relative to frame width; usable X travel is narrow.");
    if (workspace.length < frameLength * 0.45) warnings.push("Y margin is large relative to frame length; usable Y travel is narrow.");
    if (safeMaxZ > anchorHeight - 0.15) warnings.push("Max Z is close to anchor height; leave more clearance below the frame.");
    if (safeMinZ < 0.12) warnings.push("Min Z is very low; verify carriage and cable clearance in the real build.");
    if (Math.max(...samples.map((sample) => sample.worstAngleDeg)) > 68) warnings.push("One or more sampled cable angles are steep from vertical; edge positions may be mechanically awkward.");
    if (inputs.spoolRadius < 0.008 || inputs.spoolRadius > 0.03) warnings.push("Spool radius is outside a typical small winch range; verify travel and torque assumptions.");

    return {
      frameWidth,
      frameLength,
      anchorHeight,
      bounds,
      anchors,
      center,
      workspace,
      stepsPerMeter,
      turnsPerMeter,
      samples,
      anchorTravel,
      warnings,
      diagonalXY: Math.hypot(frameWidth, frameLength),
      maxCableLength: Math.max(...samples.flatMap((sample) => Object.values(sample.lengths))),
      minCableLength: Math.min(...samples.flatMap((sample) => Object.values(sample.lengths))),
      totalMass: inputs.carriageMass + inputs.payloadMass,
    };
  }, [inputs]);

  const topView = {
    width: 320,
    height: 240,
    pad: 26,
  };
  const xScale = (value: number) =>
    topView.pad + (value / derived.frameWidth) * (topView.width - topView.pad * 2);
  const yScale = (value: number) =>
    topView.pad + (value / derived.frameLength) * (topView.height - topView.pad * 2);

  const sideView = {
    width: 320,
    height: 180,
    pad: 24,
  };
  const zScale = (value: number) =>
    sideView.height - sideView.pad - (value / derived.anchorHeight) * (sideView.height - sideView.pad * 2);

  return (
    <div className="plannerLayout">
      <div className="panel plannerPanel">
        <div className="plannerHeader">
          <div>
            <h3>Frame Planner</h3>
            <p className="plannerIntro">
              Size your physical frame first, then use these computed anchors, bounds, cable travel, and drive conversions to guide a DIY build.
            </p>
          </div>
          <div className="plannerActions">
            <button type="button" onClick={() => setInputs(DEFAULTS)}>Reset Defaults</button>
            <button
              type="button"
              onClick={() => {
                if (!state) return;
                setInputs(plannerFromState(state));
              }}
            >
              Load Current Frame
            </button>
          </div>
        </div>

        <div className="plannerSection">
          <h4>Frame Geometry</h4>
          <div className="plannerFields">
            <InputField label="Frame Width (m)" value={inputs.frameWidth} step={0.1} onChange={(value) => setInputs((current) => ({ ...current, frameWidth: value }))} />
            <InputField label="Frame Length (m)" value={inputs.frameLength} step={0.1} onChange={(value) => setInputs((current) => ({ ...current, frameLength: value }))} />
            <InputField label="Anchor Height (m)" value={inputs.anchorHeight} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, anchorHeight: value }))} />
            <InputField label="X Edge Margin (m)" value={inputs.marginX} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, marginX: value }))} />
            <InputField label="Y Edge Margin (m)" value={inputs.marginY} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, marginY: value }))} />
            <InputField label="Min Working Z (m)" value={inputs.minZ} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, minZ: value }))} />
            <InputField label="Max Working Z (m)" value={inputs.maxZ} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, maxZ: value }))} />
          </div>
        </div>

        <div className="plannerSection">
          <h4>Drive Parameters</h4>
          <div className="plannerFields">
            <InputField label="Spool Radius (m)" value={inputs.spoolRadius} step={0.001} onChange={(value) => setInputs((current) => ({ ...current, spoolRadius: value }))} />
            <InputField label="Motor Steps / Rev" value={inputs.motorStepsPerRev} step={1} onChange={(value) => setInputs((current) => ({ ...current, motorStepsPerRev: value }))} />
            <InputField label="Microsteps" value={inputs.microsteps} step={1} onChange={(value) => setInputs((current) => ({ ...current, microsteps: value }))} />
            <InputField label="Carriage Mass (kg)" value={inputs.carriageMass} step={0.01} onChange={(value) => setInputs((current) => ({ ...current, carriageMass: value }))} />
            <InputField label="Payload Mass (kg)" value={inputs.payloadMass} step={0.01} onChange={(value) => setInputs((current) => ({ ...current, payloadMass: value }))} />
            <InputField label="Target Max Speed (m/s)" value={inputs.maxSpeed} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, maxSpeed: value }))} />
            <InputField label="Target Max Accel (m/s²)" value={inputs.maxAccel} step={0.05} onChange={(value) => setInputs((current) => ({ ...current, maxAccel: value }))} />
          </div>
        </div>
      </div>

      <div className="plannerResults">
        <div className="panel">
          <h3>Computed Parameters</h3>
          <div className="kv"><span>Anchors</span><span>{`A(0,0,${num(derived.anchorHeight, 2)}) B(${num(derived.frameWidth, 2)},0,${num(derived.anchorHeight, 2)})`}</span></div>
          <div className="kv"><span>Bounds X</span><span>{`${num(derived.bounds.x[0], 2)} to ${num(derived.bounds.x[1], 2)} m`}</span></div>
          <div className="kv"><span>Bounds Y</span><span>{`${num(derived.bounds.y[0], 2)} to ${num(derived.bounds.y[1], 2)} m`}</span></div>
          <div className="kv"><span>Bounds Z</span><span>{`${num(derived.bounds.z[0], 2)} to ${num(derived.bounds.z[1], 2)} m`}</span></div>
          <div className="kv"><span>Usable XY</span><span>{`${num(derived.workspace.width, 2)} x ${num(derived.workspace.length, 2)} m`}</span></div>
          <div className="kv"><span>Usable Z Travel</span><span>{`${num(derived.workspace.height, 2)} m`}</span></div>
          <div className="kv"><span>Frame Diagonal</span><span>{`${num(derived.diagonalXY, 2)} m`}</span></div>
          <div className="kv"><span>Steps / Meter</span><span>{`${Math.round(derived.stepsPerMeter)} steps`}</span></div>
          <div className="kv"><span>Turns / Meter</span><span>{`${num(derived.turnsPerMeter, 2)} rev`}</span></div>
          <div className="kv"><span>Cable Length Range</span><span>{`${num(derived.minCableLength, 2)} to ${num(derived.maxCableLength, 2)} m`}</span></div>
          <div className="kv"><span>Total Moving Mass</span><span>{`${num(derived.totalMass, 2)} kg`}</span></div>
        </div>

        <div className="panel">
          <h3>Cable Travel By Corner</h3>
          {derived.anchorTravel.map((item) => (
            <div className="kv" key={item.name}>
              <span>{`Cable ${item.name}`}</span>
              <span>{`${num(item.travel, 3)} m / ${Math.round(item.steps)} steps`}</span>
            </div>
          ))}
        </div>

        <div className="panel">
          <h3>Sample Points</h3>
          {derived.samples.map((sample) => (
            <div className="plannerSample" key={sample.name}>
              <div className="plannerSampleTitle">{sample.name}</div>
              <div className="plannerSampleMeta">
                {`(${num(sample.x, 2)}, ${num(sample.y, 2)}, ${num(sample.z, 2)})  worst angle ${num(sample.worstAngleDeg, 1)}°`}
              </div>
              <div className="plannerLengthGrid">
                {(["A", "B", "C", "D"] as const).map((name) => (
                  <span key={name}>{`${name}: ${num(sample.lengths[name], 3)} m`}</span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="panel">
          <h3>Warnings</h3>
          {derived.warnings.length ? (
            <div className="plannerWarnings">
              {derived.warnings.map((warning) => (
                <div className="plannerWarning" key={warning}>{warning}</div>
              ))}
            </div>
          ) : (
            <div className="plannerOk">No obvious geometry warnings for this frame size.</div>
          )}
        </div>
      </div>

      <div className="plannerPreview">
        <div className="panel">
          <h3>Engineering Preview</h3>
          <div className="plannerPreviewGrid">
            <svg className="plannerSvg" viewBox={`0 0 ${topView.width} ${topView.height}`}>
              <rect x="0" y="0" width={topView.width} height={topView.height} rx="16" fill="#0f172a" />
              <rect
                x={xScale(0)}
                y={yScale(0)}
                width={xScale(derived.frameWidth) - xScale(0)}
                height={yScale(derived.frameLength) - yScale(0)}
                fill="none"
                stroke="#93c5fd"
                strokeWidth="3"
              />
              <rect
                x={xScale(derived.bounds.x[0])}
                y={yScale(derived.bounds.y[0])}
                width={xScale(derived.bounds.x[1]) - xScale(derived.bounds.x[0])}
                height={yScale(derived.bounds.y[1]) - yScale(derived.bounds.y[0])}
                fill="rgba(34,197,94,0.12)"
                stroke="#4ade80"
                strokeWidth="2"
                strokeDasharray="6 6"
              />
              {Object.entries(derived.anchors).map(([name, [x, y]]) => (
                <g key={name}>
                  <circle cx={xScale(x)} cy={yScale(y)} r="6" fill="#f59e0b" />
                  <text x={xScale(x) + 10} y={yScale(y) - 10} fill="#e2e8f0" fontSize="12">{name}</text>
                </g>
              ))}
              <circle cx={xScale(derived.center.x)} cy={yScale(derived.center.y)} r="5" fill="#f8fafc" />
              <text x={xScale(derived.center.x) + 8} y={yScale(derived.center.y) + 18} fill="#f8fafc" fontSize="12">Home</text>
            </svg>

            <svg className="plannerSvg" viewBox={`0 0 ${sideView.width} ${sideView.height}`}>
              <rect x="0" y="0" width={sideView.width} height={sideView.height} rx="16" fill="#0f172a" />
              <line x1={sideView.pad} y1={zScale(0)} x2={sideView.width - sideView.pad} y2={zScale(0)} stroke="#334155" strokeWidth="2" />
              <line x1={sideView.pad} y1={zScale(derived.anchorHeight)} x2={sideView.width - sideView.pad} y2={zScale(derived.anchorHeight)} stroke="#93c5fd" strokeWidth="3" />
              <rect
                x={sideView.pad + 40}
                y={zScale(derived.bounds.z[1])}
                width={sideView.width - sideView.pad * 2 - 80}
                height={zScale(derived.bounds.z[0]) - zScale(derived.bounds.z[1])}
                fill="rgba(34,197,94,0.12)"
                stroke="#4ade80"
                strokeWidth="2"
                strokeDasharray="6 6"
              />
              <line x1={sideView.width / 2} y1={zScale(derived.anchorHeight)} x2={sideView.width / 2} y2={zScale(derived.center.z)} stroke="#f59e0b" strokeWidth="2" />
              <circle cx={sideView.width / 2} cy={zScale(derived.center.z)} r="5" fill="#f8fafc" />
              <text x={sideView.pad} y={zScale(derived.anchorHeight) - 8} fill="#e2e8f0" fontSize="12">{`Anchor Height ${num(derived.anchorHeight, 2)} m`}</text>
              <text x={sideView.pad} y={zScale(derived.bounds.z[1]) - 8} fill="#4ade80" fontSize="12">{`Z Max ${num(derived.bounds.z[1], 2)} m`}</text>
              <text x={sideView.pad} y={zScale(derived.bounds.z[0]) - 8} fill="#4ade80" fontSize="12">{`Z Min ${num(derived.bounds.z[0], 2)} m`}</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
