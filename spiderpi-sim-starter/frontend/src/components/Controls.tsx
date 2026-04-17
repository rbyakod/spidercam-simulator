import { SpiderState } from "../types";
export function Controls({ state, jog, runPath, stop, estop, resetEstop }:{
  state: SpiderState | null;
  jog: (dx:number,dy:number,dz:number,speed?:number)=>void;
  runPath: (name:string, opts?:Record<string,number>)=>void;
  stop: ()=>void;
  estop: ()=>void;
  resetEstop: ()=>void;
}) {
  if (!state) return <div className="panel">Loading controls...</div>;
  return (
    <div className="panel">
      <h3>Controls</h3>
      <div className="grid2">
        <button onClick={() => jog(0,-0.1,0)}>Forward</button>
        <button onClick={() => jog(0,0.1,0)}>Back</button>
        <button onClick={() => jog(-0.1,0,0)}>Left</button>
        <button onClick={() => jog(0.1,0,0)}>Right</button>
        <button onClick={() => jog(0,0,0.08)}>Down</button>
        <button onClick={() => jog(0,0,-0.08)}>Up</button>
      </div>
      <div className="grid2">
        <button onClick={() => runPath('square', { size:0.8, z:state.target.z, speed:0.35 })}>Square</button>
        <button onClick={() => runPath('circle', { radius:0.45, z:state.target.z, speed:0.35 })}>Circle</button>
      </div>
      <div className="grid2">
        <button onClick={stop}>Stop</button>
        <button className="danger" onClick={estop}>E-STOP</button>
      </div>
      <button className="warn" onClick={resetEstop}>Reset E-Stop</button>
    </div>
  );
}
