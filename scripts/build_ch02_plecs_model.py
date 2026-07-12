"""从已验证的第 01 章模型派生第 02 章真实三相桥模型。"""

from __future__ import annotations

from pathlib import Path


def replace_balanced_block(text: str, marker: str, replacement: str) -> str:
    marker_index = text.index(marker)
    block_start = text.rfind("    Component {", 0, marker_index)
    if block_start < 0:
        raise ValueError(f"找不到组件起点: {marker}")

    depth = 0
    block_end = None
    for index in range(block_start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                block_end = index + 1
                break
    if block_end is None:
        raise ValueError(f"组件括号不完整: {marker}")
    return text[:block_start] + replacement + text[block_end:]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch01_bldc_baseline/ch01_bldc_baseline.plecs"
    target_dir = root / "models/plecs/ch02_three_phase_bridge"
    target = target_dir / "ch02_three_phase_bridge.plecs"

    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch01_bldc_baseline"', 'Name          "ch02_three_phase_bridge"', 1)
    text = text.replace('TimeSpan      "0.3"', 'TimeSpan      "0.01"', 1)
    text = text.replace('MaxStep       "1e-3"', 'MaxStep       "1e-5"', 1)
    text = text.replace('InitStep      "1e-3"', 'InitStep      "1e-6"', 1)
    text = text.replace('Axes          "4"', 'Axes          "2"', 1)
    text = text.replace(
        '"current_ref_A = 5;"',
        '"current_ref_A = 5;\\n"\n"initial_speed_rad_s = 0;\\n"\n"phase_cmd = [0 0 0];"',
        1,
    )
    text = text.replace(
        '''  Terminal {
    Type          Output
    Index         "5"
  }
  Schematic {''',
        '''  Terminal {
    Type          Output
    Index         "5"
  }
  Terminal {
    Type          Output
    Index         "6"
  }
  Schematic {''',
        1,
    )
    text = text.replace('Value         "300"\n        Show          off\n      }\n      Parameter {\n        Variable      "thm0"', 'Value         "initial_speed_rad_s"\n        Show          off\n      }\n      Parameter {\n        Variable      "thm0"', 1)

    controller = '''    Component {
      Type          Subsystem
      Name          "Current controller"
      Show          on
      Position      [120, 95]
      Direction     up
      Flipped       off
      LabelPosition south
      Frame         [-35, -30; 35, 30]
      SampleTime    "-1"
      CodeGenDiscretizationMethod "2"
      CodeGenTarget "Generic"
      MaskIconFrame on
      MaskIconOpaque off
      MaskIconRotates on
      Terminal {
        Type          Input
        Position      [-35, -20]
        Direction     left
      }
      Terminal {
        Type          Input
        Position      [-35, 0]
        Direction     left
      }
      Terminal {
        Type          Input
        Position      [-35, 20]
        Direction     left
      }
      Terminal {
        Type          Output
        Position      [39, 0]
        Direction     right
      }
      Schematic {
        Location      [201, 534; 643, 733]
        ZoomFactor    1
        SliderPosition [0, 0]
        ShowBrowser   off
        BrowserWidth  100
        Component {
          Type          Input
          Name          "phase_current"
          Show          off
          Position      [60, 55]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Index"
            Value         "1"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          Input
          Name          "unused_ref"
          Show          off
          Position      [60, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Index"
            Value         "2"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          Input
          Name          "rotor_angle"
          Show          off
          Position      [60, 135]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Index"
            Value         "3"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Component {
          Type          Constant
          Name          "Phase command"
          Show          on
          Position      [160, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Value"
            Value         "phase_cmd"
            Show          on
          }
          Parameter {
            Variable      "DataType"
            Value         "10"
            Show          off
          }
        }
        Component {
          Type          Output
          Name          "phase_cmd"
          Show          on
          Position      [260, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter {
            Variable      "Index"
            Value         "4"
            Show          on
          }
          Parameter {
            Variable      "Width"
            Value         "-1"
            Show          off
          }
        }
        Connection {
          Type          Signal
          SrcComponent  "Phase command"
          SrcTerminal   1
          DstComponent  "phase_cmd"
          DstTerminal   1
        }
        Annotation {
          Name          "<html><body><p align=\\"center\\">Configured three-state phase command</p></body></html>"
          Position      [165, 45]
        }
      }
    }'''
    text = replace_balanced_block(text, 'Name          "Current controller"', controller)

    scope_marker = 'Name          "Stator Phase"'
    scope_start = text.index(scope_marker)
    scope_end = text.index("      Fourier {", scope_start)
    scope_text = text[scope_start:scope_end]
    for axis_name in ("Motor", "Machine"):
        axis_marker = scope_text.index(f'Name          "{axis_name}"')
        axis_start = scope_text.rfind("      Axis {", 0, axis_marker)
        depth = 0
        axis_end = None
        for index in range(axis_start, len(scope_text)):
            if scope_text[index] == "{":
                depth += 1
            elif scope_text[index] == "}":
                depth -= 1
                if depth == 0:
                    axis_end = index + 1
                    break
        if axis_end is None:
            raise ValueError(f"找不到 Scope 坐标轴 {axis_name} 的结束位置")
        scope_text = scope_text[:axis_start] + scope_text[axis_end:]
    scope_text = scope_text.replace('Name          "Stator Phase"', 'Name          "Phase current [A]"', 1)
    scope_text = scope_text.replace('Name          "Back EMF"', 'Name          "Line voltage [V]"', 1)
    text = text[:scope_start] + scope_text + text[scope_end:]

    voltage_output = '''    Component {
      Type          Output
      Name          "line_voltage_V"
      Show          on
      Position      [650, 270]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Index"
        Value         "6"
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
    text = text.replace(connection_marker, voltage_output + connection_marker, 1)

    emf_scope_branch = '''      Branch {
        DstComponent  "Scope"
        DstTerminal   2
      }
      Branch {
        DstComponent  "back_emf_V"
        DstTerminal   1
      }'''
    text = text.replace(
        emf_scope_branch,
        '''      DstComponent  "back_emf_V"
      DstTerminal   1''',
        1,
    )

    speed_scope_branch = '''      Branch {
        DstComponent  "Scope"
        DstTerminal   3
      }
      Branch {
        DstComponent  "speed_rad_s"
        DstTerminal   1
      }'''
    text = text.replace(
        speed_scope_branch,
        '''      DstComponent  "speed_rad_s"
      DstTerminal   1''',
        1,
    )

    torque_scope_branch = '''      Branch {
        DstComponent  "Scope"
        DstTerminal   4
      }
      Branch {
        DstComponent  "electromagnetic_torque_Nm"
        DstTerminal   1
      }'''
    text = text.replace(
        torque_scope_branch,
        '''      DstComponent  "electromagnetic_torque_Nm"
      DstTerminal   1''',
        1,
    )

    command_connection = '''    Connection {
      Type          Signal
      SrcComponent  "Current controller"
      SrcTerminal   4
      Points        [245, 95]
      Branch {
        DstComponent  "2-Level\\nIGBT\\nConv."
        DstTerminal   4
      }
      Branch {
        DstComponent  "phase_command"
        DstTerminal   1
      }
    }'''
    text = text.replace(
        command_connection,
        '''    Connection {
      Type          Signal
      SrcComponent  "Current controller"
      SrcTerminal   4
      Points        [245, 95]
      Branch {
        DstComponent  "2-Level\\nIGBT\\nConv."
        DstTerminal   4
      }
      Branch {
        DstComponent  "phase_command"
        DstTerminal   1
      }
    }''',
        1,
    )

    meter_current_connection = '    Connection {\n      Type          Signal\n      SrcComponent  "3ph Meter"\n      SrcTerminal   8'
    meter_index = text.index(meter_current_connection)
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
    }
'''
    text = text[:meter_index] + voltage_connection + text[meter_index:]

    text = text.replace(
        '''Name          "<html><body>\n<p align=\\"center\\">Chapter 01 - PLECS BL"
"DC baseline model</p></body></html>"''',
        '''Name          "<html><body>\n<p align=\\"center\\">Chapter 02 - three-state command, real IGBT bridge and BLDC winding</p></body></html>"''',
        1,
    )
    script_start = text.find("  Script {", text.rfind("  Script {"))
    if script_start >= 0:
        text = text[:script_start] + "}"

    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
