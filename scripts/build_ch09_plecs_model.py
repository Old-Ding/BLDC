"""从第 03 章角度模型派生 PLECS Hall 编码与非法状态模型。"""

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
    source = root / "models/plecs/ch03_electrical_angle/ch03_electrical_angle.plecs"
    target_dir = root / "models/plecs/ch09_hall_sequence"
    target = target_dir / "ch09_hall_sequence.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch03_electrical_angle"', 'Name          "ch09_hall_sequence"', 1)
    text = text.replace('TimeSpan      "0.05"', 'TimeSpan      "0.07"', 1)
    text = text.replace(
        '"pole_pairs = 1;"',
        '"pole_pairs = 1;\\n"\n"hall_offset_rad = 0;\\n"\n"force_invalid = 0;\\n"\n"invalid_code = 0;"',
        1,
    )
    text = text.replace('Name          "Mechanical angle [rad]"', 'Name          "Hall A/B/C and valid"', 1)
    text = text.replace('AxisLabel     "Current / A"', 'AxisLabel     "Logic state"', 1)

    hall_output = '''    Component {
      Type          CScript
      Name          "Hall encoder"
      Show          on
      Position      [550, 310]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter { Variable "DialogGeometry" Value "" Show off }
      Parameter { Variable "NumInputs" Value "1" Show off }
      Parameter { Variable "NumOutputs" Value "5" Show off }
      Parameter { Variable "NumContStates" Value "0" Show off }
      Parameter { Variable "NumDiscStates" Value "0" Show off }
      Parameter { Variable "NumZCSignals" Value "0" Show off }
      Parameter { Variable "DirectFeedthrough" Value "1" Show off }
      Parameter { Variable "Ts" Value "-1" Show off }
      Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, force_invalid, invalid_code" Show off }
      Parameter { Variable "LangStandard" Value "2" Show off }
      Parameter { Variable "GnuExtensions" Value "2" Show off }
      Parameter { Variable "RuntimeCheck" Value "2" Show off }
      Parameter { Variable "Declarations" Value "" Show off }
      Parameter { Variable "StartFcn" Value "" Show off }
      Parameter {
        Variable      "OutputFcn"
        Value         "double theta=Input(0)*ParamRealData(0,0)+ParamRealData(1,0);\n"
        "double two_pi=6.283185307179586; while(theta>=two_pi)theta-=two_pi; while(theta<0)theta+=two_pi;\n"
        "int sector=(int)(theta/(two_pi/6.0)); static const int hall_table[6]={5,1,3,2,6,4};\n"
        "int code=hall_table[sector]; if(ParamRealData(2,0)>0.5)code=(int)ParamRealData(3,0);\n"
        "Output(0)=Input(0); Output(1)=(code>>2)&1; Output(2)=(code>>1)&1; Output(3)=code&1; Output(4)=(code!=0&&code!=7);"
        Show          off
      }
      Parameter { Variable "UpdateFcn" Value "" Show off }
      Parameter { Variable "DerivativeFcn" Value "" Show off }
      Parameter { Variable "TerminateFcn" Value "" Show off }
      Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
      Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
    }
'''
    connection_marker = '    Connection {\n      Type          Signal\n      SrcComponent  "lref"'
    text = text.replace(connection_marker, hall_output + connection_marker, 1)

    angle_scope_branch = '''      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }'''
    text = text.replace(angle_scope_branch, '''      Branch {
        DstComponent  "Hall encoder"
        DstTerminal   1
      }''', 1)
    text = text.replace('''      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Hall encoder"''', '''      Branch {
        DstComponent  "Hall encoder"''', 1)

    hall_connection = '''    Connection {
      Type          Signal
      SrcComponent  "Hall encoder"
      SrcTerminal   2
      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }
    }
'''
    annotation_index = text.rfind("    Annotation {")
    text = text[:annotation_index] + hall_connection + text[annotation_index:]
    text = text.replace("Chapter 03 - mechanical and electrical angle", "Chapter 09 - Hall sequence and invalid states", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
