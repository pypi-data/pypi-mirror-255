import logging

logger = logging.getLogger(__name__)

from kubernetes import client


def delete_pod(v1: client.CoreV1Api, name: str, namespace: str = 'default', async_req: bool = False):
    return v1.delete_namespaced_pod(name, namespace, async_req=async_req)
