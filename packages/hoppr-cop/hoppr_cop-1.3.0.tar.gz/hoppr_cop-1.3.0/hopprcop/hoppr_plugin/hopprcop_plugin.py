"""Setup hoppr-cop as a plugin for hoppr.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2022 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/hoppr_plugin/hopprcop_plugin.py
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

import uuid

from pathlib import Path
from typing import TYPE_CHECKING, Final

from hoppr import Affect, BomAccess, HopprPlugin, Result, Sbom, Vulnerability, hoppr_process

import hopprcop

from hopprcop.combined.combined_scanner import CombinedScanner
from hopprcop.reporting import Reporting
from hopprcop.reporting.models import ReportFormat


if TYPE_CHECKING:
    from hoppr import HopprContext


class HopprCopPlugin(HopprPlugin):
    """Hoppr plugin wrapper for hoppr-cop integration."""

    class ComponentVulnerabilityWrapper:
        """Wrapper for the vulnerabilities associated with a component."""

        def __init__(
            self,
            serial_number: str,
            version: int,
            vulnerabilities: list[Vulnerability] | None = None,
        ):
            self.serial_number = serial_number
            self.version = version
            self.vulnerabilities = vulnerabilities or []

    EMBEDDED_VEX: Final[str] = "embedded_cyclone_dx_vex"
    LINKED_VEX: Final[str] = "linked_cyclone_dx_vex"

    bom_access = BomAccess.FULL_ACCESS

    DEFAULT_SCANNERS: Final[list[str]] = [
        "hopprcop.gemnasium.gemnasium_scanner.GemnasiumScanner",
        "hopprcop.grype.grype_scanner.GrypeScanner",
        "hopprcop.trivy.trivy_scanner.TrivyScanner",
        "hopprcop.ossindex.oss_index_scanner.OSSIndexScanner",
    ]

    def __init__(self, context: HopprContext, config: dict | None = None) -> None:
        super().__init__(context, config)

        # Mapping of bom-ref to results - uses purl as ref
        self.bom_ref_to_results: dict[str, HopprCopPlugin.ComponentVulnerabilityWrapper] = {}

        # Mapping of purls to components, try to normalize purls to lowercase
        self.purl_to_component = {
            component.purl.lower(): component for component in self.context.delivered_sbom.components if component.purl
        }

        self.config = self.config or {}
        self.formats: list[str] = self.config.get("result_formats", [self.EMBEDDED_VEX])

        output_dir = Path(self.config.get("output_dir", self.context.collect_root_dir / "generic"))
        output_dir.mkdir(parents=True, exist_ok=True)

        self.reporting = Reporting(
            output_path=output_dir,
            base_name=self.config.get("base_report_name", "hopprcop-vulnerability-results"),
        )

        self.results: dict[str, list[Vulnerability]] = dict.fromkeys(self.purl_to_component, [])

    def get_version(self) -> str:
        """__version__ required for all HopprPlugin implementations."""
        return hopprcop.__version__

    @hoppr_process
    def pre_stage_process(self) -> Result:
        """Supply SBOM to hoppr cop to perform vulnerabilty check."""
        self.get_logger().info("[ Executing hopprcop vulnerability check ]")

        parsed_bom = self.context.delivered_sbom

        combined_scanner = CombinedScanner()
        combined_scanner.set_scanners((self.config or {}).get("scanners", self.DEFAULT_SCANNERS))

        try:
            self.results = combined_scanner.get_vulnerabilities_by_sbom(parsed_bom)
        except Exception as exc:
            return Result.fail(message=str(exc))

        # Build dictionary to go from bom-ref to vulnerabilities
        for purl in self.results:
            self._map_bom_ref_to_vulnerabilities(purl, parsed_bom)

        hoppr_delivered_bom = self._perform_hoppr_bom_updates(parsed_bom.copy(deep=True))
        self._perform_hopprcop_reporting(parsed_bom)

        self.get_logger().flush()

        return Result.success(return_obj=hoppr_delivered_bom)

    def _add_bom_ref_and_flatten(self, external_ref: bool = False) -> list[Vulnerability]:
        # Capture vulnerability id to vulnerability to account multiple components affected by the same vulnerability
        vuln_id_to_vuln: dict[str, Vulnerability] = {}

        for bom_ref, vuln_wrapper in self.bom_ref_to_results.items():
            for vuln in vuln_wrapper.vulnerabilities:
                if not vuln.id:
                    continue

                existing_vuln = vuln_id_to_vuln.get(vuln.id) or vuln

                affect_ref = (
                    f"urn:cdx:{vuln_wrapper.serial_number}/{vuln_wrapper.version}#{bom_ref}"
                    if external_ref
                    else bom_ref
                )

                existing_vuln.affects.append(Affect(ref=affect_ref))
                vuln_id_to_vuln[vuln.id] = existing_vuln

        return sorted(vuln_id_to_vuln.values(), key=self.reporting.get_score, reverse=True)

    def _map_bom_ref_to_vulnerabilities(self, purl_str: str, sbom: Sbom):
        # Generate `serialNumber` for delivered SBOM if it doesn't exist
        *_, bom_serial_number = (sbom.serialNumber or uuid.uuid4().urn).split(":")
        sbom.serialNumber = f"urn:uuid:{bom_serial_number}"

        if component := self.purl_to_component.get(self._normalize_purl_string(purl_str)):
            if sbom.vulnerabilities and component.bom_ref not in self.bom_ref_to_results:
                # Account for existing vulnerabilites on SBOM
                affected = [
                    existing_vulnerability
                    for existing_vulnerability in sbom.vulnerabilities
                    for affect in existing_vulnerability.affects
                    if affect.ref == component.bom_ref
                ]

                self.results[purl_str].extend(affected)

            updated_results = [vuln.copy(deep=True) for vuln in self.results[purl_str]]

            if component.bom_ref not in self.bom_ref_to_results:
                self.bom_ref_to_results[component.bom_ref] = self.ComponentVulnerabilityWrapper(
                    serial_number=sbom.serialNumber,
                    version=sbom.version,
                    vulnerabilities=updated_results,
                )
            elif updated_results:
                self.bom_ref_to_results[component.bom_ref].vulnerabilities.extend(updated_results)
        else:
            self.get_logger().info(f"Could not find purl ({purl_str}) in component map")

    def _normalize_purl_string(self, purl_str: str) -> str:
        # Different purl values being returned from different scanners, attempt to normalize the data
        # by making it lower case and if not found, reversing pypi expectations with - to _.
        normalized_purl = purl_str.lower()
        if normalized_purl not in self.purl_to_component and "pypi" in normalized_purl:
            normalized_purl = normalized_purl.replace("-", "_")

        return normalized_purl

    def _perform_hoppr_bom_updates(self, parsed_bom: Sbom) -> Sbom:
        if self.EMBEDDED_VEX in self.formats:
            flattened_results = self._add_bom_ref_and_flatten()

            # Existing vulnerabilities were accounted for
            parsed_bom.vulnerabilities = flattened_results
        elif self.LINKED_VEX in self.formats:
            flattened_results = self._add_bom_ref_and_flatten(external_ref=True)

            # Existing vulnerabilities were accounted for
            parsed_bom.vulnerabilities.clear()
            vex_bom = Sbom(vulnerabilities=flattened_results)
            (self.reporting.output_path / f"{self.reporting.base_name}-vex.json").write_text(vex_bom.json())

        return parsed_bom

    def _perform_hopprcop_reporting(self, parsed_bom: Sbom):
        if filtered_formats := [
            ReportFormat[fmt.upper()] for fmt in self.formats if fmt not in {self.LINKED_VEX, self.EMBEDDED_VEX}
        ]:
            self.reporting.generate_vulnerability_reports(filtered_formats, self.results, parsed_bom)
