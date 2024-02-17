"""Scan an SBOM using the Trivy CLI.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/trivy/trivy_scanner.py
SPDX-FileType: SOURCE
SPDX-License-Identifier: MIT
--------------------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
--------------------------------------------------------------------------------
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

from pathlib import Path
from subprocess import PIPE, Popen
from typing import ClassVar

import rich

from hoppr import Component, HopprError, Sbom, Vulnerability
from packageurl import PackageURL

from hopprcop.utils import build_bom_dict_from_purls, unsupported_purl_feedback
from hopprcop.vulnerability_scanner import VulnerabilitySuper


class TrivyScanner(VulnerabilitySuper, author="Aquasec", name="Trivy", offline_mode_supported=True):  # pragma: no cover
    """Interacts with the trivy cli to scan an SBOM."""

    # used to store the operating system component discovered in the provided SBOM for generating the SBOM for trivy
    _os_component: Component | None = None

    trivy_os_distro = None

    required_tools_on_path: ClassVar[list[str]] = ["trivy"]
    supported_types: ClassVar[list[str]] = [
        "cargo",
        "conan",
        "deb",
        "gem",
        "golang",
        "gradle",
        "maven",
        "npm",
        "nuget",
        "pypi",
        "rpm",
    ]

    def __init__(self, offline_mode: bool = False, trivy_os_distro: str | None = None):
        self.offline_mode = offline_mode
        self.trivy_os_distro = trivy_os_distro or os.getenv("OS_DISTRIBUTION", None)
        super().__init__()

    def get_vulnerability_db(self) -> bool:
        """Downloads vulnerability database.

        Returns a boolean representation of success.
        """
        args = ["trivy", "image", "--download-db-only", "--no-progress"]
        with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE) as process:
            # Trivy returns all messages as stderr in the 0.48.0 version.
            # To properly report the status of the database update the return code
            # is the primary check with scraping stderr being secondary.
            stdout, stderr = process.communicate()
            rtrn_code = process.returncode
            if rtrn_code == 0:
                if b"Downloading DB" in stderr:
                    rich.print("TrivyScanner: Database Downloaded")
                else:
                    rich.print("TrivyScanner: No update needed for vulnerability database")
                return True
            else:
                rich.print("TrivyScanner: Error occurred while updating the vulnerability database")
                rich.print(f"TrivyScanner: {stderr.decode()}")
                return False

    def get_vulnerabilities_by_purl(self, purls: list[PackageURL]) -> dict[str, list[Vulnerability]]:
        """Get the vulnerabilities for a list of package URLS (purls).

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        bom = build_bom_dict_from_purls(purls)
        self._add_operating_system_component(bom)

        return self.get_vulnerabilities_by_sbom(Sbom.parse_obj(bom))

    def get_vulnerabilities_by_sbom(self, bom: Sbom) -> dict[str, list[Vulnerability]]:
        """Accepts a cyclone dx compatible SBOM and returns a list of vulnerabilities.

        Returns a dictionary of package URL to vulnerabilities or none if no vulnerabilities are found.
        """
        results: dict[str, list[Vulnerability]] = {}

        _win32 = sys.platform == "win32"
        with tempfile.NamedTemporaryFile(mode="w+", delete=not _win32, encoding="utf-8") as bom_file:
            # Remove tools from metadata due to cyclonedx-go only having partial support for spec version 1.5 (as of 0.72.0)
            # TODO: roll back once full support is in cyclonedx-go
            copied_bom = bom.copy(deep=True)
            if copied_bom.metadata:
                copied_bom.metadata.tools = None

            bom_file.write(copied_bom.json())
            bom_file.flush()

            args = ["trivy", "sbom", "--format", "cyclonedx", str(bom_file.name)]
            if self.offline_mode:
                args = [*args, "--skip-db-update", "--offline-scan"]
            cache = os.getenv("CACHE_DIR")

            # Check for unsupported purl types and report if found
            purls = [PackageURL.from_string(component.purl) for component in bom.components or [] if component.purl]
            unsupported_purl_feedback(self._scanner_name, self.supported_types, purls)

            if cache is not None:
                args += ["--cache-dir", cache]

            with Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                if not stdout and stderr:
                    raise HopprError(f"{self.__class__.__name__} generated an exception: {stderr}")

                if _win32:
                    bom_file.close()
                    Path(bom_file.name).unlink()

            bom_dict = json.loads(stdout)

            for vuln_dict in bom_dict["vulnerabilities"]:
                vuln = Vulnerability.parse_obj(vuln_dict)
                for affect in vuln.affects:
                    *_, purl_str = str(affect.ref).split("#")
                    affect.ref = purl_str or affect.ref

                    if vuln.ratings is not None:
                        results.setdefault(affect.ref, [])
                        results[affect.ref].append(vuln)

                vuln.tools = self.scanner_tools()

        return results

    def _add_operating_system_component(self, bom: dict):
        version = None
        distro = None

        if self.trivy_os_distro is not None:
            parts = self.trivy_os_distro.split(":")

            if len(parts) != 2:
                rich.print(f"{self.trivy_os_distro} is an invalid distribution ")
            else:
                distro = parts[0]
                version = parts[1]
        elif self._os_component is not None:
            version = self._os_component.version
            distro = self._os_component.name

        if version is not None and distro is not None:
            component = {
                "bom-ref": "ab16d2bb-90f7-4049-96ce-8c473ba13bd2",
                "type": "operating-system",
                "name": distro,
                "version": version,
            }
            bom["components"].append(component)
