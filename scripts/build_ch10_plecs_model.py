"""从第 07 章功率模型派生 Hall 位置换相与安装偏置模型。"""

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
    source = root / "models/plecs/ch07_startup_ramp/ch07_startup_ramp.plecs"
    target_dir = root / "models/plecs/ch10_hall_commutation"
    target = target_dir / "ch10_hall_commutation.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch07_startup_ramp"', 'Name          "ch10_hall_commutation"', 1)
    text = text.replace('TimeSpan      "0.3"', 'TimeSpan      "0.08"', 1)
    text = text.replace('TimeRange     "0.1"', 'TimeRange     "0.08"', 1)
    text = text.replace('Name          "Mechanical angle [rad]"', 'Name          "Electromagnetic torque with correct Hall table"', 1)
    text = text.replace('AxisLabel     "Current / A"', 'AxisLabel     "torque / (N m)"', 1)
    text = text.replace(
        '"sequence_direction = 1;"',
        '"sequence_direction = 1;\\n"\n"hall_offset_rad = 0;\\n"\n"commutation_offset_steps = 0;\\n"\n"table_direction = 1;\\n"\n"hall_enable = 1;"',
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

    controller_start, controller_end = block_bounds(text, 'Name          "Startup angle generator"', "        Component {")
    controller = '''        Component {
          Type          CScript
          Name          "Hall interface"
          Show          on
          Position      [125, 135]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "1" Show off }
          Parameter { Variable "NumOutputs" Value "10" Show off }
          Parameter { Variable "NumContStates" Value "0" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "-1" Show off }
          Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, hall_enable" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "static int previous_code=-1;" Show off }
          Parameter { Variable "StartFcn" Value "previous_code=-1;" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double theta=Input(0)*ParamRealData(0,0)+ParamRealData(1,0); double two_pi=6.283185307179586;
"
            "while(theta>=two_pi)theta-=two_pi; while(theta<0)theta+=two_pi; int sector=(int)(theta/(two_pi/6.0)); static const int seq[6]={5,1,3,2,6,4}; int code=seq[sector];
"
            "int valid=(code==5||code==1||code==3||code==2||code==6||code==4); int decoded=-1; for(int i=0;i<6;i++){if(seq[i]==code)decoded=i;} int cls=valid?0:2; int direction=0; int legal=0; int fault=valid?0:1;
"
            "if(valid&&previous_code>=0&&code!=previous_code){int pi=-1,ci=-1;for(int i=0;i<6;i++){if(seq[i]==previous_code)pi=i;if(seq[i]==code)ci=i;}int delta=(ci-pi+6)%6;if(delta==1){cls=1;direction=1;legal=1;}else if(delta==5){cls=-1;direction=-1;legal=1;}else{cls=3;fault=1;}}
"
            "if(IsMajorStep&&valid&&fault==0)previous_code=code; int enable=(ParamRealData(2,0)>=0.5&&valid&&fault==0);
"
            "Output(0)=(code>>2)&1;Output(1)=(code>>1)&1;Output(2)=code&1;Output(3)=code;Output(4)=decoded;Output(5)=cls;Output(6)=legal;Output(7)=direction;Output(8)=enable;Output(9)=fault;"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }
        Component {
          Type          CScript
          Name          "Hall commutator"
          Show          on
          Position      [225, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "DialogGeometry" Value "" Show off }
          Parameter { Variable "NumInputs" Value "10" Show off }
          Parameter { Variable "NumOutputs" Value "13" Show off }
          Parameter { Variable "NumContStates" Value "0" Show off }
          Parameter { Variable "NumDiscStates" Value "0" Show off }
          Parameter { Variable "NumZCSignals" Value "0" Show off }
          Parameter { Variable "DirectFeedthrough" Value "1" Show off }
          Parameter { Variable "Ts" Value "-1" Show off }
          Parameter { Variable "Parameters" Value "commutation_offset_steps, table_direction" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "" Show off }
          Parameter { Variable "StartFcn" Value "" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "int sector=(int)(Input(4)+0.5); int offset=(int)ParamRealData(0,0); int table_direction=ParamRealData(1,0)>=0?1:-1; int step=(sector+offset)%6; if(step<0)step+=6; if(table_direction<0&&step!=0)step=6-step;
"
            "static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}}; int enable=(Input(8)>0.5&&Input(9)<0.5&&sector>=0);
"
            "for(int k=0;k<3;k++)Output(k)=enable?table[step][k]:0; for(int k=0;k<10;k++)Output(3+k)=Input(k);"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }
        Component {
          Type          SignalDemux
          Name          "control_output_demux"
          Show          on
          Position      [305, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Width" Value "[3 10]" Show off }
        }
        Component {
          Type          Output
          Name          "phase_cmd"
          Show          on
          Position      [360, 80]
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
          Position      [360, 120]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Index" Value "5" Show on }
          Parameter { Variable "Width" Value "-1" Show off }
        }
        Connection {
          Type          Signal
          SrcComponent  "rotor_angle"
          SrcTerminal   1
          Points        [100, 135]
          DstComponent  "Hall interface"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Hall interface"
          SrcTerminal   2
          Points        [175, 135; 175, 95]
          DstComponent  "Hall commutator"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Hall commutator"
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
    text = text[:controller_start] + controller + text[controller_end:]
    first_phase = text.index('Name          "phase_cmd"')
    stale_phase = text.index('Name          "phase_cmd"', first_phase + 1)
    stale_start = text.rfind("        Component {", 0, stale_phase)
    _, stale_annotation_end = block_bounds(
        text,
        'Name          "<html><body><p align=\\"center\\">Configured three-state phase command',
        "        Annotation {",
    )
    text = text[:stale_start] + text[stale_annotation_end:]
    text = text.replace(
        '''      SrcComponent  "Demux"
      SrcTerminal   4
      DstComponent  "electromagnetic_torque_Nm"
      DstTerminal   1''',
        '''      SrcComponent  "Demux"
      SrcTerminal   4
      Branch {
        DstComponent  "electromagnetic_torque_Nm"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }''',
        1,
    )
    text = text.replace(
        '''      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }''',
        '''      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }''',
        1,
    )
    mech_start, mech_end = block_bounds(text, 'Name          "mechanical_angle_rad"', "    Component {")
    diagnostics_mux = '''    Component {
      Type          SignalMux
      Name          "mechanical_angle_diag_mux"
      Show          on
      Position      [585, 310]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter { Variable "Width" Value "[1 10]" Show off }
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
    text = text.replace("Chapter 07 - alignment and startup frequency ramp", "Chapter 10 - Hall commutation and installation offset", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
