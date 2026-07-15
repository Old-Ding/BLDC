"""从第 09 章 Hall 模型派生长时间测速与超时模型。"""
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs"
    target_dir = root / "models/plecs/ch12_hall_speed"
    target = target_dir / "ch12_hall_speed.plecs"
    text = source.read_text(encoding="utf-8")
    text = (
        text.replace('Name          "ch09_hall_sequence"', 'Name          "ch12_hall_speed"', 1)
        .replace('TimeSpan      "0.07"', 'TimeSpan      "0.25"', 1)
        .replace("Chapter 09 - Hall sequence and invalid states", "Chapter 12 - Hall edge speed estimation", 1)
    )
    text = text.replace(
        '"invalid_code = 0;"',
        '"invalid_code = 0;\\n"\n"hall_speed_alpha = 0.25;\\n"\n"hall_speed_timeout_s = 0.05;"',
        1,
    )
    text = text.replace(
        'Parameter { Variable "NumOutputs" Value "5" Show off }',
        'Parameter { Variable "NumOutputs" Value "13" Show off }',
        1,
    )
    text = text.replace(
        'Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, force_invalid, invalid_code" Show off }',
        'Parameter { Variable "Parameters" Value "pole_pairs, hall_offset_rad, force_invalid, invalid_code, hall_speed_alpha, hall_speed_timeout_s" Show off }',
        1,
    )
    text = text.replace(
        'Parameter { Variable "Declarations" Value "" Show off }',
        'Parameter { Variable "Declarations" Value "static int previous_code=-1, legal_edge_count=0, timed_out_active=0; static double last_edge_time=0, raw_speed=0, filtered_speed=0;" Show off }',
        1,
    )
    text = text.replace(
        'Parameter { Variable "StartFcn" Value "" Show off }',
        'Parameter { Variable "StartFcn" Value "previous_code=-1;legal_edge_count=0;timed_out_active=0;last_edge_time=0;raw_speed=0;filtered_speed=0;" Show off }',
        1,
    )
    text = text.replace(
        '''Output(0)=Input(0); Output(1)=(code>>2)&1; Output(2)=(code>>1)&1; Output(3)=code&1; Output(4)=(code!=0&&code!=7);''',
        '''int valid=(code==5||code==1||code==3||code==2||code==6||code==4); int cls=valid?0:2; int direction=0; int legal=0;
"
        "if(valid&&previous_code>=0&&code!=previous_code){int pi=-1,ci=-1; static const int seq[6]={5,1,3,2,6,4}; for(int i=0;i<6;i++){if(seq[i]==previous_code)pi=i;if(seq[i]==code)ci=i;} int delta=(ci-pi+6)%6; if(delta==1){cls=1;direction=1;legal=1;}else if(delta==5){cls=-1;direction=-1;legal=1;}else{cls=3;}}
"
        "if(IsMajorStep){if(valid&&previous_code<0){previous_code=code;last_edge_time=CurrentTime;}else if(valid&&legal){double dt=CurrentTime-last_edge_time; if(timed_out_active||legal_edge_count==0){raw_speed=0;filtered_speed=0;}else if(dt>1e-9){raw_speed=direction*1.0471975511965976/(ParamRealData(0,0)*dt); filtered_speed=(legal_edge_count==1)?raw_speed:ParamRealData(4,0)*raw_speed+(1-ParamRealData(4,0))*filtered_speed;} legal_edge_count++; previous_code=code; last_edge_time=CurrentTime; timed_out_active=0;}}
"
        "int timeout=((previous_code<0&&CurrentTime>=ParamRealData(5,0))||(previous_code>=0&&CurrentTime-last_edge_time>=ParamRealData(5,0))); if(timeout){raw_speed=0;filtered_speed=0;timed_out_active=1;}
"
        "Output(0)=Input(0);Output(1)=(code>>2)&1;Output(2)=(code>>1)&1;Output(3)=code&1;Output(4)=valid;Output(5)=code;Output(6)=cls;Output(7)=direction;Output(8)=legal;Output(9)=raw_speed;Output(10)=filtered_speed;Output(11)=timeout;Output(12)=legal_edge_count;''',
        1,
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__":
    main()
