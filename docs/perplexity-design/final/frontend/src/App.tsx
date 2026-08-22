import React, { Suspense } from 'react';
import { useSpiderSocket } from './useSpiderSocket';
import SpiderScene from './SpiderScene';
import Telemetry from './Telemetry';
import TopMap from './TopMap';
import Joystick from './Joystick';
import SpoolWidget from './SpoolWidget';
import PhysicsPanel from './PhysicsPanel';
import Controls from './Controls';
import CalibrationPanel from './CalibrationPanel';
import HomingPanel from './HomingPanel';
import FrameSizingPanel from './FrameSizingPanel';
import ProfileSelector from './ProfileSelector';
import ProfileManager from './ProfileManager';
import CalibrationWizard from './CalibrationWizard';
import HardwareGatePanel from './HardwareGatePanel';

export default function App() {
  const { telemetry, connected } = useSpiderSocket();

  return (
    <div className="app">
      <aside className="sidebar">
        <Telemetry telemetry={telemetry} connected={connected} />
        <HomingPanel homing={telemetry?.homing} />
        <CalibrationWizard />
        <CalibrationPanel />
        <PhysicsPanel />
        <Joystick />
        <Controls />
        <ProfileSelector />
        <ProfileManager />
        <FrameSizingPanel />
        <HardwareGatePanel />
        <SpoolWidget lengths={telemetry?.cable_lengths ?? [0,0,0,0]} />
        <TopMap telemetry={telemetry} />
      </aside>
      <main className="main">
        <div className="canvas-area">
          <Suspense fallback={<div style={{color:'#fff',padding:20}}>Loading 3D...</div>}>
            <SpiderScene telemetry={telemetry} />
          </Suspense>
        </div>
      </main>
    </div>
  );
}
