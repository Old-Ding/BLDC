"""从第 13 章速度 PI 模型派生第一季完整 Hall 六步闭环模型。"""
from pathlib import Path

def main()->None:
    root=Path(__file__).resolve().parents[1];source=root/"models/plecs/ch13_speed_pi/ch13_speed_pi.plecs";target_dir=root/"models/plecs/ch14_complete_hall_closed_loop";target=target_dir/"ch14_complete_hall_closed_loop.plecs";text=source.read_text(encoding="utf-8")
    text=text.replace('Name          "ch13_speed_pi"','Name          "ch14_complete_hall_closed_loop"',1).replace('TimeSpan      "0.2"','TimeSpan      "0.5"',1).replace('TimeRange     "0.25"','TimeRange     "0.5"',1)
    text=text.replace('"load_step_time_s = 1;"','"load_step_time_s = 1;\\n"\n"hall_invalid_start_s = 1;\\n"\n"hall_invalid_end_s = 1;\\n"\n"hall_speed_alpha = 0.25;\\n"\n"hall_speed_timeout_s = 0.05;"',1)
    text=text.replace('speed_kp, speed_ki, duty_min, duty_max, antiwindup_enable"','speed_kp, speed_ki, duty_min, duty_max, antiwindup_enable, hall_invalid_start_s, hall_invalid_end_s, hall_speed_alpha, hall_speed_timeout_s"',1)
    text=text.replace('Parameter { Variable "Declarations" Value "" Show off }','Parameter { Variable "Declarations" Value "static int hall_est_initialized=0, hall_last_sector=0, hall_edge_count=0, hall_was_invalid=0; static double hall_last_edge_time=0, hall_speed_feedback=0;" Show off }',1)
    text=text.replace('Parameter { Variable "StartFcn" Value "" Show off }','Parameter { Variable "StartFcn" Value "hall_est_initialized=0;hall_last_sector=0;hall_edge_count=0;hall_was_invalid=0;hall_last_edge_time=0;hall_speed_feedback=0;" Show off }',1)
    text=text.replace('''double t=CurrentTime; double speed=Input(0); double theta=Input(1)*ParamRealData(0,0)+ParamRealData(1,0); double target=t<ParamRealData(9,0)?ParamRealData(7,0):ParamRealData(8,0);''','''double t=CurrentTime; double theta=Input(1)*ParamRealData(0,0)+ParamRealData(1,0); double target=t<ParamRealData(9,0)?ParamRealData(7,0):ParamRealData(8,0);''',1)
    text=text.replace('''double duty=ParamRealData(10,0)*(target-speed)+ContState(0); if(duty<ParamRealData(12,0))duty=ParamRealData(12,0); if(duty>ParamRealData(13,0))duty=ParamRealData(13,0);''','',1)
    old_sector='''double two_pi=6.283185307179586;while(theta>=two_pi)theta-=two_pi;while(theta<0)theta+=two_pi;int sector=(int)(theta/(two_pi/6.0));int step=(sector+(int)ParamRealData(2,0))%6;if(step<0)step+=6;if(ParamRealData(3,0)<0&&step!=0)step=6-step;'''
    new_sector='''double two_pi=6.283185307179586;while(theta>=two_pi)theta-=two_pi;while(theta<0)theta+=two_pi;int sector=(int)(theta/(two_pi/6.0));int invalid=t>=ParamRealData(15,0)&&t<ParamRealData(16,0);if(!hall_est_initialized){hall_est_initialized=1;hall_last_sector=sector;hall_last_edge_time=t;hall_speed_feedback=0;}if(invalid)hall_was_invalid=1;if(!invalid&&hall_was_invalid){hall_was_invalid=0;hall_last_sector=sector;hall_last_edge_time=t;hall_edge_count=0;hall_speed_feedback=0;}else if(IsMajorStep&&!invalid&&sector!=hall_last_sector){int delta=(sector-hall_last_sector+6)%6;double dt=t-hall_last_edge_time;if(delta==1||delta==5){if(hall_edge_count==0){hall_edge_count=1;hall_speed_feedback=0;}else if(dt>1e-9){double raw=(delta==1?1:-1)*(two_pi/6.0)/(ParamRealData(0,0)*dt);hall_speed_feedback=hall_edge_count==1?raw:ParamRealData(17,0)*raw+(1-ParamRealData(17,0))*hall_speed_feedback;hall_edge_count++;}}hall_last_sector=sector;hall_last_edge_time=t;}if(t-hall_last_edge_time>=ParamRealData(18,0))hall_speed_feedback=0;double speed=hall_speed_feedback;double duty=ParamRealData(10,0)*(target-speed)+ContState(0);if(duty<ParamRealData(12,0))duty=ParamRealData(12,0);if(duty>ParamRealData(13,0))duty=ParamRealData(13,0);int step=(sector+(int)ParamRealData(2,0))%6;if(step<0)step+=6;if(ParamRealData(3,0)<0&&step!=0)step=6-step;''';text=text.replace(old_sector,new_sector,1)
    old='''static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}};for(int k=0;k<3;k++){double base=table[step][k];Output(k)=base>0?(high_on?1:0):(base<0?-1:0);if(t<blank_until||ParamRealData(4,0)<0.5)Output(k)=0;}'''
    new='''static const double table[6][3]={{1,-1,0},{1,0,-1},{0,1,-1},{-1,1,0},{-1,0,1},{0,-1,1}};for(int k=0;k<3;k++){double base=table[step][k];Output(k)=base>0?(high_on?1:0):(base<0?-1:0);if(t<blank_until||ParamRealData(4,0)<0.5||invalid)Output(k)=0;}Output(3)=hall_speed_feedback;''';text=text.replace(old,new,1)
    old_deriv='''int freeze=ParamRealData(14,0)>0.5&&((u>=ParamRealData(13,0)&&e>0)||(u<=ParamRealData(12,0)&&e<0));ContDeriv(0)=freeze?0:ParamRealData(11,0)*e;'''
    new_deriv='''speed=hall_speed_feedback;int invalid=t>=ParamRealData(15,0)&&t<ParamRealData(16,0);e=target-speed;u=ParamRealData(10,0)*e+ContState(0);int freeze=invalid||(ParamRealData(14,0)>0.5&&((u>=ParamRealData(13,0)&&e>0)||(u<=ParamRealData(12,0)&&e<0)));ContDeriv(0)=freeze?0:ParamRealData(11,0)*e;''';text=text.replace(old_deriv,new_deriv,1)
    text=text.replace('Parameter { Variable "NumOutputs" Value "3" Show off }','Parameter { Variable "NumOutputs" Value "4" Show off }',1)
    text=text.replace('''      Terminal {
        Type          Output
        Position      [39, 0]
        Direction     right
      }''','''      Terminal {
        Type          Output
        Position      [39, -10]
        Direction     right
      }
      Terminal {
        Type          Output
        Position      [39, 10]
        Direction     right
      }''',1)
    text=text.replace('''        Component {
          Type          Output
          Name          "phase_cmd"''','''        Component {
          Type          SignalDemux
          Name          "control_output_demux"
          Show          on
          Position      [245, 95]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Width" Value "[3 1]" Show off }
        }
        Component {
          Type          Output
          Name          "phase_cmd"''',1)
    text=text.replace('''          Position      [260, 95]''','''          Position      [305, 80]''',1)
    hall_output='''        Component {
          Type          Output
          Name          "hall_speed_feedback"
          Show          on
          Position      [305, 120]
          Direction     right
          Flipped       off
          LabelPosition south
          Parameter { Variable "Index" Value "5" Show on }
          Parameter { Variable "Width" Value "1" Show off }
        }
'''
    text=text.replace('''        Connection {
          Type          Signal
          SrcComponent  "mechanical_speed"''',hall_output+'''        Connection {
          Type          Signal
          SrcComponent  "mechanical_speed"''',1)
    text=text.replace('''        Connection {
          Type          Signal
          SrcComponent  "Speed PI Hall PWM"
          SrcTerminal   2
          DstComponent  "phase_cmd"
          DstTerminal   1
        }''','''        Connection {
          Type          Signal
          SrcComponent  "Speed PI Hall PWM"
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
          DstComponent  "hall_speed_feedback"
          DstTerminal   1
        }''',1)
    text=text.replace('''  Terminal {
    Type          Output
    Index         "7"
  }''','''  Terminal {
    Type          Output
    Index         "7"
  }
  Terminal {
    Type          Output
    Index         "8"
  }''',1)
    hall_top_output='''    Component {
      Type          Output
      Name          "hall_speed_feedback_rad_s"
      Show          on
      Position      [650, 350]
      Direction     right
      Flipped       off
      LabelPosition south
      Parameter { Variable "Index" Value "8" Show on }
      Parameter { Variable "Width" Value "1" Show off }
    }
'''
    text=text.replace('''    Connection {
      Type          Signal
      SrcComponent  "Clock"''',hall_top_output+'''    Connection {
      Type          Signal
      SrcComponent  "Clock"''',1)
    hall_top_connection='''    Connection {
      Type          Signal
      SrcComponent  "Current controller"
      SrcTerminal   5
      DstComponent  "hall_speed_feedback_rad_s"
      DstTerminal   1
    }
'''
    text=text.replace('''    Connection {
      Type          Signal
      SrcComponent  "Udc"''',hall_top_connection+'''    Connection {
      Type          Signal
      SrcComponent  "Udc"''',1)
    text=text.replace('Name          "Mechanical speed under PI control"','Name          "Complete Hall closed-loop speed"',1).replace("Chapter 13 - speed PI saturation and anti-windup","Chapter 14 - complete Hall six-step closed loop",1)
    target_dir.mkdir(parents=True,exist_ok=True);target.write_text(text.replace("\r\n","\n").replace("\n","\r\n"),encoding="utf-8",newline="");print(f"Generated {target.relative_to(root)}")

if __name__=="__main__":main()
