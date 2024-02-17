import os
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter


class Telemetry:
	"""A class to handle telemetry for the crewai package.

	The data being collected is only for development purposes
	and is not being used for any other purpose.

	There is NO data being collected on the prompts and responses or
	any data that is being processed by the agents, nor any secrets
	related to the data.

	Data collected includes:
	- Version of crewAI
	- Version of Python
	- General OS (e.g. number of CPUs, macOS/Windows/Linux)
	- Number of agents and tasks in a crew.
	- Process being used
	- Language model being used
	- Time taken to complete the crew
	- Time taken to complete each task
	"""
	def __init__(self):
		telemetry_endpoint = "localhost:4317"
		self.disable = os.environ.get("CREWAI_TELEMETRY", False)
		self.resource = Resource(attributes={
			SERVICE_NAME: "crewAI-telemetry"
		})
		self.reader = PeriodicExportingMetricReader(
			OTLPMetricExporter(endpoint=telemetry_endpoint)
		)
		provider = TracerProvider(resource=self.resource)
		processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=telemetry_endpoint))
		provider.add_span_processor(processor)
		trace.set_tracer_provider(provider)
		provider = MeterProvider(resource=self.resource, metric_readers=[self.reader])
		metrics.set_meter_provider(provider)

	def start_span(self, tracer_name: str, name: str, attributes: dict = {}, links=[]):
		tracer = self._tracer(tracer_name)
		span = tracer.start_span(name, links=links)
		for key, value in attributes.items():
			span.set_attribute(key, value)
		return span

	def add_event(self, span, event: str):
		span.add_event(event)

	def end_span(self, span):
		span.set_status(Status(StatusCode.OK))

	def create_meter(self, name: str):
		return metrics.get_meter(name)

	def create_counter(self, meter, name: str, description: str):
		return meter.create_counter(
    	name, unit="1", description=description
		)

	def _tracer(self, name: str):
		tracer = trace.get_tracer(name)
		return tracer