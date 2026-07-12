"""运行第 11 章 PWM duty 与 deadtime 场景。"""

from __future__ import annotations
import csv,socket,statistics,subprocess,sys,xmlrpc.client
from pathlib import Path

MODEL="ch11_pwm_deadtime";NAMES=("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_rad")
SCENARIOS=({"name":"duty_025","duty":0.25,"deadtime":2e-6},{"name":"duty_050","duty":0.50,"deadtime":2e-6},{"name":"duty_075","duty":0.75,"deadtime":2e-6},{"name":"zero_deadtime","duty":0.50,"deadtime":0.0},{"name":"large_deadtime","duty":0.50,"deadtime":15e-6})

def main()->int:
    root=Path(__file__).resolve().parents[1];model=root/"models/plecs/ch11_pwm_deadtime/ch11_pwm_deadtime.plecs";wave=root/"waveforms/11-pwm-deadtime";assets=root/"assets/11-pwm-deadtime";wave.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2):pass
    except OSError:print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
    times=[round(i*2e-6,10) for i in range(25001)];server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);rows=[]
    try:
        try:server.plecs.close(MODEL)
        except Exception:pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":30.0,"phase_cmd":[0,0,0],"pole_pairs":1,"alignment_s":0.02,"start_frequency_Hz":5.0,"end_frequency_Hz":25.0,"ramp_duration_s":0.2,"sequence_direction":1,"hall_offset_rad":0.0,"commutation_offset_steps":0,"table_direction":1,"hall_enable":1,"pwm_frequency_Hz":10000.0,"pwm_duty":scenario["duty"],"deadtime_s":scenario["deadtime"]},"SolverOpts":{"OutputTimes":times}});values=result["Values"]
            if len(values)!=15:raise RuntimeError(f"signals={len(values)}")
            data={name:list(value) for name,value in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"]);columns=("time_s",*NAMES)
            with (wave/f"plecs_{scenario['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(columns)
                for i in range(len(times)):writer.writerow(data[column][i] for column in columns)
            effective=3*sum(v>0.5 for name in ("cmd_a","cmd_b","cmd_c") for v in data[name])/(3*len(times));all_off=sum(abs(a)<0.5 and abs(b)<0.5 and abs(c)<0.5 for a,b,c in zip(data["cmd_a"],data["cmd_b"],data["cmd_c"],strict=True))/len(times);peak=max(abs(v) for name in ("ia_A","ib_A","ic_A") for v in data[name])
            rows.append({"scenario":scenario["name"],"command_duty":scenario["duty"],"deadtime_us":scenario["deadtime"]*1e6,"effective_high_duty":effective,"all_off_fraction":all_off,"final_speed_rad_s":data["speed_rad_s"][-1],"mean_torque_Nm":statistics.fmean(data["torque_Nm"]),"peak_phase_current_A":peak,"result":"MEASURED"})
            if scenario["name"]=="duty_050":
                cap=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern",f"*{MODEL}/Scope*","-OutputPath",str(assets/"plecs_scope_pwm_50.png")],text=True,capture_output=True)
                if cap.returncode:raise RuntimeError(cap.stderr)
    finally:
        try:server.plecs.close(MODEL)
        except Exception:pass
    by={str(row["scenario"]):row for row in rows}
    expected={"duty_025":0.23,"duty_050":0.48,"duty_075":0.73}
    for name,target in expected.items():by[name]["result"]="PASS" if abs(float(by[name]["effective_high_duty"])-target)<0.02 else "FAIL"
    ordered=float(by["duty_025"]["final_speed_rad_s"])<float(by["duty_050"]["final_speed_rad_s"])<float(by["duty_075"]["final_speed_rad_s"])
    if not ordered:
        for name in expected:by[name]["result"]="FAIL"
    by["zero_deadtime"]["result"]="PASS" if float(by["zero_deadtime"]["effective_high_duty"])>float(by["duty_050"]["effective_high_duty"]) and float(by["zero_deadtime"]["final_speed_rad_s"])>float(by["duty_050"]["final_speed_rad_s"]) else "FAIL"
    by["large_deadtime"]["result"]="PASS" if float(by["large_deadtime"]["effective_high_duty"])<0.40 and float(by["large_deadtime"]["final_speed_rad_s"])<float(by["duty_050"]["final_speed_rad_s"]) else "FAIL"
    with (wave/"plecs_pwm_summary.csv").open("w",encoding="utf-8",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 11 章 PWM duty 与 deadtime PLECS 报告","","| 场景 | 命令 duty | deadtime/us | 实测高侧 duty | 末值速度/rad/s | 平均转矩/N m | 峰值相电流/A | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:lines.append("| {scenario} | {command_duty:.2f} | {deadtime_us:.1f} | {effective_high_duty:.4f} | {final_speed_rad_s:.3f} | {mean_torque_Nm:.3f} | {peak_phase_current_A:.3f} | {result} |".format(**row))
    (root/"reports/11-pwm-deadtime-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline="")
    passed=sum(row["result"]=="PASS" for row in rows);print(f"Generated chapter 11 PLECS PWM evidence. scenarios=5 pass={passed} time_points=25001 signals=15")
    return 0 if passed==5 else 1

if __name__=="__main__":raise SystemExit(main())
