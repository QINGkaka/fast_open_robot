from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from openwam.deploy.server import PolicyServer


class FakePolicy:
    def __init__(self, engine, cfg, execution_config=None):
        del engine, cfg, execution_config
        self.value = 0
        self.shutdown_called = False

    def predict_action(self, obs):
        del obs
        self.value += 1
        return np.asarray([self.value], dtype=np.float32)

    def reset(self):
        self.value = 0

    def shutdown(self):
        self.shutdown_called = True


class IdentityPreprocessor:
    @classmethod
    def from_cfg(cls, cfg, engine):
        del cfg, engine
        return cls()

    multiview = False
    camera_layout = []
    img_height = 1
    img_width = 1

    def preprocess(self, obs):
        return obs


def execution_config(*, enabled=False):
    return SimpleNamespace(enabled=enabled, inference_horizon=1, inference_delay_steps=0)


@patch("openwam.deploy.obs_preprocess.ObsPreprocessor.from_cfg", IdentityPreprocessor.from_cfg)
@patch("openwam.deploy.policy.WAMPolicy", FakePolicy)
@patch("openwam.deploy.executors.resolve_execution_config", lambda cfg: execution_config())
def test_sessions_have_independent_reset_and_request_state():
    server = PolicyServer(object(), object(), session_isolation=True)
    first = server.new_session()
    second = server.new_session()

    with pytest.raises(ValueError, match="must reset"):
        server.predict({}, session=first)

    first.reset()
    second.reset()
    first_result = server.predict({}, session=first)
    second_result = server.predict({}, session=second)
    assert first_result["step"] == 1
    assert first_result["action"] == [1.0]
    assert second_result["step"] == 1
    assert second_result["action"] == [1.0]

    first.reset()
    assert server.predict({}, session=first)["step"] == 1
    assert server.predict({}, session=second)["step"] == 2

    first.shutdown()
    second.shutdown()
    assert first.policy.shutdown_called
    assert second.policy.shutdown_called


@patch("openwam.deploy.policy.WAMPolicy", FakePolicy)
@patch("openwam.deploy.executors.resolve_execution_config", lambda cfg: execution_config(enabled=True))
def test_session_isolation_rejects_async_executor():
    server = PolicyServer(object(), object(), session_isolation=True)
    with pytest.raises(ValueError, match="synchronous executor"):
        server._init_policy()
