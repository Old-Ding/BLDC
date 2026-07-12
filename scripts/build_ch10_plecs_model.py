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
    controller_start, controller_end = block_bounds(text, 'Name          "Startup angle generator"', "        Component {")
    controller = '''        Component {
          Type          CScript
          Name          "Hall commutator"
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
          Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, commutation_offset_steps, table_direction, hall_enable" Show off }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "" Show off }
          Parameter { Variable "StartFcn" Value "" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double theta=Input(0)*ParamRealData(0,0)+ParamRealData(1,0); double two_pi=6.283185307179586;\n"
            "while(theta>=two_pi)theta-=two_pi; while(theta<0)theta+=two_pi;\n"
            "int sector=(int)(theta/(two_pi/6.0)); int offset=(int)ParamRealData(2,0); int direction=ParamRealData(3,0)>=0?1:-1;\n"
            "int step=(sector+offset)%6; if(step<0)step+=6; if(direction<0&&step!=0)step=6-step;\n"
            "static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}};\n"
            "if(ParamRealData(4,0)<0.5){Output(0)=0;Output(1)=0;Output(2)=0;}else{Output(0)=table[step][0];Output(1)=table[step][1];Output(2)=table[step][2];}"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }'''
    text = text[:controller_start] + controller + text[controller_end:]
    text = text.replace('DstComponent  "Startup angle generator"', 'DstComponent  "Hall commutator"', 1)
    text = text.replace('SrcComponent  "Startup angle generator"', 'SrcComponent  "Hall commutator"', 1)
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
    text = text.replace('SrcComponent  "unused_ref"\n          SrcTerminal   1\n          DstComponent  "Hall commutator"',
                        'SrcComponent  "rotor_angle"\n          SrcTerminal   1\n          Points        [110, 135; 110, 95]\n          DstComponent  "Hall commutator"', 1)
    text = text.replace("Chapter 07 - alignment and startup frequency ramp", "Chapter 10 - Hall commutation and installation offset", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
