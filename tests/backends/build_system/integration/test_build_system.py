# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import os
import subprocess

import pytest

from tests.backends.build_system.integration import BaseArtifactTest
from tests.backends.build_system.integration import VEnvWorkspace


class TestBuildBackend(BaseArtifactTest):
    def test_exe_with_deps(self, workspace: VEnvWorkspace):
        workspace.call_build_system("portable-exe", download_deps=True)

        self.assert_built_exe_is_correct(workspace.cli_path)

    def test_exe_without_deps(self, workspace: VEnvWorkspace):
        workspace.install_dependencies()
        workspace.install_pyinstaller()
        workspace.call_build_system("portable-exe", download_deps=False)

        self.assert_built_exe_is_correct(workspace.cli_path)

    def test_venv_with_deps(self, workspace: VEnvWorkspace):
        workspace.call_build_system("system-sandbox", download_deps=True)

        self.assert_built_venv_is_correct(workspace.build_path)

    def test_venv_without_deps(self, workspace: VEnvWorkspace):
        workspace.install_dependencies()
        workspace.call_build_system("system-sandbox", download_deps=False)

        self.assert_built_venv_is_correct(workspace.build_path)


class TestBuildBackendFailureCases:
    def test_errors_building_exe_without_pyinstaller(self, workspace, capsys):
        workspace.install_dependencies()
        with pytest.raises(subprocess.CalledProcessError) as e:
            workspace.call_build_system("portable-exe", download_deps=False)
        error_text = e.value.stdout.decode()
        assert "pyinstaller" in error_text
        assert "No such file or directory" in error_text

    def test_errors_building_venv_without_runtime_deps(self, workspace):
        with pytest.raises(subprocess.CalledProcessError) as e:
            workspace.call_build_system("system-sandbox", download_deps=False)
        error_text = e.value.stdout.decode()
        assert "No module named 'flit_core'" in error_text


class TestInstall(BaseArtifactTest):
    def test_install_exe(self, workspace: VEnvWorkspace):
        workspace.call_build_system("portable-exe", download_deps=True)
        workspace.call_install(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        self.assert_installed_exe_is_correct(workspace.bin_path)

    def test_install_venv(self, workspace: VEnvWorkspace):
        workspace.call_build_system("system-sandbox", download_deps=True)
        workspace.call_install(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        self.assert_installed_venv_is_correct(
            workspace.bin_path,
            workspace.lib_path,
        )


class TestUninstall(BaseArtifactTest):
    def test_uninstall_exe(self, workspace: VEnvWorkspace):
        workspace.call_build_system("portable-exe", download_deps=True)
        workspace.call_install(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        workspace.call_uninstall(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        assert os.listdir(workspace.bin_path) == []
        assert os.listdir(workspace.lib_path) == []

    def test_uninstall_venv(self, workspace: VEnvWorkspace):
        workspace.call_build_system("system-sandbox", download_deps=True)
        workspace.call_install(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        workspace.call_uninstall(
            bin_path=workspace.bin_path,
            lib_path=workspace.lib_path,
        )

        assert os.listdir(workspace.bin_path) == []
        assert os.listdir(workspace.lib_path) == []