"""Hourly metrics per country and publisher."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from taptap_codetest.records import Record
from taptap_codetest.tabular.base import Tabulator, TableSet

GROUP_KEYS = ["date_utc", "hour_utc", "country", "publisher_id"]
METRIC_COLUMNS = [
    *GROUP_KEYS,
    "publisher_name",
    "bid_requests",
    "impressions",
    "clicks",
    "ctr",
    "spend_eur",
]
MICROS_PER_EUR = 1_000_000


class MetricsTabulator(Tabulator):
    def __init__(self, publishers: pd.DataFrame, table_name: str = "metrics") -> None:
        self.publishers = publishers
        self.table_name = table_name

    def build(self, records: Iterable[Record]) -> TableSet:
        events = pd.DataFrame([record.payload for record in records])
        if events.empty:
            return {self.table_name: pd.DataFrame(columns=METRIC_COLUMNS)}

        event_type = events["event_type"]
        is_impression = event_type == "impression"
        events = events.assign(
            bid_requests=(event_type == "bid_request").astype(int),
            impressions=is_impression.astype(int),
            clicks=(event_type == "click").astype(int),
            spend_micros=pd.to_numeric(events["price_micros"], errors="coerce")
            .where(is_impression, 0)
            .fillna(0),
        )

        metrics = (
            events.groupby(GROUP_KEYS, dropna=False)[
                ["bid_requests", "impressions", "clicks", "spend_micros"]
            ]
            .sum()
            .reset_index()
        )
        metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]).where(
            metrics["impressions"] > 0, 0.0
        )
        metrics["spend_eur"] = metrics["spend_micros"] / MICROS_PER_EUR
        metrics = metrics.merge(self.publishers, on="publisher_id", how="left")

        return {self.table_name: metrics[METRIC_COLUMNS]}
