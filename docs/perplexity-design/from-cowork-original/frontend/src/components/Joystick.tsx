import { useRef, useState } from "react";

export function Joystick({ onMove, onEnd }: { onMove: (nx: number, ny: number) => void; onEnd: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const [stick, setStick] = useState({ x: 0, y: 0 });
  const [active, setActive] = useState(false);

  const update = (clientX: number, clientY: number) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const dx = clientX - cx, dy = clientY - cy;
    const max = r.width * 0.35;
    const len = Math.sqrt(dx * dx + dy * dy) || 1;
    const clamped = Math.min(max, len);
    const x = (dx / len) * clamped, y = (dy / len) * clamped;
    setStick({ x, y });
    onMove(x / max, y / max);
  };

  return (
    <div>
      <div style={{ textAlign: "center", fontSize: 12, color: "#94a3b8", marginBottom: 6 }}>Joystick</div>
      <div
        ref={ref}
        className="joyBase"
        onPointerDown={(e) => {
          setActive(true);
          (e.target as HTMLDivElement).setPointerCapture(e.pointerId);
          update(e.clientX, e.clientY);
        }}
        onPointerMove={(e) => active && update(e.clientX, e.clientY)}
        onPointerUp={() => {
          setActive(false);
          setStick({ x: 0, y: 0 });
          onEnd();
        }}
      >
        <div className="joyStick" style={{ transform: `translate(${stick.x}px, ${stick.y}px)` }} />
      </div>
    </div>
  );
}
