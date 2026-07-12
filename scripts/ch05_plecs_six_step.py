"""运行第 05 章正序、反序和全关六步 PLECS 场景。"""

from __future__ import annotations

import csv
import socket
import subprocess
import sys
import xmlrpc.client
from pathlib import Path


MODEL = "ch05_six_step_sequence"
SCENARIOS = (("forward", 0.001, 1), ("reverse", 0.001, -1), ("all_off", 0.0, 1))
NAMES = ("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V")
FORWARD = ((1,-1,0),(1,0,-1),(0,1,-1),(-1,1,0),(-1,0,1),(0,-1,1))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    model_path = root / "models/plecs/ch05_six_step_sequence/ch05_six_step_sequence.plecs"
    wave = root / "waveforms/05-six-step-sequence"; wave.mkdir(parents=True, exist_ok=True)
    assets = root / "assets/05-six-step-sequence"; assets.mkdir(parents=True, exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2): pass
    except OSError:
        print("PLECS_RPC_NOT_READY", file=sys.stderr); return 2
    server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True)
    times=[i*20e-6 for i in range(601)]
    rows=[]
    try:
        try: server.plecs.close(MODEL)
        except Exception: pass
        server.plecs.load(str(model_path))
        for name,period,direction in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":0.0,"phase_cmd":[0,0,0],"step_period_s":period,"sequence_direction":direction},"SolverOpts":{"OutputTimes":times}})
            values=result["Values"]
            if len(values)!=14: raise RuntimeError(f"signals={len(values)}")
            data={key:list(value) for key,value in zip(NAMES,values,strict=True)}; data["time_s"]=list(result["Time"])
            with (wave/f"plecs_{name}.csv").open("w",encoding="utf-8",newline="") as f:
                cols=("time_s",*NAMES); w=csv.writer(f,lineterminator="\r\n"); w.writerow(cols)
                for i in range(len(times)): w.writerow(data[c][i] for c in cols)
            observed=[]
            for a,b,c in zip(data["cmd_a"],data["cmd_b"],data["cmd_c"],strict=True):
                state=(round(a),round(b),round(c))
                if not observed or observed[-1]!=state: observed.append(state)
            expected=[(0,0,0)] if period<=0 else list(FORWARD if direction>0 else (FORWARD[0],*reversed(FORWARD[1:])))
            if name=="reverse": expected=list(FORWARD[i] for i in (0,5,4,3,2,1))
            sequence_ok=observed[:len(expected)]==expected
            kcl=max(abs(a+b+c) for a,b,c in zip(data["ia_A"],data["ib_A"],data["ic_A"],strict=True))
            valid=all(sorted(s)==[-1,0,1] for s in observed) if period>0 else observed==[(0,0,0)]
            passed=sequence_ok and valid and kcl<=1e-6
            rows.append({"scenario":name,"observed_states":";".join(" ".join(map(str,s)) for s in observed),"state_count":len(observed),"kcl_peak_A":kcl,"result":"PASS" if passed else "FAIL"})
            if name=="forward":
                cp=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern","*ch05_six_step_sequence/Scope*","-OutputPath",str(assets/"plecs_scope_forward_sequence.png")],text=True,capture_output=True)
                if cp.returncode: raise RuntimeError(cp.stderr); print(cp.stdout)
    finally:
        try: server.plecs.close(MODEL)
        except Exception: pass
    with (wave/"plecs_six_step_summary.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\r\n");w.writeheader();w.writerows(rows)
    report=["# 第 05 章六步序列 PLECS 报告","","| 场景 | 状态数 | KCL 峰值/A | 结果 |","|---|---:|---:|---|"]
    for r in rows: report.append(f"| {r['scenario']} | {r['state_count']} | {r['kcl_peak_A']:.3e} | {r['result']} |")
    (root/"reports/05-six-step-sequence-test_report.md").write_text("\r\n".join(report)+"\r\n",encoding="utf-8",newline="")
    passed=sum(r["result"]=="PASS" for r in rows); print(f"Generated chapter 05 PLECS six-step evidence. scenarios=3 pass={passed} time_points=601 signals=14")
    return 0 if passed==3 else 1


if __name__=="__main__": raise SystemExit(main())
