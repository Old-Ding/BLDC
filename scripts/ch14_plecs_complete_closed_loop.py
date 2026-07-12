"""运行第 14 章完整 Hall 六步闭环验收场景。"""
from __future__ import annotations
import csv,socket,statistics,subprocess,sys,xmlrpc.client
from pathlib import Path

MODEL="ch14_complete_hall_closed_loop";NAMES=("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_rad","hall_speed_feedback_rad_s")
SCENARIOS=({"name":"zero_speed_start","initial":0.0,"before":60.0,"after":60.0,"target_step":1.0,"load_after":0.0,"load_step":1.0,"invalid_start":1.0,"invalid_end":1.0},{"name":"target_step","initial":30.0,"before":45.0,"after":60.0,"target_step":0.12,"load_after":0.0,"load_step":1.0,"invalid_start":1.0,"invalid_end":1.0},{"name":"load_step","initial":30.0,"before":60.0,"after":60.0,"target_step":1.0,"load_after":3.0,"load_step":0.15,"invalid_start":1.0,"invalid_end":1.0},{"name":"invalid_hall","initial":30.0,"before":60.0,"after":60.0,"target_step":1.0,"load_after":0.0,"load_step":1.0,"invalid_start":0.12,"invalid_end":0.14},{"name":"overload","initial":30.0,"before":60.0,"after":60.0,"target_step":1.0,"load_after":12.0,"load_step":0.15,"invalid_start":1.0,"invalid_end":1.0})

def moving_duty(a,b,c,window=100):
    pos=[(x>0.5)+(y>0.5)+(z>0.5) for x,y,z in zip(a,b,c,strict=True)];prefix=[0]
    for v in pos:prefix.append(prefix[-1]+v)
    return [(prefix[i+1]-prefix[max(0,i-window+1)])/(i-max(0,i-window+1)+1) for i in range(len(pos))]

def main()->int:
    root=Path(__file__).resolve().parents[1];model=root/"models/plecs/ch14_complete_hall_closed_loop/ch14_complete_hall_closed_loop.plecs";wave=root/"waveforms/14-complete-hall-closed-loop";assets=root/"assets/14-complete-hall-closed-loop";wave.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2):pass
    except OSError:print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
    times=[round(i*1e-5,10) for i in range(50001)];server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);rows=[]
    try:
        try:server.plecs.close(MODEL)
        except Exception:pass
        server.plecs.load(str(model))
        for sc in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":sc["initial"],"phase_cmd":[0,0,0],"pole_pairs":1,"alignment_s":0.02,"start_frequency_Hz":5.0,"end_frequency_Hz":25.0,"ramp_duration_s":0.2,"sequence_direction":1,"hall_offset_rad":0.0,"commutation_offset_steps":0,"table_direction":1,"hall_enable":1,"pwm_frequency_Hz":10000.0,"pwm_duty":0.5,"deadtime_s":2e-6,"speed_target_before_rad_s":sc["before"],"speed_target_after_rad_s":sc["after"],"speed_target_step_s":sc["target_step"],"speed_kp":0.008,"speed_ki":0.8,"duty_min":0.1,"duty_max":0.9,"antiwindup_enable":1,"load_before_Nm":0.0,"load_after_Nm":sc["load_after"],"load_step_time_s":sc["load_step"],"hall_invalid_start_s":sc["invalid_start"],"hall_invalid_end_s":sc["invalid_end"],"hall_speed_alpha":0.25,"hall_speed_timeout_s":0.05},"SolverOpts":{"OutputTimes":times}});values=result["Values"]
            if len(values)!=16:raise RuntimeError(f"signals={len(values)}")
            data={name:list(value) for name,value in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"]);target=[sc["before"] if t<sc["target_step"] else sc["after"] for t in data["time_s"]];load=[0.0 if t<sc["load_step"] else sc["load_after"] for t in data["time_s"]];invalid=[1 if sc["invalid_start"]<=t<sc["invalid_end"] else 0 for t in data["time_s"]];duty=moving_duty(data["cmd_a"],data["cmd_b"],data["cmd_c"]);data.update(speed_target_rad_s=target,load_torque_Nm=load,hall_invalid=invalid,effective_duty=duty)
            cols=("time_s","speed_target_rad_s","load_torque_Nm","hall_invalid","effective_duty",*NAMES)
            with (wave/f"plecs_{sc['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(cols)
                for i in range(len(times)):writer.writerow(data[col][i] for col in cols)
            tail=5000;tail_error=statistics.fmean(abs(t-s) for t,s in zip(target[-tail:],data["speed_rad_s"][-tail:],strict=True));hall_valid=[i for i in range(len(times)-tail,len(times)) if abs(data["hall_speed_feedback_rad_s"][i])>1e-9];hall_tail_bias=abs(statistics.fmean(data["speed_rad_s"][i] for i in hall_valid)-statistics.fmean(data["hall_speed_feedback_rad_s"][i] for i in hall_valid)) if hall_valid else float("inf");post_load=[i for i,t in enumerate(data["time_s"]) if t>=sc["load_step"]] if sc["load_step"]<1 else [];high_sat=sum(duty[i]>0.85 for i in post_load)/len(post_load) if post_load else 0;fault_idx=[i for i,v in enumerate(invalid) if v];fault_off=sum(abs(data["cmd_a"][i])<0.5 and abs(data["cmd_b"][i])<0.5 and abs(data["cmd_c"][i])<0.5 for i in fault_idx)/len(fault_idx) if fault_idx else 0;cross=next((data["time_s"][i] for i,v in enumerate(data["speed_rad_s"]) if v>=50),-1)
            rows.append({"scenario":sc["name"],"final_speed_rad_s":data["speed_rad_s"][-1],"tail_abs_error_rad_s":tail_error,"hall_tail_bias_rad_s":hall_tail_bias,"minimum_speed_rad_s":min(data["speed_rad_s"]),"rise_to_50_s":cross,"post_load_high_saturation_fraction":high_sat,"fault_all_off_fraction":fault_off,"peak_phase_current_A":max(abs(v) for name in ("ia_A","ib_A","ic_A") for v in data[name]),"result":"MEASURED"})
            if sc["name"]=="zero_speed_start":
                cap=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern",f"*{MODEL}/Scope*","-OutputPath",str(assets/"plecs_scope_complete_startup.png")],text=True,capture_output=True)
                if cap.returncode:raise RuntimeError(cap.stderr)
    finally:
        try:server.plecs.close(MODEL)
        except Exception:pass
    by={str(row["scenario"]):row for row in rows};row=by["zero_speed_start"];row["result"]="PASS" if 55<float(row["final_speed_rad_s"])<62 and float(row["tail_abs_error_rad_s"])<3 and float(row["hall_tail_bias_rad_s"])<1.5 and 0<float(row["rise_to_50_s"])<0.03 else "FAIL"
    row=by["target_step"];row["result"]="PASS" if float(row["tail_abs_error_rad_s"])<3 and float(row["hall_tail_bias_rad_s"])<1.5 and 57<float(row["final_speed_rad_s"])<65 else "FAIL"
    row=by["load_step"];row["result"]="PASS" if float(row["tail_abs_error_rad_s"])<8 and float(row["hall_tail_bias_rad_s"])<1.5 and float(row["post_load_high_saturation_fraction"])>0.5 and float(row["final_speed_rad_s"])>45 else "FAIL"
    row=by["invalid_hall"];row["result"]="PASS" if float(row["fault_all_off_fraction"])>0.999 and float(row["tail_abs_error_rad_s"])<3 and float(row["hall_tail_bias_rad_s"])<1.5 and float(row["final_speed_rad_s"])>55 else "FAIL"
    row=by["overload"];row["result"]="PASS" if float(row["final_speed_rad_s"])<55 and float(row["tail_abs_error_rad_s"])>15 and float(row["hall_tail_bias_rad_s"])<1.5 and float(row["post_load_high_saturation_fraction"])>0.85 else "FAIL"
    with (wave/"plecs_closed_loop_summary.csv").open("w",encoding="utf-8",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 14 章完整 Hall 六步闭环 PLECS 报告","","| 场景 | 末值速度/rad/s | 尾段目标误差/rad/s | Hall 尾段均值偏差/rad/s | 50 rad/s 上升时间/s | 负载后高限幅占比 | 故障全关占比 | 峰值相电流/A | 结果 |","|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:lines.append("| {scenario} | {final_speed_rad_s:.3f} | {tail_abs_error_rad_s:.3f} | {hall_tail_bias_rad_s:.3f} | {rise_to_50_s:.5f} | {post_load_high_saturation_fraction:.3f} | {fault_all_off_fraction:.3f} | {peak_phase_current_A:.3f} | {result} |".format(**row))
    (root/"reports/14-complete-hall-closed-loop-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline="");passed=sum(row["result"]=="PASS" for row in rows);print(f"Generated chapter 14 PLECS closed-loop evidence. scenarios=5 pass={passed} time_points=50001 signals=16")
    return 0 if passed==5 else 1

if __name__=="__main__":raise SystemExit(main())
