"""从第 02 章真实功率级派生六步换相序列模型。"""

from __future__ import annotations

from pathlib import Path


def bounds(text: str, marker: str) -> tuple[int, int]:
    marker_index = text.index(marker)
    start = text.rfind("        Component {", 0, marker_index)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{": depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0: return start, index + 1
    raise ValueError(marker)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs"
    target_dir = root / "models/plecs/ch05_six_step_sequence"
    target = target_dir / "ch05_six_step_sequence.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch02_three_phase_bridge"', 'Name          "ch05_six_step_sequence"', 1)
    text = text.replace('TimeSpan      "0.01"', 'TimeSpan      "0.012"', 1)
    text = text.replace(
        '"phase_cmd = [0 0 0];"',
        '"phase_cmd = [0 0 0];\\n"\n"step_period_s = 0.001;\\n"\n"sequence_direction = 1;"',
        1,
    )

    start, end = bounds(text, 'Name          "Phase command"')
    cscript = '''        Component {
          Type          CScript
          Name          "Six-step table"
          Show          on
          Position      [160, 95]
          Direction     up
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "DialogGeometry"
            Value         ""
            Show          off
          }
          Parameter {
            Variable      "NumInputs"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "NumOutputs"
            Value         "3"
            Show          off
          }
          Parameter {
            Variable      "NumContStates"
            Value         "0"
            Show          off
          }
          Parameter {
            Variable      "NumDiscStates"
            Value         "0"
            Show          off
          }
          Parameter {
            Variable      "NumZCSignals"
            Value         "0"
            Show          off
          }
          Parameter {
            Variable      "DirectFeedthrough"
            Value         "1"
            Show          off
          }
          Parameter {
            Variable      "Ts"
            Value         "-1"
            Show          off
          }
          Parameter {
            Variable      "Parameters"
            Value         "step_period_s, sequence_direction"
            Show          off
          }
          Parameter {
            Variable      "LangStandard"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "GnuExtensions"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "RuntimeCheck"
            Value         "2"
            Show          off
          }
          Parameter {
            Variable      "Declarations"
            Value         ""
            Show          off
          }
          Parameter {
            Variable      "StartFcn"
            Value         ""
            Show          off
          }
          Parameter {
            Variable      "OutputFcn"
            Value         "double t = Input(0);\n"
            "double period = ParamRealData(0, 0);\n"
            "int direction = ParamRealData(1, 0) >= 0.0 ? 1 : -1;\n"
            "int step = 0;\n"
            "static const double table[6][3] = {\n"
            "  { 1, -1,  0}, { 1,  0, -1}, { 0,  1, -1},\n"
            "  {-1,  1,  0}, {-1,  0,  1}, { 0, -1,  1}\n"
            "};\n"
            "if (period <= 0.0) {\n"
            "  Output(0) = 0.0; Output(1) = 0.0; Output(2) = 0.0;\n"
            "} else {\n"
            "  step = ((int)(t / period)) % 6;\n"
            "  if (direction < 0) { step = (6 - step) % 6; }\n"
            "  Output(0) = table[step][0];\n"
            "  Output(1) = table[step][1];\n"
            "  Output(2) = table[step][2];\n"
            "}"
            Show          off
          }
          Parameter { Variable "UpdateFcn" Value "" Show off }
          Parameter { Variable "DerivativeFcn" Value "" Show off }
          Parameter { Variable "TerminateFcn" Value "" Show off }
          Parameter { Variable "StoreCustomStateFcn" Value "" Show off }
          Parameter { Variable "RestoreCustomStateFcn" Value "" Show off }
        }'''
    text = text[:start] + cscript + text[end:]
    text = text.replace('SrcComponent  "Phase command"', 'SrcComponent  "Six-step table"', 1)
    text = text.replace(
        '''        Connection {
          Type          Signal
          SrcComponent  "Six-step table"
          SrcTerminal   1
          DstComponent  "phase_cmd"
          DstTerminal   1
        }''',
        '''        Connection {
          Type          Signal
          SrcComponent  "unused_ref"
          SrcTerminal   1
          DstComponent  "Six-step table"
          DstTerminal   1
        }
        Connection {
          Type          Signal
          SrcComponent  "Six-step table"
          SrcTerminal   2
          DstComponent  "phase_cmd"
          DstTerminal   1
        }''',
        1,
    )
    clock_component = '''    Component {
      Type          Clock
      Name          "Clock"
      Show          on
      Position      [35, 95]
      Direction     right
      Flipped       off
      LabelPosition south
    }
'''
    lref_marker = text.index('Name          "lref"')
    lref_start = text.rfind("    Component {", 0, lref_marker)
    depth = 0
    lref_end = None
    for index in range(lref_start, len(text)):
        if text[index] == "{": depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                lref_end = index + 1
                break
    if lref_end is None: raise ValueError("lref component")
    text = text[:lref_start] + clock_component + text[lref_end:]
    text = text.replace('SrcComponent  "lref"\n      SrcTerminal   1\n      DstComponent  "Current controller"', 'SrcComponent  "Clock"\n      SrcTerminal   1\n      DstComponent  "Current controller"', 1)
    text = text.replace("Chapter 02 - three-state command, real IGBT bridge and BLDC winding", "Chapter 05 - six-step sequence", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__": main()
