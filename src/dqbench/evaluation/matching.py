"""Greedy earliest matching for incident-aware evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from dqbench.contracts.alerts import AlertRecord
from dqbench.contracts.incidents import IncidentRecord


@dataclass
class MatchResult:
    alerts: List[AlertRecord]
    incidents: List[IncidentRecord]
    matched_pairs: List[Tuple[AlertRecord, IncidentRecord]] = field(default_factory=list)
    duplicate_alerts: List[AlertRecord] = field(default_factory=list)
    unmatched_alerts: List[AlertRecord] = field(default_factory=list)
    missed_incidents: List[IncidentRecord] = field(default_factory=list)
    duplicates_by_incident: Dict[str, List[AlertRecord]] = field(default_factory=dict)


def scope_compatible(alert: AlertRecord, incident: IncidentRecord) -> bool:
    target = incident.target_scope
    target_level = target.get("level")
    target_ref = target.get("ref")
    table_ref = target.get("table_ref")
    relation_ref = target.get("relation_ref")

    if alert.scope_level == "column":
        return target_level == "column" and alert.scope_ref == target_ref
    if alert.scope_level == "table":
        return alert.scope_ref == target_ref or (target_level == "column" and alert.scope_ref == table_ref)
    if alert.scope_level == "relation":
        return alert.scope_ref == relation_ref or alert.scope_ref == target_ref
    return False


def valid_pair(alert: AlertRecord, incident: IncidentRecord) -> bool:
    return (
        alert.domain == incident.domain
        and incident.window_start <= alert.batch_id <= incident.window_end
        and scope_compatible(alert, incident)
    )


def match_alerts(alerts: List[AlertRecord], incidents: List[IncidentRecord]) -> MatchResult:
    sorted_alerts = sorted(alerts, key=lambda item: (item.batch_id, item.alert_id))
    sorted_incidents = sorted(incidents, key=lambda item: (item.window_start, item.incident_id))
    used_alert_ids = set()
    result = MatchResult(alerts=sorted_alerts, incidents=sorted_incidents)

    for incident in sorted_incidents:
        chosen = None
        for alert in sorted_alerts:
            if alert.alert_id in used_alert_ids:
                continue
            if valid_pair(alert, incident):
                chosen = alert
                break
        if chosen is None:
            result.missed_incidents.append(incident)
            continue
        used_alert_ids.add(chosen.alert_id)
        result.matched_pairs.append((chosen, incident))
        dupes = [
            alert
            for alert in sorted_alerts
            if alert.alert_id not in used_alert_ids and valid_pair(alert, incident)
        ]
        if dupes:
            result.duplicate_alerts.extend(dupes)
            result.duplicates_by_incident[incident.incident_id] = dupes

    result.unmatched_alerts = [
        alert
        for alert in sorted_alerts
        if alert.alert_id not in used_alert_ids and alert.alert_id not in {dupe.alert_id for dupe in result.duplicate_alerts}
    ]
    return result
