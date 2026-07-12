"""运行第 10 章 Hall 换相偏置扫参与反向表场景。"""

from __future__ import annotations

import csv
import socket
import statistics
import subprocess
import sys
import xmlrpc.client
from pathlib import Path

MODEL = "ch10_hall_commutation"
NAMES = ("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_rad")
SCENARIOS = tuple({"name": f"offset_{offset}", "offset": offset, "direction": 1} for offset in range(6)) + (
    {"name": "reverse_table", "offset": 0, "direction": -1},
    {"name": "all_off", "offset": 0, "direction": 1, "enable": 0},
)


def main() -> int:
    root=Path(__file__).resolve().parents[1]; model=root/"models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs"; wave=root/"waveforms/10-hall-commutation"; assets=root/"assets/10-hall-commutation"; wave.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2): pass
    except OSError: print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
    times=[round(i*0.0002,10) for i in range(401)];server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);rows=[]
    try:
        try: server.plecs.close(MODEL)
        except Exception: pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":30.0,"phase_cmd":[0,0,0],"pole_pairs":1,"alignment_s":0.02,"start_frequency_Hz":5.0,"end_frequency_Hz":25.0,"ramp_duration_s":0.2,"sequence_direction":1,"hall_offset_rad":0.0,"commutation_offset_steps":scenario["offset"],"table_direction":scenario["direction"],"hall_enable":scenario.get("enable",1)},"SolverOpts":{"OutputTimes":times}});values=result["Values"]
            if len(values)!=15: raise RuntimeError(f"signals={len(values)}")
            data={name:list(value) for name,value in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"])
            columns=("time_s",*NAMES)
            with (wave/f"plecs_{scenario['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(columns)
                for i in range(len(times)):writer.writerow(data[column][i] for column in columns)
            peak=max(abs(v) for phase in (data["ia_A"],data["ib_A"],data["ic_A"]) for v in phase)
            rows.append({"scenario":scenario["name"],"offset_steps":scenario["offset"],"table_direction":scenario["direction"],"final_speed_rad_s":data["speed_rad_s"][-1],"mean_torque_Nm":statistics.fmean(data["torque_Nm"]),"positive_torque_fraction":sum(v>0 for v in data["torque_Nm"])/len(times),"peak_phase_current_A":peak,"result":"MEASURED"})
            if scenario["name"]=="offset_0":
                capture=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern",f"*{MODEL}/Scope*","-OutputPath",str(assets/"plecs_scope_correct_hall.png")],text=True,capture_output=True)
                if capture.returncode:raise RuntimeError(capture.stderr)
    finally:
        try:server.plecs.close(MODEL)
        except Exception:pass
    by_name={str(row["scenario"]):row for row in rows};correct=by_name["offset_0"]
    by_name["offset_0"]["result"]="PASS" if float(correct["final_speed_rad_s"])>60 and float(correct["mean_torque_Nm"])>0.8 and float(correct["peak_phase_current_A"])<30 else "FAIL"
    wrong=by_name["offset_1"];by_name["offset_1"]["result"]="PASS" if float(wrong["final_speed_rad_s"])<30 and float(wrong["mean_torque_Nm"])<0 and float(wrong["peak_phase_current_A"])>50 else "FAIL"
    for name in ("offset_2","offset_3","offset_4"):
        row=by_name[name];row["result"]="PASS" if float(row["mean_torque_Nm"])<-1 else "FAIL"
    row=by_name["offset_5"];row["result"]="PASS" if 0<float(row["mean_torque_Nm"])<float(correct["mean_torque_Nm"]) else "FAIL"
    row=by_name["reverse_table"];row["result"]="PASS" if abs(float(row["final_speed_rad_s"]))<5 and float(row["mean_torque_Nm"])<0 and float(row["peak_phase_current_A"])>50 else "FAIL"
    row=by_name["all_off"];row["result"]="PASS" if abs(float(row["mean_torque_Nm"]))<1e-12 and float(row["peak_phase_current_A"])<1e-12 else "FAIL"
    with (wave/"plecs_hall_commutation_summary.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 10 章 Hall 换相与安装偏置 PLECS 报告","","| 场景 | 偏置/60°步 | 表方向 | 末值速度/rad/s | 平均转矩/N m | 正转矩占比 | 峰值相电流/A | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:lines.append("| {scenario} | {offset_steps} | {table_direction} | {final_speed_rad_s:.3f} | {mean_torque_Nm:.3f} | {positive_torque_fraction:.3f} | {peak_phase_current_A:.3f} | {result} |".format(**row))
    (root/"reports/10-hall-commutation-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline="")
    passed=sum(row["result"]=="PASS" for row in rows);print(f"Generated chapter 10 PLECS Hall commutation evidence. scenarios=8 pass={passed} time_points=401 signals=15 best_offset=0")
    return 0 if passed==8 else 1


if __name__=="__main__":raise SystemExit(main())
