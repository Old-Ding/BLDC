Act as an independent release reviewer.

Review mode: `series_architecture`
Track: UI/writing architecture
Target reader: 已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Read only this frozen packet:

- Packet manifest: `D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json`
- Externally pinned packet hash: `d6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2`

Do not inspect mutable workspace files outside the packet copy. Do not edit files. Do not read other reviews.

Before and after review, verify the packet with:

```powershell
& "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v7-local\manifest.json' -ExpectedManifestSha256 'd6359403cf2d4dfb3abb8f479c42868d9b3dc33f48c9d62ceac4ef7210b1c4c2'
```

Inspect every desktop/mobile top-middle-bottom render, every targeted diagram PNG in `diagram_matrix`, and every section-boundary PNG in `contract_matrix`. Check progressive disclosure, navigation from the compact chapter index, diagram nodes/edges/labels, tables, detailed contracts, evidence/mastery mapping, bidirectional coverage, mobile overflow, terminology consistency, and separation of internal contracts from public teaching prose.

You must cite dimensions and visible facts from:

- all six viewport renders
- all four diagram renders
- all eight contract renders

Required checks:

- every viewport-matrix row resolves to an inspected screenshot
- figures are nonblank, legible, correctly cropped, and adjacent to interpretation
- every formal evidence figure has an adjacent caption naming object/scenario and supported conclusion
- labels, legends, units, colors, tables, headings, and code blocks fit desktop and mobile
- first screen shows the concrete problem and minimum mental model
- visual order follows phenomenon -> core relation -> comparison -> diagnostic detail
- no review notes, placeholders, local paths, or defensive curriculum prose remain in public-facing materials
- missing or uninspected render evidence is a blocker

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
ID: UI-01
Severity: P0 | P1 | P2 | P3
Location: exact packet file/line, heading, table, or figure
Evidence: observed value, wording, pixel fact, missing artifact, or failed teach-back
Failure mechanism: how it causes error or misunderstanding
Required correction: smallest responsibility-correct change
Verification: exact check that closes it
```

`PASS` requires zero P0-P2 findings. Any P0-P2 requires `REJECT`.
