Act as an independent release reviewer.

Review mode: `series_architecture`
Track: reader-comprehension architecture
Target reader: 已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Read only this frozen packet:

- Packet manifest: `D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json`
- Externally pinned packet hash: `d6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2`

Do not inspect mutable workspace files outside the packet copy. Do not edit files. Do not read author rationale or other reviews.

Before and after review, verify the packet with:

```powershell
& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json' -ExpectedManifestSha256 'd6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2'
```

Trace target reader -> observable exit ability -> system causal map -> knowledge/prerequisite DAG -> evidence/mastery chain -> module -> one-question chapter -> worked example/scenarios -> measurable closure -> reused conclusion. Record the first point that requires guessing or backtracking, and test that first-use concepts have one owner and no future dependency.

Required checks:

- every first-use concept has purpose, input, transformation/responsibility, output, and evidence
- one smallest complete example appears before dense parameters, automation, or file details in each chapter contract
- the reader can independently reach the conclusion from displayed evidence
- limitations teach evidence interpretation rather than apologize
- the ending of each formal chapter closes the result and previews one immediate next question
- architecture approval fails when any link in the target-reader-to-evidence chain is absent, a prerequisite ID cannot resolve, or an attractive chapter lacks unique capability evidence and a measurable pass criterion

Return exactly these logical sections:

```text
packet_hash_before
packet_validation_before: PASS | FAIL plus command/result
reviewed_files: every manifest relative_path exactly once
findings: zero or more schema-complete P0-P3 findings
packet_hash_after
packet_validation_after: PASS | FAIL plus command/result
verdict: PASS | REJECT
```

Every finding must use this schema:

```text
ID: READ-01
Severity: P0 | P1 | P2 | P3
Location: exact packet file/line, heading, table, or figure
Evidence: observed value, wording, pixel fact, missing artifact, or failed teach-back
Failure mechanism: how it causes error or misunderstanding
Required correction: smallest responsibility-correct change
Verification: exact check that closes it
```

`PASS` requires zero P0-P2 findings. Any P0-P2 requires `REJECT`.
