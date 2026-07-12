"""从第 03 章角度模型派生定位与频率斜坡启动模型。"""

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
    target_dir = root / "models/plecs/ch07_startup_ramp"
    target = target_dir / "ch07_startup_ramp.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch03_electrical_angle"', 'Name          "ch07_startup_ramp"', 1)
    text = text.replace('TimeSpan      "0.05"', 'TimeSpan      "0.3"', 1)
    text = text.replace(
        '"pole_pairs = 1;"',
        '"pole_pairs = 1;\\n"\n"alignment_s = 0.02;\\n"\n"start_frequency_Hz = 5;\\n"\n"end_frequency_Hz = 33.333333;\\n"\n"ramp_duration_s = 0.2;\\n"\n"sequence_direction = 1;"',
        1,
    )
    constant_start, constant_end = block_bounds(text, 'Name          "Phase command"', "        Component {")
    cscript = '''        Component {
          Type          CScript
          Name          "Startup angle generator"
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
          Parameter {
            Variable      "Parameters"
            Value         "alignment_s, start_frequency_Hz, end_frequency_Hz, ramp_duration_s, sequence_direction"
            Show          off
          }
          Parameter { Variable "LangStandard" Value "2" Show off }
          Parameter { Variable "GnuExtensions" Value "2" Show off }
          Parameter { Variable "RuntimeCheck" Value "2" Show off }
          Parameter { Variable "Declarations" Value "" Show off }
          Parameter { Variable "StartFcn" Value "" Show off }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t = Input(0);\n"
            "double alignment = ParamRealData(0, 0);\n"
            "double f0 = ParamRealData(1, 0);\n"
            "double f1 = ParamRealData(2, 0);\n"
            "double ramp = ParamRealData(3, 0);\n"
            "int direction = ParamRealData(4, 0) >= 0.0 ? 1 : -1;\n"
            "double phase_cycles = 0.0;\n"
            "double run_t = t - alignment;\n"
            "int step = 0;\n"
            "static const double table[6][3] = {\n"
            " {1,-1,0}, {1,0,-1}, {0,1,-1}, {-1,1,0}, {-1,0,1}, {0,-1,1}\n"
            "};\n"
            "if (run_t > 0.0) {\n"
            " if (ramp <= 0.0) { phase_cycles = f1 * run_t; }\n"
            " else if (run_t < ramp) {\n"
            "  phase_cycles = f0 * run_t + 0.5 * (f1-f0) / ramp * run_t * run_t;\n"
            " } else {\n"
            "  phase_cycles = 0.5 * (f0+f1) * ramp + f1 * (run_t-ramp);\n"
            " }\n"
            " step = ((int)(phase_cycles * 6.0)) % 6;\n"
            " if (direction < 0 && step != 0) { step = 6-step; }\n"
            "}\n"
            "Output(0)=table[step][0]; Output(1)=table[step][1]; Output(2)=table[step][2];"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }'''
    text = text[:constant_start] + cscript + text[constant_end:]
    text = text.replace('SrcComponent  "Phase command"', 'SrcComponent  "Startup angle generator"', 1)
    text = text.replace('SrcTerminal   1\n          DstComponent  "phase_cmd"', 'SrcTerminal   2\n          DstComponent  "phase_cmd"', 1)

    lref_marker = text.index('Name          "lref"')
    lref_start, lref_end = block_bounds(text, 'Name          "lref"', "    Component {")
    clock = '''    Component {
      Type          Clock
      Name          "Clock"
      Show          on
      Position      [35, 95]
      Direction     right
      Flipped       off
      LabelPosition south
    }'''
    text = text[:lref_start] + clock + text[lref_end:]
    text = text.replace('SrcComponent  "lref"\n      SrcTerminal   1\n      DstComponent  "Current controller"', 'SrcComponent  "Clock"\n      SrcTerminal   1\n      DstComponent  "Current controller"', 1)
    text = text.replace('SrcComponent  "unused_ref"\n          SrcTerminal   1\n          DstComponent  "Startup angle generator"', 'SrcComponent  "unused_ref"\n          SrcTerminal   1\n          DstComponent  "Startup angle generator"', 1)
    # 原固定命令只有输出连接；显式加入 Clock 内部端口到 C-Script 的数据流。
    output_connection = '''        Connection {
          Type          Signal
          SrcComponent  "Startup angle generator"
          SrcTerminal   2
          DstComponent  "phase_cmd"
          DstTerminal   1
        }'''
    input_connection = '''        Connection {
          Type          Signal
          SrcComponent  "unused_ref"
          SrcTerminal   1
          DstComponent  "Startup angle generator"
          DstTerminal   1
        }
'''
    text = text.replace(output_connection, input_connection + output_connection, 1)
    text = text.replace("Chapter 03 - mechanical and electrical angle", "Chapter 07 - alignment and startup frequency ramp", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
