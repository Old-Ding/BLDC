"""把第 05 章六步模型扩展为 60 ms 开环频率实验。"""

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "models/plecs/ch05_six_step_sequence/ch05_six_step_sequence.plecs"
    target_dir = root / "models/plecs/ch06_open_loop_angle"
    target = target_dir / "ch06_open_loop_angle.plecs"
    text = source.read_text(encoding="utf-8")
    text = text.replace('Name          "ch05_six_step_sequence"', 'Name          "ch06_open_loop_angle"', 1)
    text = text.replace('TimeSpan      "0.012"', 'TimeSpan      "0.06"', 1)
    text = text.replace("Chapter 05 - six-step sequence", "Chapter 06 - open-loop electrical frequency", 1)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")
    print(f"Generated {target.relative_to(root)}")


if __name__ == "__main__": main()
