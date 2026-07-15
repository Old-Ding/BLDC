# ui-writing initial output

状态：TIMED_OUT

| 字段 | 值 |
|---|---|
| agent id | `019f6478-8fae-7451-b507-1372d9bf020b` |
| requested model | `gpt-5.6-terra` |
| fork_context | `false` |
| timeout | 10 minutes |
| close result | previous_status=`running` |

本轨在 10 分钟上限内未返回完整 `packet_hash_before`、`reviewed_files`、`findings`、`packet_hash_after` 和 `verdict`，按协议记为 `TIMED_OUT`，不能计为 PASS。
