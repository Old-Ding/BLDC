Review mode: `series_architecture`

You are the engineering architecture track in a formal independent review.

Review only this frozen packet:

`D:\1codex\BLDC\reports\review-packets\series-architecture-v2\manifest.json`

Externally pinned packet hash:

`86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e`

Target reader:

已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Rules:

- Inspect only files copied inside the frozen packet. Do not inspect mutable workspace files outside the packet.
- Do not edit any file.
- Do not read other reviews.
- Do not infer truth from polish.
- Verify the externally pinned packet hash before and after review with:

```powershell
& "C:\Users\ww\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" `
  -Manifest "D:\1codex\BLDC\reports\review-packets\series-architecture-v2\manifest.json" `
  -ExpectedManifestSha256 "86c4e4bf89bd8cd868c45d703903a01e4d5ee7425652dc20d216518ce20e275e"
```

Track contract:

Independently review only the frozen series-architecture packet. Verify its externally pinned hash before and after. Audit the real-system causal/data-flow map, engineering responsibility boundaries, knowledge DAG, prerequisite registry, exit capabilities, evidence/mastery chains, modules, chapter contracts, and integration coverage. Test whether planned evidence can prove each capability and whether every prerequisite is established before first use. Return findings, then PASS or REJECT. Do not edit or read other reviews.

Required output sections:

```text
packet_hash_before
packet_validation_before: PASS | FAIL plus command/result
reviewed_files: every manifest relative_path exactly once
findings:
  ID: ENG-01
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
