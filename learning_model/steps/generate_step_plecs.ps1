# 生成每一步对应的 PLECS 信号教学模型。
# 为什么用统一生成脚本：每个模型的结构都保持 Clock -> CScript -> Demux -> Scope，
# 只替换唯一职责层的输出变量，避免手写多个 .plecs 时引入格式差异。

$ErrorActionPreference = 'Stop'

function ConvertTo-PlecsString {
    param(
        [string]$Value = '',

        [Parameter(Mandatory = $true)]
        [string]$Indent
    )

    $normalized = $Value -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    $lines = $normalized -split "`n", -1
    $result = New-Object System.Collections.Generic.List[string]

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $line = $line.Replace('\', '\\').Replace('"', '\"')

        if ($i -lt ($lines.Count - 1)) {
            $line = $line + '\n'
        }

        if ($i -eq 0) {
            $result.Add("${Indent}Value         `"$line`"")
        } else {
            $result.Add("${Indent}`"$line`"")
        }
    }

    return ($result -join "`r`n")
}

function New-AxisBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    return @"
      Axis {
        Name          "$Name"
        AutoScale     1
        MinValue      0
        MaxValue      1
        Signals       {}
        SignalTypes   [ ]
        Untangle      0
        KeepBaseline  off
        BaselineValue 0
      }
"@
}

function New-ScopeBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Axes
    )

    $axisBlocks = ($Axes | ForEach-Object { New-AxisBlock -Name $_ }) -join "`r`n"
    $fourierAxes = ($Axes | ForEach-Object {
@"
        Axis {
          Name          ""
          AutoScale     1
          MinValue      0
          MaxValue      1
          Signals       {}
          Untangle      0
          KeepBaseline  off
          BaselineValue 0
        }
"@
    }) -join "`r`n"

    return @"
    Component {
      Type          Scope
      Name          "Scope"
      Show          on
      Position      [380, 95]
      Direction     up
      Flipped       off
      LabelPosition south
      Axes          "$($Axes.Count)"
      TimeRange     "0"
      ScrollingMode "1"
      SingleTimeAxis "1"
      Open          "1"
      Ts            "-1"
      SampleLimit   "0"
      XAxisLabel    "Time / s"
      ShowLegend    "1"
$axisBlocks
      Fourier {
        SingleXAxis       on
        AxisLabel         "Frequency"
        Scaling           0
        PhaseDisplay      0
        ShowFourierLegend off
$fourierAxes
      }
    }
"@
}

function New-CScriptBlock {
    param(
        [Parameter(Mandatory = $true)]
        [int]$NumOutputs,

        [string]$Declarations = '',

        [Parameter(Mandatory = $true)]
        [string]$OutputFcn
    )

    $declarationsValue = ConvertTo-PlecsString -Value $Declarations -Indent '        '
    $outputValue = ConvertTo-PlecsString -Value $OutputFcn -Indent '        '

    return @"
    Component {
      Type          CScript
      Name          "StepLogic"
      Show          on
      Position      [210, 95]
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
        Value         "$NumOutputs"
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
        Value         "[1]"
        Show          off
      }
      Parameter {
        Variable      "Ts"
        Value         "-1"
        Show          off
      }
      Parameter {
        Variable      "Parameters"
        Value         ""
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
$declarationsValue
        Show          off
      }
      Parameter {
        Variable      "StartFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "OutputFcn"
$outputValue
        Show          off
      }
      Parameter {
        Variable      "UpdateFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "DerivativeFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "TerminateFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "StoreCustomStateFcn"
        Value         ""
        Show          off
      }
      Parameter {
        Variable      "RestoreCustomStateFcn"
        Value         ""
        Show          off
      }
    }
"@
}

function New-StepModel {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModelName,

        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [string]$OutFile,

        [Parameter(Mandatory = $true)]
        [string[]]$Axes,

        [Parameter(Mandatory = $true)]
        [string]$OutputFcn,

        [string]$Declarations = ''
    )

    $scope = New-ScopeBlock -Axes $Axes
    $script = New-CScriptBlock -NumOutputs $Axes.Count -Declarations $Declarations -OutputFcn $OutputFcn
    $demuxWidth = '[' + (($Axes | ForEach-Object { '1' }) -join ' ') + ']'
    $connections = New-Object System.Collections.Generic.List[string]

    $connections.Add(@"
    Connection {
      Type          Signal
      SrcComponent  "Clock"
      SrcTerminal   1
      DstComponent  "StepLogic"
      DstTerminal   1
    }
"@)

    $connections.Add(@"
    Connection {
      Type          Signal
      SrcComponent  "StepLogic"
      SrcTerminal   2
      DstComponent  "Demux"
      DstTerminal   1
    }
"@)

    for ($i = 0; $i -lt $Axes.Count; $i++) {
        $srcTerminal = $i + 2
        $dstTerminal = $i + 1
        $connections.Add(@"
    Connection {
      Type          Signal
      SrcComponent  "Demux"
      SrcTerminal   $srcTerminal
      DstComponent  "Scope"
      DstTerminal   $dstTerminal
    }
"@)
    }

    $connectionText = $connections -join "`r`n"

    $model = @"
Plecs {
  Name          "$ModelName"
  Version       "4.7"
  CircuitModel  "ContStateSpace"
  StartTime     "0.0"
  TimeSpan      "1.0"
  Timeout       ""
  Solver        "dopri"
  MaxStep       "1e-4"
  InitStep      "-1"
  FixedStep     "1e-4"
  Refine        "1"
  ZCStepSize    "1e-9"
  RelTol        "1e-3"
  AbsTol        "-1"
  TurnOnThreshold "0"
  SyncFixedStepTasks "2"
  UseSingleCommonBaseRate "2"
  LossVariableLimitExceededMsg "3"
  NegativeSwitchLossMsg "3"
  DivisionByZeroMsg "2"
  StiffnessDetectionMsg "2"
  MaxConsecutiveZCs "1000"
  AlgebraicLoopWithStateMachineMsg "2"
  AssertionAction "1"
  InitializationCommands ""
  InitialState  "1"
  SystemState   ""
  TaskingMode   "1"
  TaskConfigurations ""
  CodeGenParameterInlining "2"
  CodeGenFloatingPointFormat "2"
  CodeGenAbsTimeUsageMsg "3"
  CodeGenBaseName ""
  CodeGenOutputDir ""
  CodeGenExtraOpts ""
  CodeGenTarget "Generic"
  CodeGenTargetSettings ""
  ExtendedMatrixPrecision "1"
  MatrixSignificanceCheck "2"
  EnableStateSpaceSplitting "2"
  DisplayStateSpaceSplitting "1"
  DiscretizationMethod "2"
  ExternalModeSettings ""
  AlgebraicLoopMethod "1"
  AlgebraicLoopTolerance "1e-6"
  ScriptsDialogGeometry ""
  ScriptsDialogSplitterPos "0"
  Schematic {
    Location      [0, 53; 620, 360]
    ZoomFactor    1
    SliderPosition [0, 0]
    ShowBrowser   off
    BrowserWidth  100
$scope
    Component {
      Type          Clock
      Name          "Clock"
      Show          on
      Position      [75, 95]
      Direction     right
      Flipped       off
      LabelPosition south
    }
$script
    Component {
      Type          SignalDemux
      Name          "Demux"
      Show          on
      Position      [290, 95]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter {
        Variable      "Width"
        Value         "$demuxWidth"
        Show          off
      }
    }
$connectionText
    Annotation {
      Name          "<html><body><p align=\"center\">$Title</p></body></html>"
      Position      [210, 30]
    }
  }
}
"@

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $normalized = $model -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    $normalized = $normalized -replace "`n", "`r`n"
    [System.IO.File]::WriteAllText((Resolve-Path -Path (Split-Path -Path $OutFile -Parent)).Path + [System.IO.Path]::DirectorySeparatorChar + (Split-Path -Path $OutFile -Leaf), $normalized, $utf8NoBom)
}

function Convert-FileToCrLfUtf8 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $resolved = Resolve-Path -Path $Path
    $text = [System.IO.File]::ReadAllText($resolved, [System.Text.Encoding]::UTF8)
    $text = $text -replace "`r`n", "`n"
    $text = $text -replace "`r", "`n"
    $text = $text -replace "`n", "`r`n"
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($resolved, $text, $utf8NoBom)
}

$models = @(
    @{
        ModelName = 'step_01_three_phase_bridge'
        Title = 'Step 01 - three phase bridge state'
        OutFile = '.\step_01_three_phase_bridge\step_01_three_phase_bridge.plecs'
        Axes = @('AH', 'BH', 'CH', 'AL', 'BL', 'CL', 'A_state', 'B_state', 'C_state', 'shoot_through')
        OutputFcn = @'
double t = Input(0);
int scenario = ((int)(t / 0.1)) % 4;
double ah = 0, bh = 0, ch = 0, al = 0, bl = 0, cl = 0;
double a = 0, b = 0, c = 0, shoot = 0;

if (scenario == 0) {
  ah = 1; bl = 1;
} else if (scenario == 1) {
  bh = 1; cl = 1;
} else if (scenario == 2) {
  ch = 1; al = 1;
} else {
  ah = 1; al = 1;
}

if (ah && al) { a = 2; shoot = 1; } else if (ah) { a = 1; } else if (al) { a = -1; }
if (bh && bl) { b = 2; shoot = 1; } else if (bh) { b = 1; } else if (bl) { b = -1; }
if (ch && cl) { c = 2; shoot = 1; } else if (ch) { c = 1; } else if (cl) { c = -1; }

Output(0) = ah;
Output(1) = bh;
Output(2) = ch;
Output(3) = al;
Output(4) = bl;
Output(5) = cl;
Output(6) = a;
Output(7) = b;
Output(8) = c;
Output(9) = shoot;
'@
    },
    @{
        ModelName = 'step_02_six_step_table'
        Title = 'Step 02 - six step table'
        OutFile = '.\step_02_six_step_table\step_02_six_step_table.plecs'
        Axes = @('step', 'AH', 'BH', 'CH', 'AL', 'BL', 'CL')
        OutputFcn = @'
double t = Input(0);
int step = ((int)(t / 0.08)) % 6;
double ah = 0, bh = 0, ch = 0, al = 0, bl = 0, cl = 0;

if (step == 0) { ah = 1; bl = 1; }
else if (step == 1) { ah = 1; cl = 1; }
else if (step == 2) { bh = 1; cl = 1; }
else if (step == 3) { bh = 1; al = 1; }
else if (step == 4) { ch = 1; al = 1; }
else { ch = 1; bl = 1; }

Output(0) = step;
Output(1) = ah;
Output(2) = bh;
Output(3) = ch;
Output(4) = al;
Output(5) = bl;
Output(6) = cl;
'@
    },
    @{
        ModelName = 'step_03_open_loop_commutation'
        Title = 'Step 03 - open loop commutation'
        OutFile = '.\step_03_open_loop_commutation\step_03_open_loop_commutation.plecs'
        Axes = @('ticks_per_step', 'step', 'elec_angle_deg', 'AH', 'BH', 'CH', 'AL', 'BL', 'CL')
        OutputFcn = @'
double t = Input(0);
double ticks_per_step = 80.0;
int step = ((int)(t / 0.08)) % 6;
double ah = 0, bh = 0, ch = 0, al = 0, bl = 0, cl = 0;

if (step == 0) { ah = 1; bl = 1; }
else if (step == 1) { ah = 1; cl = 1; }
else if (step == 2) { bh = 1; cl = 1; }
else if (step == 3) { bh = 1; al = 1; }
else if (step == 4) { ch = 1; al = 1; }
else { ch = 1; bl = 1; }

Output(0) = ticks_per_step;
Output(1) = step;
Output(2) = step * 60.0;
Output(3) = ah;
Output(4) = bh;
Output(5) = ch;
Output(6) = al;
Output(7) = bl;
Output(8) = cl;
'@
    },
    @{
        ModelName = 'step_04_hall_commutation'
        Title = 'Step 04 - hall commutation'
        OutFile = '.\step_04_hall_commutation\step_04_hall_commutation.plecs'
        Axes = @('HallA', 'HallB', 'HallC', 'hall_state', 'valid', 'AH', 'BH', 'CH', 'AL', 'BL', 'CL')
        OutputFcn = @'
double t = Input(0);
int idx = ((int)(t / 0.08)) % 6;
int hall = 5;
double ah = 0, bh = 0, ch = 0, al = 0, bl = 0, cl = 0;
double valid = 1;

if (idx == 0) { hall = 5; ah = 1; bl = 1; }
else if (idx == 1) { hall = 1; ah = 1; cl = 1; }
else if (idx == 2) { hall = 3; bh = 1; cl = 1; }
else if (idx == 3) { hall = 2; bh = 1; al = 1; }
else if (idx == 4) { hall = 6; ch = 1; al = 1; }
else { hall = 4; ch = 1; bl = 1; }

Output(0) = hall & 1;
Output(1) = (hall >> 1) & 1;
Output(2) = (hall >> 2) & 1;
Output(3) = hall;
Output(4) = valid;
Output(5) = ah;
Output(6) = bh;
Output(7) = ch;
Output(8) = al;
Output(9) = bl;
Output(10) = cl;
'@
    },
    @{
        ModelName = 'step_05_pwm_duty'
        Title = 'Step 05 - high side pwm duty'
        OutFile = '.\step_05_pwm_duty\step_05_pwm_duty.plecs'
        Axes = @('step', 'duty', 'carrier', 'AH_base', 'AH_pwm', 'BH_pwm', 'CH_pwm', 'AL', 'BL', 'CL')
        OutputFcn = @'
double t = Input(0);
int step = ((int)(t / 0.12)) % 6;
int duty_mode = ((int)(t / 0.33)) % 3;
double duty = duty_mode == 0 ? 0.2 : (duty_mode == 1 ? 0.5 : 0.8);
double carrier = t * 200.0 - (int)(t * 200.0);
double pwm_on = carrier < duty ? 1.0 : 0.0;
double ah = 0, bh = 0, ch = 0, al = 0, bl = 0, cl = 0;

if (step == 0) { ah = 1; bl = 1; }
else if (step == 1) { ah = 1; cl = 1; }
else if (step == 2) { bh = 1; cl = 1; }
else if (step == 3) { bh = 1; al = 1; }
else if (step == 4) { ch = 1; al = 1; }
else { ch = 1; bl = 1; }

Output(0) = step;
Output(1) = duty;
Output(2) = carrier;
Output(3) = ah;
Output(4) = ah * pwm_on;
Output(5) = bh * pwm_on;
Output(6) = ch * pwm_on;
Output(7) = al;
Output(8) = bl;
Output(9) = cl;
'@
    },
    @{
        ModelName = 'step_06_speed_estimation'
        Title = 'Step 06 - hall speed estimation'
        OutFile = '.\step_06_speed_estimation\step_06_speed_estimation.plecs'
        Axes = @('edge_period_ms', 'pole_pairs', 'edges_per_rev', 'rpm')
        OutputFcn = @'
double t = Input(0);
int mode = ((int)(t / 0.25)) % 3;
double pole_pairs = 4.0;
double edge_period_s = mode == 0 ? 0.006 : (mode == 1 ? 0.003 : 0.0015);
double edges_per_rev = pole_pairs * 6.0;
double rpm = 60.0 / (edge_period_s * edges_per_rev);

Output(0) = edge_period_s * 1000.0;
Output(1) = pole_pairs;
Output(2) = edges_per_rev;
Output(3) = rpm;
'@
    },
    @{
        ModelName = 'step_07_speed_pi'
        Title = 'Step 07 - speed PI output duty'
        OutFile = '.\step_07_speed_pi\step_07_speed_pi.plecs'
        Axes = @('target_rpm', 'actual_rpm', 'error', 'integral_view', 'duty')
        OutputFcn = @'
double t = Input(0);
double target = t < 0.1 ? 0.0 : 1000.0;
double actual = 0.0;
double error = 0.0;
double integral_view = 0.0;
double duty = 0.0;
double run_t = t - 0.1;

if (run_t > 0.0) {
  actual = run_t < 0.6 ? run_t / 0.6 * 850.0 : 850.0 + (run_t - 0.6) / 0.3 * 150.0;
  if (actual > 1000.0) { actual = 1000.0; }
}

error = target - actual;
integral_view = error * 0.2;
if (integral_view > 120.0) { integral_view = 120.0; }
if (integral_view < 0.0) { integral_view = 0.0; }

duty = 0.0003 * error + 0.002 * integral_view;
if (duty > 0.9) { duty = 0.9; }
if (duty < 0.0) { duty = 0.0; }

Output(0) = target;
Output(1) = actual;
Output(2) = error;
Output(3) = integral_view;
Output(4) = duty;
'@
    }
)

Push-Location -Path $PSScriptRoot
try {
    foreach ($model in $models) {
        New-StepModel `
            -ModelName $model.ModelName `
            -Title $model.Title `
            -OutFile $model.OutFile `
            -Axes $model.Axes `
            -OutputFcn $model.OutputFcn
    }

    $sourceHallCode = Join-Path -Path (Split-Path -Path $PSScriptRoot -Parent) -ChildPath 'six_step_commutation_hall.c'
    $targetHallCode = Join-Path -Path $PSScriptRoot -ChildPath 'step_04_hall_commutation\six_step_commutation_hall.c'
    Copy-Item -Path $sourceHallCode -Destination $targetHallCode -Force
    Convert-FileToCrLfUtf8 -Path $targetHallCode

    $sourceFullModel = Join-Path -Path (Split-Path -Path $PSScriptRoot -Parent) -ChildPath 'bldc_six_step_learning.plecs'
    $targetFullModel = Join-Path -Path $PSScriptRoot -ChildPath 'step_08_plecs_full_model\step_08_plecs_full_model.plecs'
    Copy-Item -Path $sourceFullModel -Destination $targetFullModel -Force
    Set-ItemProperty -Path $targetFullModel -Name IsReadOnly -Value $false
    Convert-FileToCrLfUtf8 -Path $targetFullModel
} finally {
    Pop-Location
}

Write-Output 'Generated step PLECS models.'
