"""从第 13 章速度 PI 模型派生第一季完整 Hall 六步闭环模型。"""
from pathlib import Path


def block_bounds(text: str, marker: str, opening: str) -> tuple[int, int]:
    marker_index = text.index(marker)
    start = text.rfind(opening, 0, marker_index)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(marker)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch13_speed_pi/ch13_speed_pi.plecs"
    target_dir = root / "models/plecs/ch14_complete_hall_closed_loop"
    target = target_dir / "ch14_complete_hall_closed_loop.plecs"
    text = source.read_text(encoding="utf-8")
    text = (
        text.replace('Name          "ch13_speed_pi"', 'Name          "ch14_complete_hall_closed_loop"', 1)
        .replace('TimeSpan      "0.2"', 'TimeSpan      "0.5"', 1)
        .replace('TimeRange     "0.25"', 'TimeRange     "0.5"', 1)
    )
    text = text.replace(
        '"load_step_time_s = 1;"',
        '"load_step_time_s = 1;\\n"\n"hall_invalid_start_s = 1;\\n"\n"hall_invalid_end_s = 1;\\n"\n"hall_speed_alpha = 0.25;\\n"\n"hall_speed_timeout_s = 0.05;"',
        1,
    )
    text = text.replace(
        '''      Terminal {
        Type          Output
        Position      [39, 0]
        Direction     right
      }''',
        '''      Terminal {
        Type          Output
        Position      [39, -10]
        Direction     right
      }
      Terminal {
        Type          Output
        Position      [39, 10]
        Direction     right
      }''',
        1,
    )

    suite_start, _ = block_bounds(text, 'Name          "speed_angle_mux"', "        Component {")
    _, suite_end = block_bounds(
        text,
        'Name          "<html><body><p align=\\"center\\">Configured three-state phase command',
        "        Annotation {",
    )
    suite = '''        Component {
          Type          CScript
          Name          "Hall interface"
          Show          on
          Position      [115, 135]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "1" Show off }
          Parameter { Variable "NumOutputs" Value "13" Show off }
          Parameter { Variable "NumContStates" Value "0" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "-1" Show off }
          Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, hall_enable, hall_invalid_start_s, hall_invalid_end_s, hall_speed_alpha, hall_speed_timeout_s" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "static int previous_code=-1, legal_edge_count=0, was_fault=0, timed_out_active=0; static double last_edge_time=0, raw_speed=0, filtered_speed=0;" Show off }
          Parameter { Variable "StartFcn" Value "previous_code=-1;legal_edge_count=0;was_fault=0;timed_out_active=0;last_edge_time=0;raw_speed=0;filtered_speed=0;" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t=CurrentTime; double theta=Input(0)*ParamRealData(0,0)+ParamRealData(1,0); double two_pi=6.283185307179586;
"
            "while(theta>=two_pi)theta-=two_pi; while(theta<0)theta+=two_pi; int sector=(int)(theta/(two_pi/6.0)); static const int seq[6]={5,1,3,2,6,4}; int injected=(t>=ParamRealData(3,0)&&t<ParamRealData(4,0)); int code=injected?0:seq[sector];
"
            "int valid=(code==5||code==1||code==3||code==2||code==6||code==4); int decoded=-1; for(int i=0;i<6;i++){if(seq[i]==code)decoded=i;} int cls=valid?0:2; int direction=0; int legal=0; int fault=valid?0:1;
"
            "if(valid&&previous_code>=0&&code!=previous_code){int pi=-1,ci=-1;for(int i=0;i<6;i++){if(seq[i]==previous_code)pi=i;if(seq[i]==code)ci=i;}int delta=(ci-pi+6)%6;if(delta==1){cls=1;direction=1;legal=1;}else if(delta==5){cls=-1;direction=-1;legal=1;}else{cls=3;fault=1;}}
"
            "if(IsMajorStep){if(fault){was_fault=1;raw_speed=0;filtered_speed=0;timed_out_active=1;}else if(was_fault){was_fault=0;previous_code=code;last_edge_time=t;legal_edge_count=0;raw_speed=0;filtered_speed=0;timed_out_active=0;}else if(valid&&previous_code<0){previous_code=code;last_edge_time=t;}else if(valid&&legal){double dt=t-last_edge_time; if(timed_out_active||legal_edge_count==0){raw_speed=0;filtered_speed=0;}else if(dt>1e-9){raw_speed=direction*1.0471975511965976/(ParamRealData(0,0)*dt);filtered_speed=(legal_edge_count==1)?raw_speed:ParamRealData(5,0)*raw_speed+(1-ParamRealData(5,0))*filtered_speed;} legal_edge_count++; previous_code=code; last_edge_time=t; timed_out_active=0;}}
"
            "int timeout=((previous_code<0&&t>=ParamRealData(6,0))||(previous_code>=0&&t-last_edge_time>=ParamRealData(6,0))); if(timeout){raw_speed=0;filtered_speed=0;timed_out_active=1;} int enable=(ParamRealData(2,0)>=0.5&&valid&&fault==0);
"
            "Output(0)=(code>>2)&1;Output(1)=(code>>1)&1;Output(2)=code&1;Output(3)=code;Output(4)=decoded;Output(5)=cls;Output(6)=legal;Output(7)=direction;Output(8)=filtered_speed;Output(9)=timeout;Output(10)=enable;Output(11)=fault;Output(12)=legal_edge_count;"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }
        Component {
          Type          SignalMux
          Name          "speed_hall_mux"
          Show          on
          Position      [175, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Width" Value "[1 13]" Show off }
        }
        Component {
          Type          CScript
          Name          "Speed PI Hall PWM"
          Show          on
          Position      [245, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "14" Show off }
          Parameter { Variable "NumOutputs" Value "23" Show off }
          Parameter { Variable "NumContStates" Value "1" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "0" Show off }
          Parameter { Variable "Parameters" Value "commutation_offset_steps, table_direction, pwm_frequency_Hz, deadtime_s, speed_target_before_rad_s, speed_target_after_rad_s, speed_target_step_s, speed_kp, speed_ki, duty_min, duty_max, antiwindup_enable" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "static int last_step=-1; static double blank_until=0;" Show off }
          Parameter { Variable "StartFcn" Value "last_step=-1;blank_until=0;" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t=CurrentTime; double speed=Input(9); double target=t<ParamRealData(6,0)?ParamRealData(4,0):ParamRealData(5,0); double duty=ParamRealData(7,0)*(target-speed)+ContState(0); if(duty<ParamRealData(9,0))duty=ParamRealData(9,0); if(duty>ParamRealData(10,0))duty=ParamRealData(10,0);
"
            "int sector=(int)(Input(5)+0.5); int offset=(int)ParamRealData(0,0); int table_direction=ParamRealData(1,0)>=0?1:-1; int step=(sector+offset)%6; if(step<0)step+=6; if(table_direction<0&&step!=0)step=6-step; int enable=(Input(11)>0.5&&Input(12)<0.5&&sector>=0);
"
            "double deadtime=ParamRealData(3,0); if(IsMajorStep&&step!=last_step){last_step=step;blank_until=t+deadtime;} double period=1.0/ParamRealData(2,0); int cycle=(int)(t/period); double carrier=t-cycle*period; int high_on=(carrier>=deadtime&&carrier<duty*period);
"
            "static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}}; double cmd[3]={0,0,0}; for(int k=0;k<3;k++){double base=table[step][k];cmd[k]=enable?(base>0?(high_on?1:0):(base<0?-1:0)):0;if(t<blank_until)cmd[k]=0;Output(k)=cmd[k];}
"
            "Output(3)=duty;for(int k=0;k<13;k++)Output(4+k)=Input(1+k);Output(17)=cmd[0]>0.5;Output(18)=cmd[0]<-0.5;Output(19)=cmd[1]>0.5;Output(20)=cmd[1]<-0.5;Output(21)=cmd[2]>0.5;Output(22)=cmd[2]<-0.5;"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter {
            Variable      "DerivativeFcn"
            Value         "double t=CurrentTime;double speed=Input(9);double target=t<ParamRealData(6,0)?ParamRealData(4,0):ParamRealData(5,0);double e=target-speed;double u=ParamRealData(7,0)*e+ContState(0);int fault=Input(12)>0.5;int freeze=fault||(ParamRealData(11,0)>0.5&&((u>=ParamRealData(10,0)&&e>0)||(u<=ParamRealData(9,0)&&e<0)));ContDeriv(0)=freeze?0:ParamRealData(8,0)*e;"
            Show          off
          }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }
        Component {
          Type          SignalDemux
          Name          "control_output_demux"
          Show          on
          Position      [320, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Width" Value "[3 20]" Show off }
        }
        Component {
          Type          Output
          Name          "phase_cmd"
          Show          on
          Position      [375, 80]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Index" Value "4" Show on }
          Parameter { Variable "Width" Value "-1" Show off }
        }
        Component {
          Type          Output
          Name          "hall_diag_internal"
          Show          on
          Position      [375, 120]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Index" Value "5" Show on }
          Parameter { Variable "Width" Value "-1" Show off }
        }
        Connection {
          Type          Signal
          SrcComponent  "mechanical_speed"
          SrcTerminal   1
          Points        [100, 55; 100, 90]
          DstComponent  "speed_hall_mux"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "rotor_angle"
          SrcTerminal   1
          Points        [90, 135]
          DstComponent  "Hall interface"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Hall interface"
          SrcTerminal   2
          Points        [145, 135; 145, 100]
          DstComponent  "speed_hall_mux"
          DstTerminal   3
        }
        Connection {
          Type          Signal
          SrcComponent  "speed_hall_mux"
          SrcTerminal   1
          DstComponent  "Speed PI Hall PWM"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Speed PI Hall PWM"
          SrcTerminal   2
          DstComponent  "control_output_demux"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "control_output_demux"
          SrcTerminal   2
          DstComponent  "phase_cmd"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "control_output_demux"
          SrcTerminal   3
          DstComponent  "hall_diag_internal"
          DstTerminal   1
        }'''
    text = text[:suite_start] + suite + text[suite_end:]

    mech_start, mech_end = block_bounds(text, 'Name          "mechanical_angle_rad"', "    Component {")
    diagnostics_mux = '''    Component {
      Type          SignalMux
      Name          "mechanical_angle_diag_mux"
      Show          on
      Position      [585, 310]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter { Variable "Width" Value "[1 20]" Show off }
    }
'''
    text = text[:mech_end] + "\n" + diagnostics_mux + text[mech_end:]
    text = text.replace(
        '''      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }''',
        '''      Branch {
        DstComponent  "mechanical_angle_diag_mux"
        DstTerminal   2
      }''',
        1,
    )
    diagnostics_connection = '''    Connection {
      Type          Signal
      SrcComponent  "Current controller"
      SrcTerminal   5
      DstComponent  "mechanical_angle_diag_mux"
      DstTerminal   3
    }
    Connection {
      Type          Signal
      SrcComponent  "mechanical_angle_diag_mux"
      SrcTerminal   1
      DstComponent  "mechanical_angle_rad"
      DstTerminal   1
    }
'''
    text = text.replace(
        '''    Connection {
      Type          Signal
      SrcComponent  "Udc"''',
        diagnostics_connection + '''    Connection {
      Type          Signal
      SrcComponent  "Udc"''',
        1,
    )
    text = text.replace('Name          "Mechanical speed under PI control"', 'Name          "Complete Hall closed-loop speed"', 1)
    text = text.replace("Chapter 13 - speed PI saturation and anti-windup", "Chapter 14 - complete Hall six-step closed loop", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
