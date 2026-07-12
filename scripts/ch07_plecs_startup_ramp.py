"""运行第 07 章定位+频率斜坡与直接高频启动场景。"""

from __future__ import annotations

import csv, math, socket, statistics, subprocess, sys, xmlrpc.client
from pathlib import Path

MODEL = "ch07_startup_ramp"
NAMES = ("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_raw_rad")
SCENARIOS = (
    {"name":"ramp_start","alignment_s":0.02,"f0":5.0,"f1":33.333333,"ramp_s":0.2},
    {"name":"direct_fast","alignment_s":0.0,"f0":166.666667,"f1":166.666667,"ramp_s":0.0},
)


def command_phase(t: float, s: dict[str, float | str]) -> tuple[float, float]:
    run_t = t - float(s["alignment_s"])
    if run_t <= 0:
        return 0.0, 0.0
    f0, f1, ramp = float(s["f0"]), float(s["f1"]), float(s["ramp_s"])
    if ramp <= 0:
        return 2*math.pi*f1*run_t, f1
    if run_t < ramp:
        k=(f1-f0)/ramp
        return 2*math.pi*(f0*run_t+0.5*k*run_t*run_t), f0+k*run_t
    return 2*math.pi*(0.5*(f0+f1)*ramp+f1*(run_t-ramp)), f1


def unwrap(raw: list[float]) -> list[float]:
    out=[raw[0]]; offset=0.0
    for previous,current in zip(raw[:-1],raw[1:],strict=True):
        delta=current-previous
        if delta < -math.pi: offset += 2*math.pi
        elif delta > math.pi: offset -= 2*math.pi
        out.append(current+offset)
    return out


def main() -> int:
    root=Path(__file__).resolve().parents[1]; model=root/"models/plecs/ch07_startup_ramp/ch07_startup_ramp.plecs"; wave=root/"waveforms/07-startup-ramp"; assets=root/"assets/07-startup-ramp"; wave.mkdir(parents=True,exist_ok=True); assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2): pass
    except OSError: print("PLECS_RPC_NOT_READY",file=sys.stderr); return 2
    server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True); times=[round(i*0.0005,10) for i in range(601)]; rows=[]
    try:
        try: server.plecs.close(MODEL)
        except Exception: pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":0.0,"phase_cmd":[0,0,0],"pole_pairs":1,"alignment_s":scenario["alignment_s"],"start_frequency_Hz":scenario["f0"],"end_frequency_Hz":scenario["f1"],"ramp_duration_s":scenario["ramp_s"],"sequence_direction":1},"SolverOpts":{"OutputTimes":times}}); values=result["Values"]
            if len(values)!=15: raise RuntimeError(f"signals={len(values)}")
            data={key:list(value) for key,value in zip(NAMES,values,strict=True)}; data["time_s"]=list(result["Time"]); rotor=unwrap(data["mechanical_angle_raw_rad"]); phases=[command_phase(t,scenario) for t in data["time_s"]]; command=[p[0] for p in phases]; frequency=[p[1] for p in phases]; error=[math.atan2(math.sin(c-r),math.cos(c-r)) for c,r in zip(command,rotor,strict=True)]; data.update(rotor_angle_unwrapped_rad=rotor,command_electrical_angle_rad=command,command_frequency_Hz=frequency,phase_error_rad=error)
            columns=("time_s","command_frequency_Hz","command_electrical_angle_rad","mechanical_angle_raw_rad","rotor_angle_unwrapped_rad","phase_error_rad",*NAMES[:-1])
            with (wave/f"plecs_{scenario['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(columns)
                for i in range(len(times)): writer.writerow(data[column][i] for column in columns)
            tail=100; final_speed=data["speed_rad_s"][-1]; tail_torque=statistics.fmean(data["torque_Nm"][-tail:]); tail_phase=statistics.fmean(abs(v) for v in error[-tail:]); peak_current=max(abs(v) for phase in (data["ia_A"],data["ib_A"],data["ic_A"]) for v in phase); passed=(final_speed>70 and tail_torque>1) if scenario["name"]=="ramp_start" else (abs(final_speed)<10 and abs(tail_torque)<1)
            rows.append({"scenario":scenario["name"],"final_command_frequency_Hz":frequency[-1],"synchronous_speed_rad_s":2*math.pi*frequency[-1],"final_speed_rad_s":final_speed,"tail_torque_Nm":tail_torque,"tail_abs_phase_error_rad":tail_phase,"peak_phase_current_A":peak_current,"result":"PASS" if passed else "FAIL"})
            if scenario["name"]=="ramp_start":
                cp=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern","*ch07_startup_ramp/Scope*","-OutputPath",str(assets/"plecs_scope_ramp_start.png")],text=True,capture_output=True)
                if cp.returncode: raise RuntimeError(cp.stderr)
    finally:
        try: server.plecs.close(MODEL)
        except Exception: pass
    with (wave/"plecs_startup_summary.csv").open("w",encoding="utf-8",newline="") as stream: writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 07 章定位与频率斜坡启动 PLECS 报告","","| 场景 | 最终电频率/Hz | 同步速度/rad/s | 末值速度/rad/s | 尾段转矩/Nm | 尾段绝对相差/rad | 峰值相电流/A | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows: lines.append("| {scenario} | {final_command_frequency_Hz:.3f} | {synchronous_speed_rad_s:.3f} | {final_speed_rad_s:.3f} | {tail_torque_Nm:.3f} | {tail_abs_phase_error_rad:.3f} | {peak_phase_current_A:.3f} | {result} |".format(**row))
    (root/"reports/07-startup-ramp-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline=""); passed=sum(row["result"]=="PASS" for row in rows); print(f"Generated chapter 07 PLECS startup evidence. scenarios=2 pass={passed} time_points=601 signals=15"); return 0 if passed==2 else 1


if __name__=="__main__": raise SystemExit(main())
