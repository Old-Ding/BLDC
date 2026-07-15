# 第 12 章 Hall 测速事件 oracle

| 用例 | 极对数 | 最后转移分类 | 合法边沿数 | 实测末值/rad/s | 期望末值/rad/s | 结果 |
|---|---:|---|---:|---:|---:|---|
| pole_pairs_1_forward | 1 | legal_forward | 2 | 104.719755 | 104.719755 | PASS |
| pole_pairs_4_forward | 4 | legal_forward | 2 | 26.179939 | 26.179939 | PASS |
| reverse | 1 | legal_reverse | 2 | -104.719755 | -104.719755 | PASS |
| invalid_ignored | 1 | legal_forward | 2 | 104.719755 | 104.719755 | PASS |
| non_adjacent_ignored | 1 | legal_forward | 2 | 104.719755 | 104.719755 | PASS |
| hold_ignored | 1 | legal_forward | 2 | 104.719755 | 104.719755 | PASS |
| timeout_recovery | 1 | legal_forward | 3 | 104.719755 | 104.719755 | PASS |

## 责任边界

Hall 解码只把相邻合法跳变交给测速；`invalid_code`、`non_adjacent` 和 `hold` 不更新测速基准。
测速层使用 `omega_m = s * (pi/3)/(pole_pairs * delta_t)`，因此同一 Hall 边沿间隔在 4 极对时机械速度是 1 极对的四分之一。
