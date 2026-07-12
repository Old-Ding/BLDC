"""从第 09 章 Hall 模型派生长时间测速与超时模型。"""
from pathlib import Path

def main()->None:
    root=Path(__file__).resolve().parents[1];source=root/"models/plecs/ch09_hall_sequence/ch09_hall_sequence.plecs";target_dir=root/"models/plecs/ch12_hall_speed";target=target_dir/"ch12_hall_speed.plecs";text=source.read_text(encoding="utf-8")
    text=text.replace('Name          "ch09_hall_sequence"','Name          "ch12_hall_speed"',1).replace('TimeSpan      "0.07"','TimeSpan      "0.25"',1).replace("Chapter 09 - Hall sequence and invalid states","Chapter 12 - Hall edge speed estimation",1)
    target_dir.mkdir(parents=True,exist_ok=True);target.write_text(text.replace("\r\n","\n").replace("\n","\r\n"),encoding="utf-8",newline="");print(f"Generated {target.relative_to(root)}")

if __name__=="__main__":main()
