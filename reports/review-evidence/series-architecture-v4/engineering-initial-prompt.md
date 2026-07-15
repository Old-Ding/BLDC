Act as the independent engineering architecture reviewer for a frozen series-architecture packet.

Review mode: series_architecture
Packet manifest: D:\1codex\BLDC\reports\review-packets\series-architecture-v4\manifest.json
Externally pinned packet hash: 120f74ef0829dddc9506042dcd138f97bcc17caafc45f08bb0b8396ee69f3605
Intended reader: 已经接触过电机、功率电子或嵌入式控制，但还不能把 BLDC 的三相桥、换相、Hall、PWM、测速和速度环串成可验证工程链路的读者。

Isolation rules:
- Inspect only the frozen packet under D:\1codex\BLDC\reports\review-packets\series-architecture-v4.
- Do not inspect mutable workspace source files outside that packet.
- Do not edit any files.
- Do not read other reviews or author notes.
- You may run the packet verifier script only to validate the manifest:
  & "$env:USERPROFILE\.codex\skills\technical-series-author\scripts\test_review_snapshot.ps1" -Manifest 'D:\1codex\BLDC\reports\review-packets\series-architecture-v4\manifest.json' -ExpectedManifestSha256 '120f74ef0829dddc9506042dcd138f97bcc17caafc45f08bb0b8396ee69f3605'

Engineering architecture contract:
Independently audit the real-system causal/data-flow map, engineering responsibility boundaries, knowledge DAG, prerequisite registry, exit capabilities, evidence/mastery chains, modules, chapter contracts, and integration coverage. Test whether planned evidence can prove each capability and whether every prerequisite is established before first use. Check formulas, units, scenario contracts, responsibility boundaries, source/data/report traceability, and whether any planned claim exceeds the evidence. Also check that no duplicate defensive condition exists outside the unique responsibility layer. Because this packet includes review_materials, inspect enough primary evidence to verify whether source/data/report claims are reviewable inside the frozen packet.

Required output schema. Return exactly these logical sections:
packet_hash_before
packet_validation_before: PASS | FAIL plus command/result
reviewed_files: every manifest relative_path exactly once
findings: zero or more findings, each with ID, Severity(P0/P1/P2/P3), Location, Evidence, Failure mechanism, Required correction, Verification
packet_hash_after
packet_validation_after: PASS | FAIL plus command/result
verdict: PASS | REJECT

PASS is allowed only if there are zero P0-P2 findings and packet validation passes before and after. Any P0-P2 finding requires REJECT.
