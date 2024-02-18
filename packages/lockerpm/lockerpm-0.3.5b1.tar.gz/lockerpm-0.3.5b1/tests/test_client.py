import os
import pytest
from dotenv import load_dotenv

import locker.error
from locker.client import Locker
from locker.ls_resources import Secret, Environment


class TestClient(object):
    def test_init_client(self):
        load_dotenv()
        access_key_id = os.getenv("ACCESS_KEY_ID")
        secret_access_key = os.getenv("SECRET_ACCESS_KEY")
        client = Locker(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )
        assert client.access_key_id == access_key_id
        assert client.secret_access_key == secret_access_key

    def test_secrets(self):
        load_dotenv()
        access_key_id = os.getenv("ACCESS_KEY_ID")
        secret_access_key = os.getenv("SECRET_ACCESS_KEY")
        client = Locker(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )
        if not access_key_id or not secret_access_key:
            with pytest.raises(locker.error.AuthenticationError):
                # Raise error
                return
        secrets = client.list()
        for secret in secrets:
            assert isinstance(secret, Secret)
            assert isinstance(secret.key, str)
            assert isinstance(secret.value, str)
            assert isinstance(secret.description, str) or isinstance(secret.description, None)

        default_value = "DEFAULT_SECRET_VALUE"
        secret_value = client.get_secret(key="MY_SECRET_KEY", default_value=default_value)
        assert secret_value == default_value or isinstance(secret_value, str)

    def test_environments(self):
        load_dotenv()
        access_key_id = os.getenv("ACCESS_KEY_ID")
        secret_access_key = os.getenv("SECRET_ACCESS_KEY")
        client = Locker(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )
        if not access_key_id or not secret_access_key:
            with pytest.raises(locker.error.AuthenticationError):
                # Raise error
                return
        environments = client.list_environments()
        for environment in environments:
            assert isinstance(environment, Environment)
            assert isinstance(environment.name, str)
            assert isinstance(environment.external_url, str) or environment.external_url is None
            assert isinstance(environment.description, str) or environment.description is None

        test_environment_name = "test_environment_name"
        environment = client.get_environment(name=test_environment_name)
        assert environment is None or environment.name == test_environment_name
