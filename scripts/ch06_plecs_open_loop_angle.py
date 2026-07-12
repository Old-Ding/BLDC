"""运行第 06 章慢/快开环电角频率 PLECS 场景。"""

from __future__ import annotations

import csv, math, socket, statistics, subprocess, sys, xmlrpc.client
from pathlib import Path

MODEL="ch06_open_loop_angle"; SCENARIOS=(("slow_field",0.005),("fast_field",0.001))
NAMES=("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V")
STEP_BY_STATE={(1,-1,0):0,(1,0,-1):1,(0,1,-1):2,(-1,1,0):3,(-1,0,1):4,(0,-1,1):5}

def main()->int:
 root=Path(__file__).resolve().parents[1]; model=root/"models/plecs/ch06_open_loop_angle/ch06_open_loop_angle.plecs"; wave=root/"waveforms/06-open-loop-angle"; assets=root/"assets/06-open-loop-angle"; wave.mkdir(parents=True,exist_ok=True); assets.mkdir(parents=True,exist_ok=True)
 try:
  with socket.create_connection(("localhost",1080),timeout=2):pass
 except OSError: print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
 server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);times=[round(i*0.0001,10) for i in range(601)];rows=[]
 try:
  try:server.plecs.close(MODEL)
  except Exception:pass
  server.plecs.load(str(model))
  for name,period in SCENARIOS:
   result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":0.0,"phase_cmd":[0,0,0],"step_period_s":period,"sequence_direction":1},"SolverOpts":{"OutputTimes":times}}); values=result["Values"]
   data={k:list(v) for k,v in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"]);steps=[STEP_BY_STATE[tuple(round(data[c][i]) for c in ("cmd_a","cmd_b","cmd_c"))] for i in range(len(times))];data["command_step"]=steps
   cols=("time_s","command_step",*NAMES)
   with (wave/f"plecs_{name}.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f,lineterminator="\r\n");w.writerow(cols)
    for i in range(len(times)):w.writerow(data[c][i] for c in cols)
   f_e=1/(6*period); sync=2*math.pi*f_e; final=data["speed_rad_s"][-1];mean_t=statistics.fmean(data["torque_Nm"]);positive=sum(v>0 for v in data["torque_Nm"])/len(times)
   passed=(final>30 and mean_t>0.5) if name=="slow_field" else (abs(final)<10 and abs(mean_t)<0.5)
   rows.append({"scenario":name,"step_period_ms":period*1e3,"electrical_frequency_Hz":f_e,"synchronous_speed_rad_s":sync,"final_speed_rad_s":final,"mean_torque_Nm":mean_t,"positive_torque_fraction":positive,"result":"PASS" if passed else "FAIL"})
   if name=="slow_field":
    cp=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern","*ch06_open_loop_angle/Scope*","-OutputPath",str(assets/"plecs_scope_slow_field.png")],text=True,capture_output=True)
    if cp.returncode:raise RuntimeError(cp.stderr)
 finally:
  try:server.plecs.close(MODEL)
  except Exception:pass
 with (wave/"plecs_open_loop_summary.csv").open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=rows[0].keys(),lineterminator="\r\n");w.writeheader();w.writerows(rows)
 report=["# 第 06 章开环电角频率 PLECS 报告","","| 场景 | step/ms | 电频率/Hz | 同步速度/rad/s | 末值速度/rad/s | 平均转矩/Nm | 正转矩占比 | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
 for r in rows:report.append("| {scenario} | {step_period_ms:.3f} | {electrical_frequency_Hz:.3f} | {synchronous_speed_rad_s:.3f} | {final_speed_rad_s:.3f} | {mean_torque_Nm:.3f} | {positive_torque_fraction:.3f} | {result} |".format(**r))
 (root/"reports/06-open-loop-angle-test_report.md").write_text("\r\n".join(report)+"\r\n",encoding="utf-8",newline="");passed=sum(r["result"]=="PASS" for r in rows);print(f"Generated chapter 06 PLECS open-loop evidence. scenarios=2 pass={passed} time_points=601 signals=14");return 0 if passed==2 else 1
if __name__=="__main__":raise SystemExit(main())
