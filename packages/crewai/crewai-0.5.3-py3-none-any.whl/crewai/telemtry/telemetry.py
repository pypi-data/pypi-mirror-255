import os
import json
import socket
import platform
import pkg_resources


from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

class Telemetry:
	"""A class to handle anonymous telemetry for the crewai package.

	The data being collected is for development purpose, all data is anonymous.

	There is NO data being collected on the prompts, tasks descriptions
	agents backstories or goals nor responses or any data that is being
	processed by the agents, nor any secrets and env vars.

	Data collected includes:
	- Version of crewAI
	- Version of Python
	- General OS (e.g. number of CPUs, macOS/Windows/Linux)
	- Number of agents and tasks in a crew
	- Roles of agents in a crew
	- Tools names being used
	- Country of the user
	- Process being used
	- Language model being used
	- Time taken to complete the crew
	- Time taken to complete each task
	"""
	def __init__(self):
		telemetry_endpoint = "http://telemetry.crewai.com:4318"
		self.disable = os.environ.get("CREWAI_TELEMETRY", False)
		self.resource = Resource(attributes={
			SERVICE_NAME: "crewAI-telemetry"
		})
		self.reader = PeriodicExportingMetricReader(
			OTLPMetricExporter(
				endpoint=f"{telemetry_endpoint}/v1/metrics"
			)
		)
		provider = TracerProvider(resource=self.resource)
		processor = BatchSpanProcessor(
			OTLPSpanExporter(
				endpoint=f"{telemetry_endpoint}/v1/traces"
			)
		)
		provider.add_span_processor(processor)
		trace.set_tracer_provider(provider)

		provider = MeterProvider(resource=self.resource, metric_readers=[self.reader])
		metrics.set_meter_provider(provider)

	def crew_creation(self, crew):
		"""Records the creation of a crew."""
		tracer = trace.get_tracer("crewai.telemetry")
		span = tracer.start_span("Crew Created")
		span.set_attribute("crewai_version", pkg_resources.get_distribution("crewai").version)
		span.set_attribute("python_version", platform.python_version())
		span.set_attribute("hostname", socket.gethostname())
		span.set_attribute("crewid", str(crew.id))
		span.set_attribute("crew_process", crew.process)
		span.set_attribute("crew_language", crew.language)
		span.set_attribute("crew_number_of_tasks", len(crew.tasks))
		span.set_attribute("crew_number_of_agents", len(crew.agents))
		span.set_attribute("crew_agents", json.dumps([{
			"id": str(agent.id),
			"role": agent.role,
			"memory_enabled?": agent.memory,
			"llm": json.dumps(vars(agent.llm)),
			"delegation_enabled?": agent.allow_delegation,
			"tools_names": [tool.name for tool in agent.tools]
		} for agent in crew.agents]))
		span.set_attribute("crew_tasks", json.dumps([{
			"id": str(task.id),
			"async_execution?": task.async_execution,
			"tools_names": [tool.name for tool in task.tools]
		} for task in crew.tasks]))
		span.set_attribute("platform", platform.platform())
		span.set_attribute("platform_release", platform.release())
		span.set_attribute("platform_system", platform.system())
		span.set_attribute("platform_version", platform.version())
		span.set_attribute("cpus", os.cpu_count())
		span.set_status(Status(StatusCode.OK))
		span.end()