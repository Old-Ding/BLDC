"""运行第 12 章 Hall 边沿测速、滤波和超时场景。"""
from __future__ import annotations
import csv,math,socket,statistics,subprocess,sys,xmlrpc.client
from pathlib import Path

MODEL="ch12_hall_speed";NAMES=("ia_A","ib_A","ic_A","ea_V","eb_V","ec_V","speed_rad_s","torque_Nm","cmd_a","cmd_b","cmd_c","vab_V","vbc_V","vca_V","mechanical_angle_rad","hall_a","hall_b","hall_c","hall_valid")
SCENARIOS=({"name":"slow_25","speed":25.0},{"name":"medium_100","speed":100.0},{"name":"fast_400","speed":400.0},{"name":"reverse_100","speed":-100.0},{"name":"stopped_timeout","speed":0.0})
SEQUENCE=(5,1,3,2,6,4);TIMEOUT=0.05;ALPHA=0.25

def estimate(time:list[float],codes:list[int])->tuple[list[float],list[float],list[int],int]:
    raw=[];filtered=[];timeouts=[];last_code=codes[0];last_edge=None;raw_value=0.0;filter_value=0.0;edges=0
    for t,code in zip(time,codes,strict=True):
        if code!=last_code and code in SEQUENCE and last_code in SEQUENCE:
            delta=(SEQUENCE.index(code)-SEQUENCE.index(last_code))%6;direction=1 if delta==1 else -1 if delta==5 else 0
            if last_edge is not None and direction:
                raw_value=direction*(math.pi/3)/(t-last_edge);filter_value=raw_value if edges==1 else ALPHA*raw_value+(1-ALPHA)*filter_value
            last_edge=t;last_code=code;edges+=1
        timed_out=last_edge is None and t>=TIMEOUT or last_edge is not None and t-last_edge>=TIMEOUT
        if timed_out:raw_value=0.0;filter_value=0.0
        raw.append(raw_value);filtered.append(filter_value);timeouts.append(1 if timed_out else 0)
    return raw,filtered,timeouts,edges

def main()->int:
    root=Path(__file__).resolve().parents[1];model=root/"models/plecs/ch12_hall_speed/ch12_hall_speed.plecs";wave=root/"waveforms/12-hall-speed";assets=root/"assets/12-hall-speed";wave.mkdir(parents=True,exist_ok=True);assets.mkdir(parents=True,exist_ok=True)
    try:
        with socket.create_connection(("localhost",1080),timeout=2):pass
    except OSError:print("PLECS_RPC_NOT_READY",file=sys.stderr);return 2
    times=[round(i*0.0001,10) for i in range(2501)];server=xmlrpc.client.ServerProxy("http://localhost:1080/RPC2",allow_none=True);rows=[]
    try:
        try:server.plecs.close(MODEL)
        except Exception:pass
        server.plecs.load(str(model))
        for scenario in SCENARIOS:
            result=server.plecs.simulate(MODEL,{"ModelVars":{"Udc_V":300.0,"load_torque_Nm":0.0,"current_ref_A":0.0,"initial_speed_rad_s":scenario["speed"],"phase_cmd":[0,0,0],"pole_pairs":1,"hall_offset_rad":0.0,"force_invalid":0,"invalid_code":0},"SolverOpts":{"OutputTimes":times}});values=result["Values"]
            if len(values)!=19:raise RuntimeError(f"signals={len(values)}")
            data={name:list(value) for name,value in zip(NAMES,values,strict=True)};data["time_s"]=list(result["Time"]);codes=[(round(a)<<2)|(round(b)<<1)|round(c) for a,b,c in zip(data["hall_a"],data["hall_b"],data["hall_c"],strict=True)];raw,filt,timeout,edges=estimate(data["time_s"],codes);data.update(hall_code=codes,speed_raw_rad_s=raw,speed_filtered_rad_s=filt,timeout=timeout)
            columns=("time_s","mechanical_angle_rad","speed_rad_s","hall_a","hall_b","hall_c","hall_code","speed_raw_rad_s","speed_filtered_rad_s","timeout")
            with (wave/f"plecs_{scenario['name']}.csv").open("w",encoding="utf-8",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\r\n");writer.writerow(columns)
                for i in range(len(times)):writer.writerow(data[column][i] for column in columns)
            valid=[abs(v) for v in raw if abs(v)>1e-9];median=statistics.median(valid) if valid else 0.0;actual=abs(statistics.fmean(data["speed_rad_s"]));error=abs(median-actual)/actual if actual>1e-9 else 0.0;passed=(edges>=3 and error<0.03 and (median>0)==(scenario["speed"]>0)) if scenario["speed"]>0 else (edges>=3 and error<0.03 and any(v<0 for v in raw)) if scenario["speed"]<0 else (edges==0 and timeout[-1]==1 and raw[-1]==0)
            rows.append({"scenario":scenario["name"],"initial_speed_rad_s":scenario["speed"],"edge_count":edges,"median_raw_speed_rad_s":statistics.median([v for v in raw if abs(v)>1e-9]) if valid else 0.0,"mean_actual_abs_speed_rad_s":actual,"relative_error":error,"timeout_final":timeout[-1],"result":"PASS" if passed else "FAIL"})
            if scenario["name"]=="fast_400":
                cap=subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(root/"scripts/capture_plecs_window.ps1"),"-TitlePattern",f"*{MODEL}/Scope*","-OutputPath",str(assets/"plecs_scope_hall_edges_fast.png")],text=True,capture_output=True)
                if cap.returncode:raise RuntimeError(cap.stderr)
    finally:
        try:server.plecs.close(MODEL)
        except Exception:pass
    with (wave/"plecs_hall_speed_summary.csv").open("w",encoding="utf-8",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=rows[0].keys(),lineterminator="\r\n");writer.writeheader();writer.writerows(rows)
    lines=["# 第 12 章 Hall 边沿测速 PLECS 报告","","| 场景 | 初速/rad/s | 边沿数 | 原始估算中位数/rad/s | 实际速度绝对均值/rad/s | 相对误差 | 最终超时 | 结果 |","|---|---:|---:|---:|---:|---:|---:|---|"]
    for row in rows:lines.append("| {scenario} | {initial_speed_rad_s:.1f} | {edge_count} | {median_raw_speed_rad_s:.3f} | {mean_actual_abs_speed_rad_s:.3f} | {relative_error:.4f} | {timeout_final} | {result} |".format(**row))
    (root/"reports/12-hall-speed-test_report.md").write_text("\r\n".join(lines)+"\r\n",encoding="utf-8",newline="");passed=sum(row["result"]=="PASS" for row in rows);print(f"Generated chapter 12 PLECS Hall-speed evidence. scenarios=5 pass={passed} time_points=2501 signals=19")
    return 0 if passed==5 else 1

if __name__=="__main__":raise SystemExit(main())
