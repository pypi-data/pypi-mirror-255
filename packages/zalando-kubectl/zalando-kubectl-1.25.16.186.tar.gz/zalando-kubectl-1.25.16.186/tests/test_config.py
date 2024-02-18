from unittest.mock import MagicMock

import pytest

from zalando_kubectl import kube_config
from zalando_kubectl.utils import Environment


def _update_config(monkeypatch, current_config, url, alias, use_okta):
    monkeypatch.setattr("zalando_kubectl.kube_config.write_config", MagicMock())
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=current_config))
    monkeypatch.setattr("zign.api.get_token", MagicMock(return_value="mytok"))
    return kube_config.update(url, alias, "mytok", use_okta)


def test_kube_config_update(monkeypatch):
    updated = _update_config(monkeypatch, {}, "https://zalan.k8s.do", "foo", False)
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "foo"}],
        "contexts": [{"context": {"cluster": "foo", "user": "zalando-token"}, "name": "foo"}],
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }


def test_kube_config_update_url(monkeypatch):
    updated = _update_config(monkeypatch, {}, "https://zalan.k8s.do", None, False)
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "zalan_k8s_do",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"}],
        "contexts": [{"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"}],
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }


def test_kube_config_update_merge(monkeypatch):
    existing = {
        "apiVersion": "v0",
        "kind": "Unknown",
        "current-context": "another",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan.k8s.do", "custom": "setting"}, "name": "foo"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "user": "zalando-token2", "custom": "setting"}, "name": "foo"},
        ],
        "users": [
            {"user": {"token": "mytok"}, "name": "another-token"},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
        ],
    }
    updated = _update_config(monkeypatch, existing, "https://zalan2.k8s.do", "foo", False)
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan2.k8s.do", "custom": "setting"}, "name": "foo"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "user": "zalando-token", "custom": "setting"}, "name": "foo"},
        ],
        "users": [
            {"user": {"token": "mytok"}, "name": "another-token"},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
        ],
    }

    updated2 = _update_config(monkeypatch, updated, "https://zalan3.k8s.do", "bar", False)
    assert updated2 == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "bar",
        "clusters": [
            {"cluster": {"server": "https://zalan.k8s.do"}, "name": "zalan_k8s_do"},
            {"cluster": {"server": "https://zalan2.k8s.do", "custom": "setting"}, "name": "foo"},
            {"cluster": {"server": "https://zalan3.k8s.do"}, "name": "bar"},
        ],
        "contexts": [
            {"context": {"cluster": "zalan_k8s_do", "user": "zalando-token"}, "name": "zalan_k8s_do"},
            {"context": {"cluster": "foo", "user": "zalando-token", "custom": "setting"}, "name": "foo"},
            {"context": {"cluster": "bar", "user": "zalando-token"}, "name": "bar"},
        ],
        "users": [
            {"user": {"token": "mytok"}, "name": "another-token"},
            {"user": {"token": "mytok", "custom": "setting"}, "name": "zalando-token"},
        ],
    }


@pytest.mark.parametrize(
    "existing, expected, use_okta",
    [
        # Add new entry without flag
        (
            {},
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "zalando-token"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                ],
            },
            False,
        ),
        # Add new okta entry
        (
            {},
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "okta-foo"}}],
                "current-context": "foo",
                "users": [
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
            True,
        ),
        # Switch to Okta from an existing Zalando OAuth setup
        (
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "zalando-token"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                ],
            },
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "okta-foo"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
            True,
        ),
        # Switch back if the Okta user is dropped
        (
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [{"name": "foo", "cluster": {"server": "https://zalan.k8s.do"}}],
                "contexts": [{"name": "foo", "context": {"cluster": "foo", "user": "okta-foo"}}],
                "current-context": "foo",
                "users": [
                    {"name": "zalando-token", "user": {"token": "mytok"}},
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
            {
                "apiVersion": "v1",
                "kind": "Config",
                "current-context": "foo",
                "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "foo"}],
                "contexts": [{"context": {"cluster": "foo", "user": "zalando-token"}, "name": "foo"}],
                "users": [
                    {"user": {"token": "mytok"}, "name": "zalando-token"},
                    {
                        "name": "okta-foo",
                        "user": {
                            "exec": {
                                "apiVersion": "client.authentication.k8s.io/v1beta1",
                                "args": ["credentials", "foo"],
                                "command": "zkubectl",
                            }
                        },
                    },
                ],
            },
            False,
        ),
    ],
)
def test_kube_config_update_okta(monkeypatch, existing, expected, use_okta):
    updated = _update_config(monkeypatch, existing, "https://zalan.k8s.do", "foo", use_okta)
    assert updated == expected


def test_kube_config_update_broken(monkeypatch):
    existing = {
        "apiVersion": "v1",
        "kind": "Config",
        "clusters": None,
        "contexts": None,
        "current-context": "",
        "users": None,
    }
    updated = _update_config(monkeypatch, existing, "https://zalan.k8s.do", "foo", False)
    assert updated == {
        "apiVersion": "v1",
        "kind": "Config",
        "current-context": "foo",
        "clusters": [{"cluster": {"server": "https://zalan.k8s.do"}, "name": "foo"}],
        "contexts": [{"context": {"cluster": "foo", "user": "zalando-token"}, "name": "foo"}],
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }


def test_kube_config_get_namespace(monkeypatch):
    ns_config = {"contexts": [{"name": "none", "context": {"namespace": "some"}}]}
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "default"
    ns_config["current-context"] = "none"
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "some"
    ns_config["contexts"][0]["context"] = {}
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=ns_config))
    assert kube_config.get_current_namespace() == "default"


def _update_token(monkeypatch, existing):
    monkeypatch.setattr("zalando_kubectl.kube_config.write_config", MagicMock())
    monkeypatch.setattr("zalando_kubectl.kube_config.read_config", MagicMock(return_value=existing))
    monkeypatch.setattr("zign.api.get_token", MagicMock(return_value="mytok"))
    return kube_config.update_token(Environment())


def test_kube_config_update_token(monkeypatch):
    updated = _update_token(monkeypatch, {})
    assert updated == {
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }

    updated = _update_token(monkeypatch, {"users": [{"user": {"token": "another"}, "name": "foo"}]})
    assert updated == {
        "users": [{"user": {"token": "another"}, "name": "foo"}, {"user": {"token": "mytok"}, "name": "zalando-token"}],
    }


def test_kube_config_update_token_refresh(monkeypatch):
    updated = _update_token(monkeypatch, {"users": [{"user": {"token": "oldtok"}, "name": "zalando-token"}]})
    assert updated == {
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }


def test_kube_config_update_token_migrate(monkeypatch):
    updated = _update_token(
        monkeypatch,
        {
            "contexts": [
                {"context": {"cluster": "foo", "user": "another", "custom": "setting"}, "name": "another"},
                {"context": {"cluster": "foo", "user": "foo_zalan_do", "custom": "setting"}, "name": "foo"},
            ],
            "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
        },
    )
    assert updated == {
        "contexts": [
            {"context": {"cluster": "foo", "user": "another", "custom": "setting"}, "name": "another"},
            {"context": {"cluster": "foo", "user": "zalando-token", "custom": "setting"}, "name": "foo"},
        ],
        "users": [{"user": {"token": "mytok"}, "name": "zalando-token"}],
    }
