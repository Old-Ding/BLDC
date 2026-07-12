"""运行第 13 章速度 PI、负载阶跃和抗饱和场景。"""
from __future__ import annotations
import csv,math,socket,statistics,subprocess,sys,xmlrpc.client
from pathlib import Path

MODEL="ch13_speed_pi";NAMES=("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_rad")
SCENARIOS=({"name":"speed_step_aw","before":45.0,"after":60.0,"step":0.08,"load_after":0.0,"load_step":1.0,"aw":1},{"name":"load_step_aw","before":60.0,"after":60.0,"step":1.0,"load_after":3.0,"load_step":0.10,"aw":1},{"name":"recovery_aw","before":200.0,"after":40.0,"step":0.10,"load_after":0.0,"load_step":1.0,"aw":1},{"name":"recovery_no_aw","before":200.0,"after":40.0,"step":0.10,"load_after":0.0,"load_step":1.0,"aw":0})

def moving_duty(a:list[float],b:list[float],c:list[float],window:int=100)->list[float]:
    positive=[(x>0.5)+(y>0.5)+(z>0.5) for x,y,z in zip(a,b,c,strict=True)];prefix=[0]
    for value in positive:prefix.append(prefix[-1]+value)
    output=[]
    for i in range(len(positive)):
        left=max(0,i-window+1);output.append(3*(prefix[i+1]-prefix[left])/(3*(i-left+1)))
    return output

def main()->int:
    root=Path(__file__).resolve().parents[1];model=root/"models/plecs/ch13_speed_pi/ch13_speed_pi.plecs";wave=root/"waveforms/13-speed-pi";assets=root/"assets/13-speed-pi";wave.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2):pass
    except OSError:print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
    times=[round(i*1e-5,10) for i in range(20001)];server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);rows=[]
    try:
        try:server.plecs.close(MODEL)
        except Exception:pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":48.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":30.0,"phase_cmd":[0,0,0],"pole_pairs":1,"alignment_s":0.02,"start_frequency_Hz":5.0,"end_frequency_Hz":25.0,"ramp_duration_s":0.2,"sequence_direction":1,"hall_offset_rad":0.0,"commutation_offset_steps":0,"table_direction":1,"hall_enable":1,"pwm_frequency_Hz":10000.0,"pwm_duty":0.5,"deadtime_s":2e-6,"speed_target_before_rad_s":scenario["before"],"speed_target_after_rad_s":scenario["after"],"speed_target_step_s":scenario["step"],"speed_kp":0.008,"speed_ki":0.8,"duty_min":0.1,"duty_max":0.9,"antiwindup_enable":scenario["aw"],"load_before_Nm":0.0,"load_after_Nm":scenario["load_after"],"load_step_time_s":scenario["load_step"]},"SolverOpts":{"OutputTimes":times}});values=result["Values"]
            if len(values)!=15:raise RuntimeError(f"signals={len(values)}")
            data={name:list(value) for name,value in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"]);target_values=[scenario["before"] if t<scenario["step"] else scenario["after"] for t in data["time_s"]];load=[0.0 if t<scenario["load_step"] else scenario["load_after"] for t in data["time_s"]];duty=moving_duty(data["cmd_a"],data["cmd_b"],data["cmd_c"]);data.update(speed_target_rad_s=target_values,load_torque_Nm=load,effective_duty=duty)
            columns=("time_s","speed_target_rad_s","load_torque_Nm","effective_duty",*NAMES)
            with (wave/f"plecs_{scenario['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(columns)
                for i in range(len(times)):writer.writerow(data[column][i] for column in columns)
            tail=2000;tail_error=statistics.fmean(abs(t-s) for t,s in zip(target_values[-tail:],data["speed_rad_s"][-tail:],strict=True));post=[i for i,t in enumerate(data["time_s"]) if t>=scenario["step"]];sat_after=sum(duty[i]>0.85 for i in post)/len(post) if post else 0;peak=max(data["speed_rad_s"]);rows.append({"scenario":scenario["name"],"antiwindup":scenario["aw"],"final_speed_rad_s":data["speed_rad_s"][-1],"tail_abs_error_rad_s":tail_error,"peak_speed_rad_s":peak,"post_step_high_saturation_fraction":sat_after,"peak_phase_current_A":max(abs(v) for name in ("ia_A","ib_A","ic_A") for v in data[name]),"result":"MEASURED"})
            if scenario["name"]=="speed_step_aw":
                cap=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern",f"*{MODEL}/Scope*","-OutputPath",str(assets/"plecs_scope_speed_pi.png")],text=True,capture_output=True)
                if cap.returncode:raise RuntimeError(cap.stderr)
    finally:
        try:server.plecs.close(MODEL)
        except Exception:pass
    by={str(row["scenario"]):row for row in rows};row=by["speed_step_aw"];row["result"]="PASS" if float(row["tail_abs_error_rad_s"])<3 and 55<float(row["final_speed_rad_s"])<62 and float(row["post_step_high_saturation_fraction"])<0.05 else "FAIL"
    row=by["load_step_aw"];row["result"]="PASS" if float(row["tail_abs_error_rad_s"])<8 and float(row["final_speed_rad_s"])>50 and float(row["peak_phase_current_A"])>float(by["speed_step_aw"]["peak_phase_current_A"]) else "FAIL"
    aw=by["recovery_aw"];aw["result"]="PASS" if float(aw["tail_abs_error_rad_s"])<10 and float(aw["post_step_high_saturation_fraction"])<0.01 else "FAIL"
    noaw=by["recovery_no_aw"];noaw["result"]="PASS" if float(noaw["tail_abs_error_rad_s"])>2*float(aw["tail_abs_error_rad_s"]) and float(noaw["post_step_high_saturation_fraction"])>0.5 else "FAIL"
    with (wave/"plecs_speed_pi_summary.csv").open("w",encoding="utf-8",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 13 章速度 PI 与抗饱和 PLECS 报告","","| 场景 | 抗饱和 | 末值速度/rad/s | 尾段绝对误差/rad/s | 峰值速度/rad/s | 降目标后高限幅占比 | 峰值相电流/A | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:lines.append("| {scenario} | {antiwindup} | {final_speed_rad_s:.3f} | {tail_abs_error_rad_s:.3f} | {peak_speed_rad_s:.3f} | {post_step_high_saturation_fraction:.4f} | {peak_phase_current_A:.3f} | {result} |".format(**row))
    (root/"reports/13-speed-pi-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline="");passed=sum(row["result"]=="PASS" for row in rows);print(f"Generated chapter 13 PLECS speed-PI evidence. scenarios=4 pass={passed} time_points=20001 signals=15")
    return 0 if passed==4 else 1

if __name__=="__main__":raise SystemExit(main())
