import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function HardwareGatePanel() {
  const [simSwitches, setSimSwitches] = useState<Record<string, boolean>>({ A:false,B:false,C:false,D:false });

  const toggleSwitch = async (axis: string) => {
    const newVal = !simSwitches[axis];
    setSimSwitches(prev => ({ ...prev, [axis]: newVal }));
    // In a real implementation, this would update the hardware runtime
  };

  return (
    <div className="panel">
      <h3>Hardware Gate Panel</h3>
      <p style={{ fontSize: 12, color: "#94a3b8" }}>Simulate hardware state for calibration gating</p>
      <div className="grid2">
        {["A","B","C","D"].map(axis => (
          <button key={axis}
            className={simSwitches[axis] ? "danger" : ""}
            onClick={() => toggleSwitch(axis)}>
            Switch {axis}: {simSwitches[axis] ? "TRIGGERED" : "idle"}
          </button>
        ))}
      </div>
    </div>
  );
}
