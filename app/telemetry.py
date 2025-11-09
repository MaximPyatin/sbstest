from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI, Request
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import REGISTRY, make_asgi_app


@dataclass(slots=True)
class _HttpMetrics:
    request_counter: metrics.Counter
    duration_histogram: metrics.Histogram


def _build_meter_provider(service_name: str) -> tuple[MeterProvider, PrometheusMetricReader]:
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "sbs",
            "service.instance.id": os.getenv("HOSTNAME", "local"),
        }
    )
    prometheus_reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
    return provider, prometheus_reader


def configure_telemetry(app: FastAPI, service_name: Optional[str] = None) -> None:
    """Включаем метрики через OpenTelemetry и отдаём их в Prometheus."""
    resolved_service_name = service_name or os.getenv("OTEL_SERVICE_NAME", "sbs-api")

    provider, prometheus_reader = _build_meter_provider(resolved_service_name)
    metrics.set_meter_provider(provider)

    FastAPIInstrumentor().instrument_app(app, excluded_urls="/metrics")

    meter = metrics.get_meter("sbs.telemetry", version="0.1.0")
    http_metrics = _HttpMetrics(
        request_counter=meter.create_counter(
            name="http_server_requests_total",
            unit="1",
            description="Total number of HTTP requests processed by the server.",
        ),
        duration_histogram=meter.create_histogram(
            name="http_server_request_duration_seconds",
            unit="s",
            description="Duration of HTTP requests in seconds.",
        ),
    )

    prometheus_app = make_asgi_app(REGISTRY)
    app.mount("/metrics", prometheus_app)

    app.state.telemetry = {
        "provider": provider,
        "reader": prometheus_reader,
        "http": http_metrics,
    }


def record_http_request_metrics(
    request: Request,
    status_code: int,
    duration_seconds: float,
) -> None:
    """Записываем один HTTP-запрос в метрики: метод, статус и сколько заняло времени."""
    telemetry_state = getattr(request.app.state, "telemetry", None)
    if telemetry_state is None:
        return

    http_metrics: _HttpMetrics = telemetry_state["http"]
    attributes = {
        "http.method": request.method,
        "http.status_code": str(status_code),
        "http.route": request.url.path,
    }
    http_metrics.request_counter.add(1, attributes=attributes)
    http_metrics.duration_histogram.record(duration_seconds, attributes=attributes)

