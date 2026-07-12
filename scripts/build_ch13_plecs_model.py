"""从第 11 章 PWM 模型派生速度 PI、限幅和抗饱和模型。"""
from pathlib import Path

def block_bounds(text:str,marker:str,opening:str)->tuple[int,int]:
    mi=text.index(marker);start=text.rfind(opening,0,mi);depth=0
    for i in range(start,len(text)):
        if text[i]=="{":depth+=1
        elif text[i]=="}":
            depth-=1
            if depth==0:return start,i+1
    raise ValueError(marker)

def main()->None:
    root=Path(__file__).resolve().parents[1];source=root/"models/plecs/ch11_pwm_deadtime/ch11_pwm_deadtime.plecs";target_dir=root/"models/plecs/ch13_speed_pi";target=target_dir/"ch13_speed_pi.plecs";text=source.read_text(encoding="utf-8")
    text=text.replace('Name          "ch11_pwm_deadtime"','Name          "ch13_speed_pi"',1).replace('TimeSpan      "0.05"','TimeSpan      "0.2"',1)
    text=text.replace('"deadtime_s = 2e-6;"','"deadtime_s = 2e-6;\\n"\n"speed_target_before_rad_s = 60;\\n"\n"speed_target_after_rad_s = 80;\\n"\n"speed_target_step_s = 0.08;\\n"\n"speed_kp = 0.008;\\n"\n"speed_ki = 0.8;\\n"\n"duty_min = 0.1;\\n"\n"duty_max = 0.9;\\n"\n"antiwindup_enable = 1;\\n"\n"load_before_Nm = 0;\\n"\n"load_after_Nm = 0;\\n"\n"load_step_time_s = 1;"',1)
    text=text.replace('Name          "PWM three-state phase command"','Name          "Mechanical speed under PI control"',1).replace('AxisLabel     "phase command"','AxisLabel     "speed / (rad/s)"',1).replace('TimeRange     "0.002"','TimeRange     "0.25"',1)
    tm_start,tm_end=block_bounds(text,'Name          "Tm"',"    Component {")
    load='''    Component {
      Type          Step
      Name          "Load profile"
      Show          on
      Position      [90, 265]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Time"
        Value         "load_step_time_s"
        Show          off
      }
      Parameter {
        Variable      "Before"
        Value         "load_before_Nm"
        Show          off
      }
      Parameter {
        Variable      "After"
        Value         "load_after_Nm"
        Show          off
      }
      Parameter {
        Variable      "DataType"
        Value         "10"
        Show          off
      }
    }'''
    text=text[:tm_start]+load+text[tm_end:];text=text.replace('SrcComponent  "Tm"','SrcComponent  "Load profile"',1)
    start,end=block_bounds(text,'Name          "Hall PWM commutator"',"        Component {")
    controller='''        Component {
          Type          SignalMux
          Name          "speed_angle_mux"
          Show          on
          Position      [120, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Width" Value "[1 1]" Show off }
        }
        Component {
          Type          CScript
          Name          "Speed PI Hall PWM"
          Show          on
          Position      [190, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "2" Show off }
          Parameter { Variable "NumOutputs" Value "3" Show off }
          Parameter { Variable "NumContStates" Value "1" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "0" Show off }
          Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, commutation_offset_steps, table_direction, hall_enable, pwm_frequency_Hz, deadtime_s, speed_target_before_rad_s, speed_target_after_rad_s, speed_target_step_s, speed_kp, speed_ki, duty_min, duty_max, antiwindup_enable" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "" Show off }
          Parameter { Variable "StartFcn" Value "" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t=CurrentTime; double speed=Input(0); double theta=Input(1)*ParamRealData(0,0)+ParamRealData(1,0); double target=t<ParamRealData(9,0)?ParamRealData(7,0):ParamRealData(8,0);\n"
            "double duty=ParamRealData(10,0)*(target-speed)+ContState(0); if(duty<ParamRealData(12,0))duty=ParamRealData(12,0); if(duty>ParamRealData(13,0))duty=ParamRealData(13,0);\n"
            "double two_pi=6.283185307179586;while(theta>=two_pi)theta-=two_pi;while(theta<0)theta+=two_pi;int sector=(int)(theta/(two_pi/6.0));int step=(sector+(int)ParamRealData(2,0))%6;if(step<0)step+=6;if(ParamRealData(3,0)<0&&step!=0)step=6-step;\n"
            "static int last_step=-1;static double blank_until=0;double deadtime=ParamRealData(6,0);if(IsMajorStep&&step!=last_step){last_step=step;blank_until=t+deadtime;}double period=1.0/ParamRealData(5,0);int cycle=(int)(t/period);double carrier=t-cycle*period;int high_on=(carrier>=deadtime&&carrier<duty*period);\n"
            "static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}};for(int k=0;k<3;k++){double base=table[step][k];Output(k)=base>0?(high_on?1:0):(base<0?-1:0);if(t<blank_until||ParamRealData(4,0)<0.5)Output(k)=0;}"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter {
            Variable      "DerivativeFcn"
            Value         "double t=CurrentTime;double speed=Input(0);double target=t<ParamRealData(9,0)?ParamRealData(7,0):ParamRealData(8,0);double e=target-speed;double u=ParamRealData(10,0)*e+ContState(0);int freeze=ParamRealData(14,0)>0.5&&((u>=ParamRealData(13,0)&&e>0)||(u<=ParamRealData(12,0)&&e<0));ContDeriv(0)=freeze?0:ParamRealData(11,0)*e;"
            Show          off
          }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }'''
    text=text[:start]+controller+text[end:]
    text=text.replace('SrcComponent  "Hall PWM commutator"','SrcComponent  "Speed PI Hall PWM"',1)
    rotor_conn='''        Connection {
          Type          Signal
          SrcComponent  "rotor_angle"
          SrcTerminal   1
          Points        [110, 135; 110, 95]
          DstComponent  "Hall PWM commutator"
          DstTerminal   1
        }'''
    mux_conns='''        Connection {
          Type          Signal
          SrcComponent  "mechanical_speed"
          SrcTerminal   1
          Points        [100, 55; 100, 90]
          DstComponent  "speed_angle_mux"
          DstTerminal   2
        }
        Connection {
          Type          Signal
          SrcComponent  "rotor_angle"
          SrcTerminal   1
          Points        [100, 135; 100, 100]
          DstComponent  "speed_angle_mux"
          DstTerminal   3
        }
        Connection {
          Type          Signal
          SrcComponent  "speed_angle_mux"
          SrcTerminal   1
          DstComponent  "Speed PI Hall PWM"
          DstTerminal   1
        }'''
    text=text.replace(rotor_conn,mux_conns,1).replace('Name          "phase_current"','Name          "mechanical_speed"',1)
    scope_branch='''      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }''';text=text.replace(scope_branch,'',1)
    speed_conn='''    Connection {
      Type          Signal
      SrcComponent  "Demux"
      SrcTerminal   3
      DstComponent  "speed_rad_s"
      DstTerminal   1
    }'''
    speed_branches='''    Connection {
      Type          Signal
      SrcComponent  "Demux"
      SrcTerminal   3
      Branch {
        DstComponent  "speed_rad_s"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Current controller"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }
    }''';text=text.replace(speed_conn,speed_branches,1)
    current_branch='''      Branch {
        Points        [60, 50; 60, 75]
        DstComponent  "Current controller"
        DstTerminal   1
      }
''';text=text.replace(current_branch,'',1)
    text=text.replace("Chapter 11 - PWM duty and deadtime","Chapter 13 - speed PI saturation and anti-windup",1)
    target_dir.mkdir(parents=True,exist_ok=True);target.write_text(text.replace("\r\n","\n").replace("\n","\r\n"),encoding="utf-8",newline="");print(f"Generated {target.relative_to(root)}")

if __name__=="__main__":main()
