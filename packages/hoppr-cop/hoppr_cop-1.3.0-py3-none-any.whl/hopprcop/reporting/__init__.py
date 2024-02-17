"""Provides vulnerability reporting.

--------------------------------------------------------------------------------
SPDX-FileCopyrightText: Copyright © 2023 Lockheed Martin <open.source@lmco.com>
SPDX-FileName: hopprcop/reporting/__init__.py
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

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2
import rich

from hoppr import Affect, Sbom, Tools, Vulnerability, cdx
from packageurl import PackageURL
from rich.box import Box
from rich.table import Table

import hopprcop

from hopprcop.reporting.gitlab.models import (
    Analyzer,
    CvssVectors3x,
    Dependency,
    DependencyFile,
    Identifier,
    Link,
    Location,
    Package,
    ReportFormatForGitlabDependencyScanning as GitlabReport,
    Scan,
    Scanner,
    Vendor,
    Vulnerability as GitlabVulnerability,
)
from hopprcop.reporting.models import ReportFormat


if TYPE_CHECKING:
    from collections.abc import Mapping


class Reporting:
    """Generates reports in multiple formats from a list of vulnerabilities."""

    output_path: Path
    base_name: str

    def __init__(self, output_path: Path, base_name: str):
        self.output_path = output_path
        self.base_name = base_name

    def generate_vulnerability_reports(
        self,
        formats: list[ReportFormat],
        vulnerabilities: Mapping[str, list[Vulnerability]],
        bom: Sbom | None = None,
    ):
        """Generates various vulnerability reports based on specified formats."""
        flattened_vulnerabilties = self._add_purl_as_bom_ref_and_flatten(vulnerabilities)

        if ReportFormat.CYCLONE_DX in formats and bom is not None:
            self.output_path.mkdir(parents=True, exist_ok=True)
            bom.vulnerabilities = flattened_vulnerabilties

            (self.output_path / f"{Path(self.base_name).name}-enhanced.json").write_text(
                bom.json(indent=2), encoding="utf-8"
            )

        if ReportFormat.GITLAB in formats:
            self.generate_gitlab_vulnerability_report(flattened_vulnerabilties)

        if ReportFormat.HTML in formats:
            self._generate_html_report(flattened_vulnerabilties)

        if ReportFormat.TABLE in formats:
            no_border, underline = "    \n", " -  \n"
            simple_box = Box(box=f"{no_border * 2}{underline}{no_border * 5}", ascii=True)

            table = Table("type", "name", "version", "id", "severity", "found by", box=simple_box)

            for finding in self._get_fields_from_vulnerabilities(flattened_vulnerabilties):
                table.add_row(*finding)

            rich.print(table)

    def _add_purl_as_bom_ref_and_flatten(
        self, vulnerabilities: Mapping[str, list[Vulnerability]]
    ) -> list[Vulnerability]:
        flattened_vulnerabilities: list[Vulnerability] = []

        for purl, vuln_list in vulnerabilities.items():
            for vuln in vuln_list or []:
                vuln.affects = vuln.affects or []
                if not any(affect for affect in vuln.affects if affect.ref == purl):
                    vuln.affects.append(Affect(ref=purl))
                flattened_vulnerabilities.append(vuln)

        flattened_vulnerabilities.sort(key=self.get_score, reverse=True)
        return flattened_vulnerabilities

    def get_score(self, vuln_to_score: Vulnerability) -> float:
        """Return best score of specified Vulnerability."""
        best_rating = self._get_best_rating(vuln_to_score.ratings)

        if best_rating is None or best_rating.score is None:
            return 0.0

        return best_rating.score

    def _get_fields_from_vulnerabilities(self, vulnerabilities: list[Vulnerability]) -> list[list[str | None]]:
        findings = []

        def get_fields(vuln: Vulnerability) -> list[str | None]:
            tool_names = []
            if vuln.tools and vuln.tools.components:
                for tool in vuln.tools.components:
                    if tool.supplier and tool.supplier.name:
                        tool_names.append((tool.name, tool.supplier.name))
                    else:
                        tool_names.append((tool.name, ""))

            vuln.tools = vuln.tools or Tools()
            vuln_tools = [tool for tool in vuln.tools.components if vuln.tools and vuln.tools.components]
            tools = [f"{(tool.supplier or cdx.OrganizationalEntity()).name} {tool.name}" for tool in vuln_tools]

            severity = self._get_severity(vuln.ratings)

            if severity == "critical":
                severity = "[red]critical[/]"
            elif severity == "high":
                severity = "[bright_yellow]high[/]"

            if not vulnerability.affects:
                return []

            purl = PackageURL.from_string(vulnerability.affects[0].ref)

            return [purl.type, purl.name, purl.version, vuln.id, severity, " | ".join(tools)]

        for vulnerability in vulnerabilities:
            findings.append(get_fields(vulnerability))

        return findings

    def _copy_assets(self):
        assets_dir = Path(__file__).parent / "templates" / "assets"
        assets = ["vulnerabilities.css"]

        output_path = self.output_path / "assets"
        output_path.mkdir(exist_ok=True, parents=True)

        for asset in assets:
            template_data = (assets_dir / asset).read_text(encoding="utf-8")
            (output_path / asset).write_text(template_data)

    def _generate_html_report(self, combined_list: list[Vulnerability]):
        self.output_path.mkdir(parents=True, exist_ok=True)
        output_path = self.output_path / f"{Path(self.base_name).name}-vulnerabilities.html"

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"))
        env.filters["severity"] = self._get_severity
        template = env.get_template("vulnerabilities.html")

        self._copy_assets()

        severity_classes = {
            "critical": "bg-red-100 rounded-lg py-5 px-6 mb-4 text-base text-red-700 mb-3",
            "high": "bg-yellow-100 rounded-lg py-5 px-6 mb-4 text-base text-yellow-700 mb-3",
            "medium": "bg-gray-50 rounded-lg py-5 px-6 mb-4 text-base text-gray-500 mb-3",
            "info": "bg-gray-50 rounded-lg py-5 px-6 mb-4 text-base text-gray-500 mb-3",
            "low": "bg-gray-50 rounded-lg py-5 px-6 mb-4 text-base text-gray-500 mb-3",
            "unknown": "bg-gray-50 rounded-lg py-5 px-6 mb-4 text-base text-gray-500 mb-3",
            "none": "bg-gray-50 rounded-lg py-5 px-6 mb-4 text-base text-gray-500 mb-3",
        }

        result = template.render(
            {"findings": combined_list, "severity_classes": severity_classes, "base_name": self.base_name},
        )

        output_path.write_text(result, encoding="utf-8")

        self._generate_vuln_detail_reports(combined_list, severity_classes)

    def _generate_vuln_detail_reports(self, vulnerabilities: list[Vulnerability], severity_classes: dict[str, str]):
        output_path = self.output_path / f"{Path(self.base_name).name}-details"
        output_path.mkdir(exist_ok=True, parents=True)

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(Path(__file__).parent / "templates"))
        env.filters["featured_link"] = self._get_featured_link
        template = env.get_template("vulnerability_details.html")

        for vuln in vulnerabilities:
            if not vuln.affects:
                continue

            purl = PackageURL.from_string(vuln.affects[0].ref)
            result = template.render(
                {
                    "type": purl.type,
                    "namespace": purl.namespace,
                    "name": purl.name,
                    "version": purl.version,
                    "severity_classes": severity_classes,
                    "vulnerability": vuln,
                    "purl": purl.to_string(),
                    "base_name": self.base_name,
                },
            )

            (output_path / f"{vuln.id}.html").write_text(result, encoding="utf-8")

    def generate_gitlab_vulnerability_report(self, vulnerabilities: list[Vulnerability]):
        """Renders the vulnerabilities report for gitlab."""
        # Note the JSON schema for this report can be found at
        # https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/blob/master/dist/dependency-scanning-report-format.json

        report = GitlabReport(
            scan=Scan(
                analyzer=Analyzer(
                    id="hoppr-cop", name="Hoppr Cop", version=hopprcop.__version__, vendor=Vendor(name="Hoppr")
                ),
                end_time=datetime.now().replace(microsecond=0).isoformat(),
                scanner=Scanner(
                    id="hoppr-cop", name="Hoppr Cop", version=hopprcop.__version__, vendor=Vendor(name="Hoppr")
                ),
                start_time=datetime.now().replace(microsecond=0).isoformat(),
                status="success",
                type="dependency_scanning",
            ),
            version="15.0.7",
            vulnerabilities=[],
            remediations=[],
            dependency_files=[],
        )

        dependencies_by_format: dict[str, list[Dependency]] = defaultdict(list, {})

        purls = [vuln.affects[0].ref for vuln in vulnerabilities if vuln.affects]

        self.output_path.mkdir(parents=True, exist_ok=True)
        output_path = self.output_path / "gl-dependency-scanning-report.json"

        for purl_str in purls:
            purl = PackageURL.from_string(purl_str)
            dependencies_by_format[purl.type].append(
                Dependency(package=Package(name=purl.name), version=str(purl.version))
            )

        for vuln in vulnerabilities:
            report.vulnerabilities.extend(filter(None, [self._generate_gitlab_row(vuln)]))

        for repo_format in dependencies_by_format:
            report.dependency_files.append(
                DependencyFile(
                    package_manager=repo_format,
                    path="cyclonedx.bom",
                    dependencies=dependencies_by_format[repo_format],
                )
            )

        output_path.write_text(data=report.json(exclude_none=True, exclude_unset=True, indent=2), encoding="utf-8")

    @staticmethod
    def _get_featured_link(advisories: list[cdx.Advisory] | None) -> str | None:
        if advisories is not None:
            for adv in advisories:
                url = "" if adv.url is None else adv.url
                if "https://snyk.io/" in url:
                    return url
        return None

    def _get_severity(self, ratings: list[cdx.Rating] | None) -> str:
        best_rating = self._get_best_rating(ratings)

        return str(best_rating.severity if best_rating else "none")

    @staticmethod
    def _get_best_rating(ratings: list[cdx.Rating] | None) -> cdx.Rating | None:
        ratings = ratings or []
        default_rating = ratings[0] if ratings else None

        methods = [str(rating.method) if rating.method else "none" for rating in ratings]

        preferred_method = None
        if "CVSSv31" in methods:
            preferred_method = "CVSSv31"
        elif "CVSSv3" in methods:
            preferred_method = "CVSSv3"
        elif "CVSSv2" in methods:
            preferred_method = "CVSSv2"

        return next((rating for rating in ratings if str(rating.method) == preferred_method), default_rating)

    def _generate_gitlab_row(self, vuln: Vulnerability) -> GitlabVulnerability | None:
        """Generates a report row."""
        # Ensure `affects` and `tools` are non-empty lists
        if not (vuln.id and vuln.affects and vuln.tools):
            return None

        purl = PackageURL.from_string(vuln.affects[0].ref)
        severity = self._get_severity(vuln.ratings).title()

        return GitlabVulnerability(
            id=vuln.id,
            name=vuln.id,
            description=vuln.description,
            severity=severity if severity != "none" else "Info",  # type: ignore[arg-type]
            solution=vuln.recommendation or "",
            identifiers=[Identifier(type=vuln.id.split("-")[0].lower(), name=vuln.id, value=vuln.id)],
            cvss_vectors=[
                CvssVectors3x(vendor=rating.source.name if rating.source else "unknown", vector=rating.vector)
                for rating in vuln.ratings or []
                if rating.vector
            ]
            or None,
            links=[Link(url=advisory.url) for advisory in vuln.advisories or []],
            location=Location(
                file="cyclonedx.bom",
                dependency=Dependency(
                    package=Package(name=purl.name),
                    version=purl.version or "",
                ),
            ),
        )
