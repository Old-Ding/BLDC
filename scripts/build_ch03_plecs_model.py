"""从第 02 章功率级模型派生机械角/电角实验模型。"""

from __future__ import annotations

from pathlib import Path


def component_bounds(text: str, marker: str) -> tuple[int, int]:
    marker_index = text.index(marker)
    start = text.rfind("    Component {", 0, marker_index)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(f"组件括号不完整: {marker}")


def remove_axis(text: str, axis_name: str) -> str:
    marker = text.index(f'Name          "{axis_name}"')
    start = text.rfind("      Axis {", 0, marker)
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + text[index + 1 :]
    raise ValueError(f"坐标轴括号不完整: {axis_name}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch02_three_phase_bridge/ch02_three_phase_bridge.plecs"
    target_dir = root / "models/plecs/ch03_electrical_angle"
    target = target_dir / "ch03_electrical_angle.plecs"
    text = source.read_text(encoding="utf-8")

    text = text.replace('Name          "ch02_three_phase_bridge"', 'Name          "ch03_electrical_angle"', 1)
    text = text.replace('TimeSpan      "0.01"', 'TimeSpan      "0.05"', 1)
    text = text.replace('"phase_cmd = [0 0 0];"', '"phase_cmd = [0 0 0];\\n"\n"pole_pairs = 1;"', 1)
    text = text.replace(
        'Variable      "p"\n        Value         "1"',
        'Variable      "p"\n        Value         "pole_pairs"',
        1,
    )
    text = text.replace(
        '''  Terminal {
    Type          Output
    Index         "6"
  }
  Schematic {''',
        '''  Terminal {
    Type          Output
    Index         "6"
  }
  Terminal {
    Type          Output
    Index         "7"
  }
  Schematic {''',
        1,
    )

    text = text.replace('Axes          "2"', 'Axes          "1"', 1)
    scope_start, scope_end = component_bounds(text, 'Name          "Scope"')
    scope = text[scope_start:scope_end]
    scope = remove_axis(scope, "Line voltage [V]")
    scope = scope.replace('Name          "Phase current [A]"', 'Name          "Mechanical angle [rad]"', 1)
    text = text[:scope_start] + scope + text[scope_end:]

    angle_output = '''    Component {
      Type          Output
      Name          "mechanical_angle_rad"
      Show          on
      Position      [650, 310]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Index"
        Value         "7"
        Show          on
      }
      Parameter {
        Variable      "Width"
        Value         "-1"
        Show          off
      }
    }
'''
    connection_marker = '    Connection {\n      Type          Signal\n      SrcComponent  "lref"'
    text = text.replace(connection_marker, angle_output + connection_marker, 1)

    current_scope_branch = '''      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }
      Branch {
        DstComponent  "phase_current_A"
        DstTerminal   1
      }'''
    text = text.replace(
        current_scope_branch,
        '''      DstComponent  "phase_current_A"
      DstTerminal   1''',
        1,
    )
    phase_output_start, phase_output_end = component_bounds(text, 'Name          "phase_current_A"')
    phase_output = text[phase_output_start:phase_output_end].replace(
        'Value         "-1"', 'Value         "3"', 1
    )
    text = text[:phase_output_start] + phase_output + text[phase_output_end:]

    voltage_connection = '''    Connection {
      Type          Signal
      SrcComponent  "3ph Meter"
      SrcTerminal   7
      Points        [285, 35]
      Branch {
        DstComponent  "Scope"
        DstTerminal   2
      }
      Branch {
        DstComponent  "line_voltage_V"
        DstTerminal   1
      }
    }'''
    text = text.replace(
        voltage_connection,
        '''    Connection {
      Type          Signal
      SrcComponent  "3ph Meter"
      SrcTerminal   7
      DstComponent  "line_voltage_V"
      DstTerminal   1
    }''',
        1,
    )

    angle_connection = '''    Connection {
      Type          Signal
      SrcComponent  "Angle\\nSensor"
      SrcTerminal   2
      Points        [525, 255; 525, 290; 60, 290; 60, 115]
      DstComponent  "Current controller"
      DstTerminal   3
    }'''
    text = text.replace(
        angle_connection,
        '''    Connection {
      Type          Signal
      SrcComponent  "Angle\\nSensor"
      SrcTerminal   2
      Points        [525, 255]
      Branch {
        Points        [525, 290; 60, 290; 60, 115]
        DstComponent  "Current controller"
        DstTerminal   3
      }
      Branch {
        DstComponent  "mechanical_angle_rad"
        DstTerminal   1
      }
      Branch {
        DstComponent  "Scope"
        DstTerminal   1
      }
    }''',
        1,
    )

    text = text.replace("Chapter 02 - three-state command, real IGBT bridge and BLDC winding", "Chapter 03 - mechanical and electrical angle", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
