from unittest.mock import MagicMock, patch
from os.path import realpath, join, dirname

from click.testing import CliRunner

from testery import add_env_vars_from_file, add_pipeline_vars_from_file, list_active_test_runs, monitor_test_runs, update_pipeline_stage
from tests.conftest import mocked_requests_get, mocked_requests_get_401, mocked_requests_patch, mocked_requests_post


# TODO: add no running tests runs scenario
class TestMonitorTestRuns:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_monitor_test_runs(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        expected_output = ("Test run 304098 is now RUNNING.\n"
                           "There are 4 tests passing out of 6 with 1 failing.\n"
                           "Test run 304090 is now SUBMITTED.\n"
                           "There are 4 tests passing out of 6 with 2 failing.\n")
        params = [f'--token={fake_token}', '--duration=0']

        result = cli_runner.invoke(monitor_test_runs, params)

        assert result.exit_code == 0
        assert result.output == expected_output
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )


# TODO: add no running tests scenario
class TestGetTestRuns:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_test_runs_pretty(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}']

        result = cli_runner.invoke(list_active_test_runs, params)

        assert result.exit_code == 0
        assert result.output == '304098: RUNNING\n304090: SUBMITTED\n'
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_test_runs_json(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--output=json']

        result = cli_runner.invoke(list_active_test_runs, params)

        assert result.exit_code == 0
        assert result.output == '{"304098": "RUNNING", "304090": "SUBMITTED"}\n'
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )


class TestUploadVars():
    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_update_stage(self, mock_patch: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--name=Production']

        result = cli_runner.invoke(update_pipeline_stage, params)

        assert result.exit_code == 0
        assert 'Updated pipeline stage Production with id: 2' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/pipeline-stages/2',
            json={
                'name': 'Production',
                'priority': 1,
                'testRunPriority': 1,
                'windowsRunnerPoolId': None,
                'linuxRunnerPoolId': None
                },
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get_401)
    def test_update_stage_auth(self, fake_token: str, cli_runner: CliRunner):
        params = [f'--token={fake_token}', '--name=Production']

        result = cli_runner.invoke(update_pipeline_stage, params)

        assert result.exit_code == 1
        assert result.exception.args[0] == "Please make sure you are using the correct token"

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_update_stage_non_exist(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--name=fake']
        result = cli_runner.invoke(update_pipeline_stage, params)
        assert result.exception.args[0] == "Pipeline Stage fake does not exist and --create-if-not-exists not set"
        mock_get.assert_any_call(
            'https://api.testery.io/api/pipeline-stages',
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.post', side_effect=mocked_requests_post)
    def test_update_stage_non_exist_create_vars(self, mock_post: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--name=fake',
                  '--create-if-not-exists', '--variable="FOO=BAR"']
        result = cli_runner.invoke(update_pipeline_stage, params)

        assert result.exit_code == 0
        assert 'Created pipeline stage fake with id: 22094' in result.output
        mock_post.assert_called_once_with(
            'https://api.testery.io/api/pipeline-stages',
            json={'name': 'fake', 'variables': [{'key': '"FOO', 'value': 'BAR"', 'encrypted': False}]},
            headers=expected_headers
        )
        assert result.output == "Created pipeline stage fake with id: 22094\n" \
            "{'accountId': 1, 'linuxRunnerPoolId': None, 'windowsRunnerPoolId': None, 'name': 'fake', 'priority': 1, " \
            "'testRunPriority': 1, 'variables': [{'key': '\"FOO', 'value': 'BAR\"', 'encrypted': False}], 'id': 22094}\n"

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.post', side_effect=mocked_requests_post)
    def test_update_stage_non_exist_create(self, mock_post: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--name=fake',
                  '--create-if-not-exists']
        result = cli_runner.invoke(update_pipeline_stage, params)

        assert result.exit_code == 0
        assert 'Created pipeline stage fake with id: 22094' in result.output
        mock_post.assert_called_once_with(
            'https://api.testery.io/api/pipeline-stages',
            json={'name': 'fake'},
            headers=expected_headers
        )
        assert result.output == "Created pipeline stage fake with id: 22094\n" \
            "{'accountId': 1, 'linuxRunnerPoolId': None, 'windowsRunnerPoolId': None, 'name': 'fake', 'priority': 1, " \
            "'testRunPriority': 1, 'variables': [], 'id': 22094}\n"


class TestVarFilePipeline:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_stage_not_exist(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--name=fake', f'--env-file={fpath}']

        result = cli_runner.invoke(add_pipeline_vars_from_file, params)

        assert result.exception.args[0] == "Pipeline Stage fake does not exist"
        mock_get.assert_any_call(
            'https://api.testery.io/api/pipeline-stages',
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get_401)
    def test_bad_auth(self, fake_token: str, cli_runner: CliRunner):
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--name=Production', f'--env-file={fpath}']

        result = cli_runner.invoke(add_pipeline_vars_from_file, params)

        assert result.exit_code == 1
        assert result.exception.args[0] == "Please make sure you are using the correct token"

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_add_vars_default(self, mock_patch: MagicMock, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--name=Production', f'--env-file={fpath}']

        result = cli_runner.invoke(add_pipeline_vars_from_file, params)

        assert result.exit_code == 0, result.output
        assert 'Updated pipeline stage Production with id: 2' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/pipeline-stages/2',
            json={
                 'name': 'Production',
                 'priority': 1,
                 'testRunPriority': 1,
                 'windowsRunnerPoolId': None,
                 'linuxRunnerPoolId': None,
                 'variables': [
                    {
                        "key": "test_var",
                        "value": "one",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "test_var_two",
                        "value": "",
                        "encrypted": True,
                        "file": False
                    },
                    {
                        "key": ".env",
                        "value": "",
                        "encrypted": True,
                        "file": True
                    },
                    {
                        "key": "FOO",
                        "value": "BAR",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "HELLO",
                        "value": "World",
                        "encrypted": False,
                        "file": False
                    }
                    ]
            },
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_add_vars_overwrite(self, mock_patch: MagicMock, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--name=Production', f'--env-file={fpath}', '--overwrite']

        result = cli_runner.invoke(add_pipeline_vars_from_file, params)

        assert result.exit_code == 0, result.output
        assert 'Updated pipeline stage Production with id: 2' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/pipeline-stages/2',
            json={
                 'name': 'Production',
                 'priority': 1,
                 'testRunPriority': 1,
                 'windowsRunnerPoolId': None,
                 'linuxRunnerPoolId': None,
                 'variables': [
                     {
                         "key": "test_var",
                         "value": "UNO",
                         "encrypted": False,
                         "file": False
                     },
                     {
                         "key": "test_var_two",
                         "value": "deux",
                         "encrypted": False,
                         "file": False
                     },
                     {
                         "key": ".env",
                         "value": "",
                         "encrypted": True,
                         "file": True
                     },
                     {
                         "key": "FOO",
                         "value": "BAR",
                         "encrypted": False,
                         "file": False
                     },
                     {
                         "key": "HELLO",
                         "value": "World",
                         "encrypted": False,
                         "file": False
                     }
                    ]
            },
            headers=expected_headers
        )


class TestEnvFile:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_env_not_exist(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--environment-key=fake', f'--env-file={fpath}']

        result = cli_runner.invoke(add_env_vars_from_file, params)

        assert result.exception.args[0] == "Environment with key: fake does not exist"
        mock_get.assert_any_call(
            'https://api.testery.io/api/environments',
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get_401)
    def test_bad_auth(self, fake_token: str, cli_runner: CliRunner):
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--environment-key=production', f'--env-file={fpath}']

        result = cli_runner.invoke(add_env_vars_from_file, params)

        assert result.exit_code == 1
        assert result.exception.args[0] == "Please make sure you are using the correct token"

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_add_vars_default(self, mock_patch: MagicMock, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--environment-key=production', f'--env-file={fpath}']

        result = cli_runner.invoke(add_env_vars_from_file, params)

        assert result.exit_code == 0, result.output
        assert 'Updated environment production with id: 99' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/environments/99',
            json={
                'key': 'production',
                'name': 'Production',
                'pipelineStageId': 136,
                'url': 'https://testery.app',
                'variables': [
                    {
                        "key": "test_var",
                        "value": "one",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "test_var_two",
                        "value": "",
                        "encrypted": True,
                        "file": False
                    },
                    {
                        "key": ".env",
                        "value": "",
                        "encrypted": True,
                        "file": True
                    },
                    {
                        "key": "FOO",
                        "value": "BAR",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "HELLO",
                        "value": "World",
                        "encrypted": False,
                        "file": False
                    }
                ]},
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_add_vars_overwrite(self, mock_patch: MagicMock, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--environment-key=production', f'--env-file={fpath}', '--overwrite']

        result = cli_runner.invoke(add_env_vars_from_file, params)

        assert result.exit_code == 0, result.output
        assert 'Updated environment production with id: 99' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/environments/99',
            json={
                'key': 'production',
                'name': 'Production',
                'pipelineStageId': 136,
                'url': 'https://testery.app',
                'variables': [
                    {
                        "key": "test_var",
                        "value": "UNO",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "test_var_two",
                        "value": "deux",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": ".env",
                        "value": "",
                        "encrypted": True,
                        "file": True
                    },
                    {
                        "key": "FOO",
                        "value": "BAR",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "HELLO",
                        "value": "World",
                        "encrypted": False,
                        "file": False
                    }
                ]},
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    @patch('requests.patch', side_effect=mocked_requests_patch)
    def test_add_vars_default_no_url_no_stage(self, mock_patch: MagicMock, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        fpath = join(dirname(realpath(__file__)), 'testdata', 'test.env')
        params = [f'--token={fake_token}', '--environment-key=demo', f'--env-file={fpath}']

        result = cli_runner.invoke(add_env_vars_from_file, params)

        assert result.exit_code == 0, result.output
        assert 'Updated environment demo with id: 42' in result.output
        mock_patch.assert_called_once_with(
            'https://api.testery.io/api/environments/42',
            json={
                'key': 'demo',
                'name': 'demo',
                'variables': [
                    {
                        "key": "FOO",
                        "value": "BAR",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "HELLO",
                        "value": "World",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "test_var",
                        "value": "UNO",
                        "encrypted": False,
                        "file": False
                    },
                    {
                        "key": "test_var_two",
                        "value": "deux",
                        "encrypted": False,
                        "file": False
                    },
                ]},
            headers=expected_headers
        )
