"""从第 10 章 Hall 换相模型派生单极性 PWM 与保护间隔模型。"""

from pathlib import Path


def block_bounds(text: str, marker: str, opening: str) -> tuple[int, int]:
    marker_index=text.index(marker);start=text.rfind(opening,0,marker_index);depth=0
    for index in range(start,len(text)):
        if text[index]=="{":depth+=1
        elif text[index]=="}":
            depth-=1
            if depth==0:return start,index+1
    raise ValueError(marker)


def main()->None:
    root=Path(__file__).resolve().parents[1];source=root/"models/plecs/ch10_hall_commutation/ch10_hall_commutation.plecs";target_dir=root/"models/plecs/ch11_pwm_deadtime";target=target_dir/"ch11_pwm_deadtime.plecs";text=source.read_text(encoding="utf-8")
    text=text.replace('Name          "ch10_hall_commutation"','Name          "ch11_pwm_deadtime"',1).replace('TimeSpan      "0.08"','TimeSpan      "0.05"',1)
    text=text.replace('"hall_enable = 1;"','"hall_enable = 1;\\n"\n"pwm_frequency_Hz = 10000;\\n"\n"pwm_duty = 0.5;\\n"\n"deadtime_s = 2e-6;"',1)
    text=text.replace('Name          "Mechanical angle [rad]"','Name          "PWM three-state phase command"',1).replace('AxisLabel     "Current / A"','AxisLabel     "phase command"',1).replace('TimeRange     "0.1"','TimeRange     "0.002"',1)
    start,end=block_bounds(text,'Name          "Hall commutator"',"        Component {")
    controller='''        Component {
          Type          CScript
          Name          "Hall PWM commutator"
          Show          on
          Position      [160, 95]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "1" Show off }
          Parameter { Variable "NumOutputs" Value "3" Show off }
          Parameter { Variable "NumContStates" Value "0" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "-1" Show off }
          Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, commutation_offset_steps, table_direction, hall_enable, pwm_frequency_Hz, pwm_duty, deadtime_s" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "" Show off }
          Parameter { Variable "StartFcn" Value "" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t=CurrentTime; double theta=Input(0)*ParamRealData(0,0)+ParamRealData(1,0); double two_pi=6.283185307179586;\n"
            "while(theta>=two_pi)theta-=two_pi; while(theta<0)theta+=two_pi; int sector=(int)(theta/(two_pi/6.0));\n"
            "int offset=(int)ParamRealData(2,0); int direction=ParamRealData(3,0)>=0?1:-1; int step=(sector+offset)%6; if(step<0)step+=6; if(direction<0&&step!=0)step=6-step;\n"
            "static int last_step=-1; static double blank_until=0; double deadtime=ParamRealData(7,0); if(IsMajorStep&&step!=last_step){last_step=step;blank_until=t+deadtime;}\n"
            "double period=1.0/ParamRealData(5,0); int cycle_index=(int)(t/period); double carrier_time=t-cycle_index*period; double duty=ParamRealData(6,0);\n"
            "int high_on=(carrier_time>=deadtime&&carrier_time<duty*period); static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}};\n"
            "for(int k=0;k<3;k++){double base=table[step][k];Output(k)=(base>0?(high_on?1:0):(base<0?-1:0));if(t<blank_until||ParamRealData(4,0)<0.5)Output(k)=0;}"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }'''
    text=text[:start]+controller+text[end:]
    text=text.replace('DstComponent  "Hall commutator"','DstComponent  "Hall PWM commutator"',1).replace('SrcComponent  "Hall commutator"','SrcComponent  "Hall PWM commutator"',1)
    angle_scope='''      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }''';text=text.replace(angle_scope,'',1)
    phase_branch='''      Branch {
        DstComponent  "phase_command"
        DstTerminal   1
      }'''
    text=text.replace(phase_branch,phase_branch+'''\n      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }''',1)
    text=text.replace("Chapter 10 - Hall commutation and installation offset","Chapter 11 - PWM duty and deadtime",1)
    target_dir.mkdir(parents=True,exist_ok=True);target.write_text(text.replace("\r\n","\n").replace("\n","\r\n"),encoding="utf-8",newline="");print(f"Generated {target.relative_to(root)}")


if __name__=="__main__":main()
