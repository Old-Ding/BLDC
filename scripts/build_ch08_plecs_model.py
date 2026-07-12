"""从第 07 章启动模型派生带负载阶跃的失步诊断模型。"""

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
    target_dir = root / "models/plecs/ch08_open_loop_desync"
    target = target_dir / "ch08_open_loop_desync.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch07_startup_ramp"', 'Name          "ch08_open_loop_desync"', 1)
    text = text.replace('TimeSpan      "0.3"', 'TimeSpan      "0.35"', 1)
    text = text.replace('TimeRange     "0.1"', 'TimeRange     "0.35"', 1)
    text = text.replace('Name          "Mechanical angle [rad]"', 'Name          "Mechanical speed under gentle open-loop ramp"', 1)
    text = text.replace('AxisLabel     "Current / A"', 'AxisLabel     "speed / (rad/s)"', 1)
    text = text.replace(
        '"sequence_direction = 1;"',
        '"sequence_direction = 1;\\n"\n"load_before_Nm = 0;\\n"\n"load_after_Nm = 0;\\n"\n"load_step_time_s = 1;"',
        1,
    )

    tm_start, tm_end = block_bounds(text, 'Name          "Tm"', "    Component {")
    load_profile = '''    Component {
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
    text = text[:tm_start] + load_profile + text[tm_end:]
    text = text.replace('SrcComponent  "Tm"', 'SrcComponent  "Load profile"', 1)
    text = text.replace(
        '''      SrcComponent  "Demux"
      SrcTerminal   3
      DstComponent  "speed_rad_s"
      DstTerminal   1''',
        '''      SrcComponent  "Demux"
      SrcTerminal   3
      Branch {
        DstComponent  "speed_rad_s"
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
    text = text.replace(
        "Chapter 07 - alignment and startup frequency ramp",
        "Chapter 08 - open-loop desynchronization diagnosis",
        1,
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
