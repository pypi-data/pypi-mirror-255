import asyncio
from collections import defaultdict
from unctl.lib.collectors.base import DataCollector
from unctl.constants import CheckProviders
from kubernetes_asyncio.client.rest import ApiException
from kubernetes_asyncio.client.api_client import ApiClient
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client import (
    AppsV1Api,
    AutoscalingV1Api,
    NetworkingV1Api,
    BatchV1Api,
    StorageV1Api,
)
from unctl.config.config import get_config_instance


class KubernetesData:
    # keep parameters sorted alphabetically to avoid merge conflicts
    def __init__(
        self,
        configmaps,
        cronjobs,
        daemonsets,
        deployments,
        endpoints,
        hpas,
        ingress_classes,
        ingresses,
        nodes,
        pods,
        network_policies,
        pvcs,
        replicationControllers,
        replicaSets,
        secrets,
        services,
        statefulsets,
        storageClasses,
        events,
    ):
        self._configmaps = configmaps
        self._cronjobs = cronjobs
        self._daemonsets = daemonsets
        self._deployments = deployments
        self._endpoints = endpoints
        self._hpas = hpas
        self._ingress_classes = ingress_classes
        self._ingresses = ingresses
        self._nodes = nodes
        self._pods = pods
        self._network_policies = network_policies
        self._pvcs = pvcs
        self._replicationControllers = replicationControllers
        self._replicaSets = replicaSets
        self._secrets = secrets
        self._services = services
        self._statefulsets = statefulsets
        self._storageClasses = storageClasses
        self._events = events

    # todo: move all k8s requests here to use it on demand

    def get_configmaps(self):
        return self._configmaps

    def get_cronjobs(self):
        return self._cronjobs

    def get_daemonsets(self):
        return self._daemonsets

    def get_deployments(self):
        return self._deployments

    def get_endpoints(self):
        return self._endpoints

    def get_hpas(self):
        return self._hpas

    def get_ingress_classes(self):
        return self._ingress_classes

    def get_ingresses(self):
        return self._ingresses

    def get_nodes(self):
        return self._nodes

    def get_pods(self):
        return self._pods

    def get_network_policies(self):
        return self._network_policies

    def get_pvcs(self):
        return self._pvcs

    def get_replication_controllers(self):
        return self._replicationControllers

    def get_replica_sets(self):
        return self._replicaSets

    def get_secrets(self):
        return self._secrets

    def get_services(self):
        return self._services

    def get_statefulsets(self):
        return self._statefulsets

    def get_storage_classes(self):
        return self._storageClasses

    def get_events(self):
        return self._events


class KubernetesDataCollector(DataCollector, name=CheckProviders.K8S):
    async def fetch_data(self):
        merged_results = defaultdict(list)

        await self.load_kube_config()

        try:
            async with ApiClient() as api:
                v1 = client.CoreV1Api(api)
                v1apps = AppsV1Api(api)
                v1autoscaling = AutoscalingV1Api(api)
                v1networking = NetworkingV1Api(api)
                v1storage = StorageV1Api(api)
                v1batch = BatchV1Api(api)
                config = get_config_instance()
                namespaces = config.filter.namespaces
                if namespaces:
                    for namespace in namespaces:
                        fetched_results = await self.fetch_resources(
                            v1,
                            v1apps,
                            v1autoscaling,
                            v1networking,
                            v1storage,
                            v1batch,
                            namespace=namespace,
                        )
                        self.aggregate_results(merged_results, fetched_results)
                    return self.create_kubernetes_data(merged_results)
                else:
                    fetched_results = await self.fetch_resources(
                        v1,
                        v1apps,
                        v1autoscaling,
                        v1networking,
                        v1storage,
                        v1batch,
                        namespace=None,
                    )
                    return KubernetesData(**fetched_results)
        except ApiException as api_exception:
            self.handle_api_exception(api_exception)
            return None

        except Exception as general_exception:
            self.handle_general_exception(general_exception)
            return None

    async def load_kube_config(self):
        await config.load_kube_config()

    async def fetch_resources(
        self,
        v1,
        v1apps,
        v1autoscaling,
        v1networking,
        v1storage,
        v1batch,
        namespace=None,
    ):
        hpas = self.fetch_items(
            "hpa",
            (
                v1autoscaling.list_namespaced_horizontal_pod_autoscaler(namespace)
                if namespace is not None
                else v1autoscaling.list_horizontal_pod_autoscaler_for_all_namespaces()
            ),
        )

        tasks = {
            "configmaps": self.fetch_items(
                "config map",
                (
                    v1.list_namespaced_config_map(namespace)
                    if namespace is not None
                    else v1.list_config_map_for_all_namespaces()
                ),
            ),
            "cronjobs": self.fetch_items(
                "cron job",
                (
                    v1batch.list_namespaced_cron_job(namespace)
                    if namespace is not None
                    else v1batch.list_cron_job_for_all_namespaces()
                ),
            ),
            "daemonsets": self.fetch_items(
                "daemon set",
                (
                    v1apps.list_namespaced_daemon_set(namespace)
                    if namespace is not None
                    else v1apps.list_daemon_set_for_all_namespaces()
                ),
            ),
            "deployments": self.fetch_items(
                "deployment",
                (
                    v1apps.list_namespaced_deployment(namespace)
                    if namespace is not None
                    else v1apps.list_deployment_for_all_namespaces()
                ),
            ),
            "endpoints": self.fetch_items(
                "endpoint",
                (
                    v1.list_namespaced_endpoints(namespace)
                    if namespace is not None
                    else v1.list_endpoints_for_all_namespaces()
                ),
            ),
            "hpas": hpas,
            "ingress_classes": self.fetch_items(
                "ingress class", v1networking.list_ingress_class()
            ),
            "ingresses": self.fetch_items(
                "ingress",
                (
                    v1networking.list_namespaced_ingress(namespace)
                    if namespace is not None
                    else v1networking.list_ingress_for_all_namespaces()
                ),
            ),
            "network_policies": self.fetch_items(
                "network policy",
                (
                    v1networking.list_namespaced_network_policy(namespace)
                    if namespace is not None
                    else v1networking.list_network_policy_for_all_namespaces()
                ),
            ),
            "nodes": self.fetch_items(
                "node",
                (
                    v1.list_node(watch=False, label_selector=f"namespace={namespace}")
                    if namespace is not None
                    else v1.list_node(watch=False)
                ),
            ),
            "pods": self.fetch_items(
                "pod",
                (
                    v1.list_namespaced_pod(namespace)
                    if namespace is not None
                    else v1.list_pod_for_all_namespaces()
                ),
            ),
            "pvcs": self.fetch_items(
                "pvc",
                (
                    v1.list_namespaced_persistent_volume_claim(namespace)
                    if namespace is not None
                    else v1.list_persistent_volume_claim_for_all_namespaces()
                ),
            ),
            "replicationControllers": self.fetch_items(
                "replication controller",
                (
                    v1.list_namespaced_replication_controller(namespace)
                    if namespace is not None
                    else v1.list_replication_controller_for_all_namespaces()
                ),
            ),
            "replicaSets": self.fetch_items(
                "replica set",
                (
                    v1apps.list_namespaced_replica_set(namespace)
                    if namespace is not None
                    else v1apps.list_replica_set_for_all_namespaces()
                ),
            ),
            "secrets": self.fetch_items(
                "secret",
                (
                    v1.list_namespaced_secret(namespace)
                    if namespace is not None
                    else v1.list_secret_for_all_namespaces()
                ),
            ),
            "services": self.fetch_items(
                "service",
                (
                    v1.list_namespaced_service(namespace)
                    if namespace is not None
                    else v1.list_service_for_all_namespaces()
                ),
            ),
            "statefulsets": self.fetch_items(
                "statefulset",
                (
                    v1apps.list_namespaced_stateful_set(namespace)
                    if namespace is not None
                    else v1apps.list_stateful_set_for_all_namespaces()
                ),
            ),
            "storageClasses": self.fetch_items(
                "storage class", v1storage.list_storage_class()
            ),
            "events": self.fetch_items(
                "event",
                (
                    v1.list_namespaced_event(namespace)
                    if namespace is not None
                    else v1.list_event_for_all_namespaces()
                ),
            ),
        }

        return dict(zip(tasks, await asyncio.gather(*tasks.values())))

    async def fetch_items(self, name, awaitable):
        try:
            return (await awaitable).items
        except ApiException as e:
            print(
                f"❌ Fetching {name} list failed. Some of checks results "
                f"may be irrelevant. Reason: {e.reason}"
            )
            return []

    def aggregate_results(self, merged_results, fetched_results):
        for key, value in fetched_results.items():
            merged_results[key].extend(value)

    def create_kubernetes_data(self, merged_results):
        aggregate_result = dict(merged_results)
        return KubernetesData(**aggregate_result)

    def handle_api_exception(self, api_exception):
        print(f"An error occurred with the Kubernetes API: {api_exception.reason}")

    def handle_general_exception(self, general_exception):
        print(f"An unexpected error occurred: {general_exception}")
