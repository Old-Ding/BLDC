Act as the independent reader-comprehension architecture reviewer for a frozen series-architecture packet.

Review mode: series_architecture
Packet manifest: D:\1codex\BLDC\reports\review-packets\series-architecture-v3\manifest.json
Externally pinned packet hash: 3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40
Intended reader: 已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Isolation rules:
- Inspect only the frozen packet under D:\1codex\BLDC\reports\review-packets\series-architecture-v3.
- Do not inspect mutable workspace source files outside that packet.
- Do not edit any files.
- Do not read other reviews or author notes.
- You may run the packet verifier script only to validate the manifest:
  & "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v3\manifest.json' -ExpectedManifestSha256 '3a187c22cc0ca28f381e24810c4d41b93f3cb4a291af14335da8b31fe5a6ac40'

Reader-comprehension architecture contract:
Read as the stated target reader and as an author who must execute the plan. Trace target reader -> observable exit ability -> system causal map -> knowledge/prerequisite DAG -> evidence/mastery chain -> module -> one-question chapter -> worked example/scenarios -> measurable closure -> reused conclusion. Record the first point where a reader must guess or backtrack. Run a teach-back: core question, minimum causal model, one worked example, what each major figure/evidence chain proves, and what the evidence does not prove. Check that first-use concepts have one owner and no future dependency.

Required output schema. Return exactly these logical sections:
packet_hash_before
packet_validation_before: PASS | FAIL plus command/result
reviewed_files: every manifest relative_path exactly once
findings: zero or more findings, each with ID, Severity(P0/P1/P2/P3), Location, Evidence, Failure mechanism, Required correction, Verification
packet_hash_after
packet_validation_after: PASS | FAIL plus command/result
verdict: PASS | REJECT

PASS is allowed only if there are zero P0-P2 findings and packet validation passes before and after. Any P0-P2 finding requires REJECT.
