"""检查系列架构知识 DAG、章节前置和模块入口时序。"""

from __future__ import annotations

import json
import re
from pathlib import Path


MODULE_FIRST_CHAPTER = {
    "M00": 0,
    "M01": 1,
    "M02": 6,
    "M03": 9,
    "M04": 12,
    "M05": 15,
}


def extract_mermaid_blocks(markdown: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"```mermaid\r?\n([\s\S]*?)```", markdown)]


def parse_endpoint(raw: str) -> tuple[str, str | None]:
    cleaned = raw.strip().replace(";", "")
    match = re.match(r'^([A-Za-z0-9_]+)(?:\["([^"]+)"\])?$', cleaned)
    if not match:
        return cleaned, None
    node_id, label = match.groups()
    return node_id, label


def extract_dag_graph(mermaid_source: str) -> tuple[set[str], list[tuple[str, str]]]:
    node_labels: dict[str, str] = {}
    raw_edges: list[tuple[str, str]] = []
    for line in mermaid_source.splitlines():
        line = line.strip()
        if not line or line.startswith("flowchart") or "-->" not in line:
            continue
        left, right = re.split(r"\s*-->\s*", line, maxsplit=1)
        from_id, from_label = parse_endpoint(left)
        to_id, to_label = parse_endpoint(right)
        if from_label or from_id not in node_labels:
            node_labels[from_id] = from_label or from_id
        if to_label or to_id not in node_labels:
            node_labels[to_id] = to_label or to_id
        raw_edges.append((from_id, to_id))
    labels = set(node_labels.values())
    edges = [(node_labels.get(left, left), node_labels.get(right, right)) for left, right in raw_edges]
    return labels, edges


def split_ids(cell: str) -> list[str]:
    cleaned = cell.replace("。", "")
    embedded = re.findall(r"(?:ENTRY|K|CAPABILITY_OUTPUT)-[A-Z0-9_-]+", cleaned)
    if embedded:
        return embedded
    items = []
    for item in re.split(r"[、,，]\s*", cleaned):
        value = item.strip().strip("`").strip()
        if value and value != "无":
            items.append(value)
    return items


def chapter_order(owner: str) -> int:
    if owner == "入口":
        return 0
    match = re.match(r"C(\d{2})", owner)
    if match:
        return int(match.group(1))
    return 999


def extract_registry_owners(markdown: str) -> dict[str, int]:
    owners: dict[str, int] = {}
    for line in markdown.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9 or cells[0] in {"ID", "---"}:
            continue
        item_id = cells[0].strip("`")
        if not re.match(r"^(ENTRY|K|CAPABILITY_OUTPUT)-", item_id):
            continue
        owner_cell = cells[8]
        owner = owner_cell.split("/")[0].strip()
        owners[item_id] = chapter_order(owner)
    return owners


def extract_chapter_prerequisites(markdown: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current_chapter: int | None = None
    for line in markdown.splitlines():
        heading = re.match(r"^### C(\d{2})\b", line)
        if heading:
            current_chapter = int(heading.group(1))
            continue
        if current_chapter is None:
            continue
        match = re.match(r"\|\s*前置 ID\s*\|\s*([^|]+?)\s*\|", line)
        if match:
            for item_id in split_ids(match.group(1)):
                rows.append({"use_type": "chapter", "use_owner": f"C{current_chapter:02d}", "use_order": current_chapter, "id": item_id})
    return rows


def extract_module_entry_prerequisites(markdown: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    in_module_table = False
    for line in markdown.splitlines():
        if line.startswith("| 模块 | 工程责任"):
            in_module_table = True
            continue
        if in_module_table and line.startswith("## "):
            break
        if not in_module_table or not line.startswith("| M"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        module_id = cells[0].split()[0]
        first_order = MODULE_FIRST_CHAPTER.get(module_id)
        if first_order is None:
            continue
        for item_id in split_ids(cells[2]):
            rows.append({"use_type": "module_entry", "use_owner": module_id, "use_order": first_order, "id": item_id})
    return rows


def find_cycle(edges: list[tuple[str, str]]) -> list[str]:
    graph: dict[str, list[str]] = {}
    for left, right in edges:
        graph.setdefault(left, []).append(right)
        graph.setdefault(right, [])
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str]:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return []
        visiting.add(node)
        stack.append(node)
        for child in graph[node]:
            cycle = visit(child)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return []


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    markdown = (root / "docs" / "series-architecture.md").read_text(encoding="utf-8")
    blocks = extract_mermaid_blocks(markdown)
    if len(blocks) < 2:
        raise RuntimeError("knowledge DAG mermaid block not found")
    dag_labels, dag_edges = extract_dag_graph(blocks[1])
    registry_owners = extract_registry_owners(markdown)
    prerequisite_uses = extract_chapter_prerequisites(markdown) + extract_module_entry_prerequisites(markdown)

    referenced = {str(row["id"]) for row in prerequisite_uses}
    missing = sorted(referenced - dag_labels)
    unresolved = sorted(referenced - set(registry_owners))
    order_violations = []
    for row in prerequisite_uses:
        item_id = str(row["id"])
        owner_order = registry_owners.get(item_id)
        if owner_order is None:
            continue
        use_order = int(row["use_order"])
        is_external_entry = item_id.startswith("ENTRY-")
        has_order_violation = owner_order > use_order if is_external_entry else owner_order >= use_order
        if has_order_violation:
            order_violations.append({
                "id": item_id,
                "owner_order": owner_order,
                "use_owner": row["use_owner"],
                "use_order": use_order,
                "use_type": row["use_type"],
            })

    cycle = find_cycle(dag_edges)
    result = "PASS" if not missing and not unresolved and not order_violations and not cycle else "FAIL"
    report = {
        "schema_version": 2,
        "dag_node_count": len(dag_labels),
        "dag_edge_count": len(dag_edges),
        "registry_id_count": len(registry_owners),
        "prerequisite_use_count": len(prerequisite_uses),
        "missing_from_dag": missing,
        "unresolved_prerequisite_ids": unresolved,
        "owner_order_violations": order_violations,
        "cycle": cycle,
        "result": result,
    }
    report_path = root / "reports" / "series-architecture-dag-check.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\r\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
