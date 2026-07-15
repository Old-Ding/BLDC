Act as an independent release reviewer.

Review mode: `series_architecture`
Track: engineering architecture
Target reader: 已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Read only this frozen packet:

- Packet manifest: `D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json`
- Externally pinned packet hash: `d6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2`

Do not inspect mutable workspace files outside the packet copy. Do not edit files. Do not read other reviews.

Before and after review, verify the packet with:

```powershell
& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json' -ExpectedManifestSha256 'd6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2'
```

Audit the real-system causal/data-flow map, engineering responsibility boundaries, knowledge DAG, prerequisite registry, exit capabilities, evidence/mastery chains, modules, chapter contracts, and integration coverage. Test whether planned evidence can prove each capability and whether every prerequisite is established before first use.

Required checks:

- formulas, units, constants, scenarios, filenames, plots, and report rows agree
- every important claim maps to code, data, real-tool evidence, or an explicit assumption
- simulation, compile, firmware, HIL, and hardware claims do not exceed evidence
- wrappers orchestrate evidence but do not secretly own behavioral truth
- model, controller, protection, state machine, and publishing responsibilities stay separated
- no duplicate defensive condition exists outside the unique responsibility layer
- the Hall interface, speed estimate, PI duty, PWM/deadtime, enable/fault, and gate synthesis chain has one clear owner per responsibility

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
ID: ENG-01
Severity: P0 | P1 | P2 | P3
Location: exact packet file/line, heading, table, or figure
Evidence: observed value, wording, pixel fact, missing artifact, or failed teach-back
Failure mechanism: how it causes error or misunderstanding
Required correction: smallest responsibility-correct change
Verification: exact check that closes it
```

`PASS` requires zero P0-P2 findings. Any P0-P2 requires `REJECT`.
