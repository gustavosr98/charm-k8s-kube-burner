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

import logging

from ops.charm import ActionEvent, CharmBase, ConfigChangedEvent, PebbleReadyEvent, RelationBrokenEvent, RelationChangedEvent, RelationCreatedEvent
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class CharmK8SKubeBurnerCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.kube_burner_pebble_ready, self._on_kube_burner_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.fortune_action, self._on_fortune_action)
        
    def _on_kube_burner_pebble_ready(self, event: PebbleReadyEvent):
        """Define and start a workload using the Pebble API."""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        kube_burner_layer = {
            "summary": "kube-burner layer",
            "description": "pebble config layer for kube-burner",
            "services": {
                "kube-burner": {
                    "override": "replace",
                    "summary": "kube-burner",
                    "command": "/bin/kube-burner",
                    "startup": "disabled",
                    "environment": {"thing": self.model.config["thing"]},
                }
            },
        }
        # Add intial Pebble config layer using the Pebble API
        container.add_layer("kube-burner", kube_burner_layer, combine=True)
        self.unit.status = ActiveStatus()

    def _on_config_changed(self, event: ConfigChangedEvent):
        """Just an example to show how to deal with changed configuration.

        TEMPLATE-TODO: change this example to suit your needs.
        If you don't need to handle config, you can remove this method,
        the hook created in __init__.py for it, the corresponding test,
        and the config.py file.

        Learn more about config at https://juju.is/docs/sdk/config
        """
        current = self.config["thing"]
        if current not in self._stored.things:
            logger.debug("found a new thing: %r", current)
            self._stored.things.append(current)

    def _on_fortune_action(self, event: ActionEvent):
        """Just an example to show how to receive actions.

        TEMPLATE-TODO: change this example to suit your needs.
        If you don't need to handle actions, you can remove this method,
        the hook created in __init__.py for it, the corresponding test,
        and the actions.py file.

        Learn more about actions at https://juju.is/docs/sdk/actions
        """
        fail = event.params["fail"]
        if fail:
            event.fail(fail)
        else:
            event.set_results({"fortune": "A bug in the code is worth two in the documentation."})


if __name__ == "__main__":
    main(CharmK8SKubeBurnerCharm)
