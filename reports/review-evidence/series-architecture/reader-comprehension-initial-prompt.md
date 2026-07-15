Review mode: `series_architecture`

You are the reader-comprehension architecture track in a formal independent review.

Review only this frozen packet:

`D:\1codex\BLDC\reports\review-packets\series-architecture-v1\manifest.json`

Externally pinned packet hash:

`35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9`

Target reader:

已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Rules:

- Inspect only files copied inside the frozen packet. Do not inspect mutable workspace files outside the packet.
- Do not edit any file.
- Do not read other reviews.
- Review as the stated target reader and as an author who must execute the architecture.
- Verify the externally pinned packet hash before and after review with:

```powershell
& "C:\Users\ww\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" `
  -Manifest "D:\1codex\BLDC\reports\review-packets\series-architecture-v1\manifest.json" `
  -ExpectedManifestSha256 "35ff270d0a01b915b45a08e535feebd202e78d85eecef8ee9b7c23346982bfe9"
```

Track contract:

Independently review only the frozen series-architecture packet as the stated target reader and as an author who must execute it. Verify its externally pinned hash before and after. Trace target reader -> observable exit ability -> system causal map -> knowledge/prerequisite DAG -> evidence/mastery chain -> module -> one-question chapter -> worked example/scenarios -> measurable closure -> reused conclusion. Record the first point that requires guessing or backtracking, and test that first-use concepts have one owner and no future dependency. Return findings, then PASS or REJECT. Do not edit or read other reviews.

Required output sections:

```text
packet_hash_before
packet_validation_before: PASS | FAIL plus command/result
reviewed_files: every manifest relative_path exactly once
teach_back:
  target_reader_to_exit_ability
  system_causal_map
  knowledge_prerequisite_dag
  evidence_mastery_chain
  module_to_one_question_chapter
  worked_examples_and_scenarios
  measurable_closure_and_reused_conclusion
  first_guess_or_backtrack_point
findings:
  ID: READ-01
  Severity: P0 | P1 | P2 | P3
  Location: exact packet file/line, heading, table, or figure
  Evidence: observed value, wording, pixel fact, missing artifact, or failed teach-back
  Failure mechanism: how it causes error or misunderstanding
  Required correction: smallest responsibility-correct change
  Verification: exact check that closes it
packet_hash_after
packet_validation_after: PASS | FAIL plus command/result
verdict: PASS | REJECT
```

Verdict rule:

- PASS requires zero P0-P2 findings.
- Any P0-P2 finding requires REJECT.
- Missing file coverage, hash drift, failed validation, malformed findings, or contradictory verdict makes the run invalid.
