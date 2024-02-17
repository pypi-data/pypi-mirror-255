import abc

from kubernetes import client

from galileofaas.system.core import KubernetesFunctionReplica


class PodFactory(abc.ABC):

    def create_pod(self, replica: KubernetesFunctionReplica, **kwargs) -> client.V1Pod:
        """
        Creates a Pod from a KubernetesFunctionReplica.
        :param replica:
        :param kwargs: passed on to the spec filed of the PodSpec
        :return:
        """
        pod = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=client.V1ObjectMeta(name=replica.replica_id, labels=replica.labels),
            spec=client.V1PodSpec(
                **kwargs,
                containers=[
                    self.create_container(replica)
                ]
            ),
        )
        return pod

    def create_container(self, replica: KubernetesFunctionReplica) -> client.V1Container: ...
