#!/usr/bin/env python3
# Copyright 2021 Gustavo Sanchez
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

from ops.model import ActiveStatus
from ops.main import main
from ops.framework import StoredState
from ops.charm import ActionEvent, CharmBase, ConfigChangedEvent, PebbleReadyEvent, RelationBrokenEvent, RelationChangedEvent, RelationCreatedEvent
import logging

KUBECONFIG_PATH = "/root/.kube/config"

KUBE_BURNER_INIT_SERVICE_WRAPPER = "/bin/kube-burner-service-wrapper"

KUBE_BURNER_FOLDER = "/root/kube-burner"
WORKLOADS_FOLDER = KUBE_BURNER_FOLDER + "/workloads"
TARGET_CONFIG = "target-config"


logger = logging.getLogger(__name__)


class CharmK8SKubeBurnerCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(
            self.on.kube_burner_pebble_ready, self._on_kube_burner_pebble_ready)
        self.framework.observe(self.on.check_alerts_action,
                               self._on_check_alerts_action)

    def _on_kube_burner_pebble_ready(self, event: PebbleReadyEvent):
        """Define and start a workload using the Pebble API."""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        kube_burner_layer = {
            "summary": "kube-burner layer",
            "description": "Pebble config layer for kube-burner",
            "services": {
                "sleep": {
                    "override": "replace",
                    "summary": "Linux sleep to allow kube-burner CLI to be a service",
                    "command": "/usr/bin/sleep infinity",
                    "startup": "enabled",
                },
                "kube-burner.init": {
                    "override": "replace",
                    "summary": "Launch benchmark",
                    "command": f'{KUBE_BURNER_INIT_SERVICE_WRAPPER}',
                    "startup": "disabled",
                }
            },
        }
        kube_burner_init_service_wrapper = """
            #!/bin/bash
            /bin/kube-burner init -c /root/kube-burner/workloads/target-config/target-config.yml
            /usr/bin/sleep infinity
        """

        # Add intial Pebble config layer using the Pebble API
        container.add_layer("kube-burner", kube_burner_layer, combine=True)
        container.push(
            KUBE_BURNER_INIT_SERVICE_WRAPPER, kube_burner_init_service_wrapper,
            make_dirs=True
        )
        container.autostart()
        self.unit.status = ActiveStatus()

    def _on_check_alerts_action(self, event: ActionEvent):
        """Launch benchmark."""
        logger.info("run-action: init")

        try:
            kube_burner_config = event.params["kube-burner-config"]
            self._clear_kube_burner_target_config()
            self._set_kube_burner_target_config(kube_burner_config)

            container = self.unit.get_container('kube-burner')
            if container.get_service("kube-burner.init").is_running():
                container.start("kube-burner.init")

        except Exception as e:
            event.fail(e)

    def _clear_kube_burner_target_config(self) -> None:
        logger.debug("_clean_kube_burner_target_config()")

        container = self.unit.get_container('kube-burner')
        try:
            container.remove_path(
                f'{WORKLOADS_FOLDER}/{TARGET_CONFIG}/', recursive=True)
        except:
            pass

    def _set_kube_burner_target_config(self, kube_burner_config) -> None:
        logger.debug("_set_kube_burner_target_config()")

        container = self.unit.get_container('kube-burner')
        container.push(
            f'{WORKLOADS_FOLDER}/{TARGET_CONFIG}/{TARGET_CONFIG}.yml',
            kube_burner_config["content"], make_dirs=True
        )
        for template in kube_burner_config["templates"]:
            container.push(
                f'{WORKLOADS_FOLDER}/{TARGET_CONFIG}/templates/{template["objectTemplate"].split("/")[-1:][0]}',
                template["content"], make_dirs=True
            )


if __name__ == "__main__":
    main(CharmK8SKubeBurnerCharm)
