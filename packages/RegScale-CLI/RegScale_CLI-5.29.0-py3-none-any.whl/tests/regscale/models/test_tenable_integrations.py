import json
from pathlib import Path
from random import randint
from unittest.mock import MagicMock, patch

import pytest
from lxml import etree

from regscale.core.app.utils.nessus_utils import (
    cpe_xml_to_dict,
    get_cpe_file,
    lookup_cpe_item_by_name,
    lookup_kev,
)
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models.integration_models.nessus import NessusReport, Plugin
from regscale.models.integration_models.tenable import TenableIOAsset


@pytest.fixture
def cpe_items():
    cpe_root = etree.parse(get_cpe_file())
    dat = cpe_xml_to_dict(cpe_root)
    return dat


@pytest.fixture
def new_assets():
    with open("./tests/test_data/ten_assets.json", "r") as f:
        dat = json.load(f)
    assets = [TenableIOAsset(**a) for a in dat]
    return assets


@pytest.fixture
def new_vulns():
    with open("./tests/test_data/ten_vulns.json", "r") as f:
        dat = json.load(f)
    vulns = [NessusReport(**v) for v in dat]
    return vulns


@pytest.fixture
def sync_vuln_result():
    dat = {
        "asset": {
            "device_type": "general-purpose",
            "hostname": "WIN-HJFQ8SOFVCP",
            "uuid": "ef2eed0a-29b3-45a2-af6a-3d12141d1a71",
            "ipv4": "10.40.16.200",
            "netbios_name": "WIN-HJFQ8SOFVCP",
            "operating_system": ["Microsoft Windows"],
            "network_id": "32df72f3-5914-4c54-8e28-26a924c8c6ca",
            "tracked": True,
        },
        "output": "\nAn SMB server is running on this port.\n",
        "plugin": {
            "bid": [11011],
            "checks_for_default_account": False,
            "checks_for_malware": False,
            "description": "The remote service understands the CIFS (Common Internet File System) or "
            "Server Message Block (SMB) protocol, used to provide shared access to files, "
            "printers, etc between nodes on a network.",
            "exploited_by_malware": False,
            "exploited_by_nessus": False,
            "family": "Windows",
            "family_id": 7,
            "id": 11011,
            "in_the_news": False,
            "name": "Microsoft Windows SMB Service Detection",
            "modification_date": "2021-02-11T00:00:00Z",
            "publication_date": "2002-06-05T00:00:00Z",
            "risk_factor": "info",
            "synopsis": "A file / print sharing service is listening on the remote host.",
            "type": "REMOTE",
            "unsupported_by_vendor": False,
            "version": "1.43",
        },
        "port": {"port": 139, "protocol": "TCP", "service": "smb"},
        "scan": {
            "schedule_uuid": "template-0962c046-6816-1fa3-a5c4-ab987819db38a7aa1358e9a1e7eb",
            "started_at": "2023-11-05T04:05:03.266Z",
            "uuid": "0ec1bf66-28e1-4e19-9894-60a19556c1d9",
        },
        "severity": "info",
        "severity_id": 0,
        "severity_default_id": 0,
        "severity_modification_type": "NONE",
        "first_found": "2022-09-18T10:44:50.586Z",
        "last_found": "2023-11-05T07:21:39.476Z",
        "state": "OPEN",
        "indexed": "2023-11-05T07:22:28.474691Z",
    }
    result = NessusReport(**dat)
    return iter([result])


@pytest.mark.skip(reason="Manual test")
def test_nessus_processing():
    folder_path = Path().absolute() / "test_data"
    regscale_ssp_id = 2
    NessusReport.process_nessus_files(
        folder_path=folder_path, regscale_ssp_id=regscale_ssp_id
    )


@patch("regscale.core.app.application.Application")
@patch("regscale.models.integration_models.tenable.TenableIOAsset.sync_to_regscale")
def test_fetch_assets(mock_app, new_assets):
    # Call the fetch_assets function
    assets = new_assets
    app = mock_app
    with patch.object(TenableIOAsset, "sync_to_regscale") as mock_sync:
        mock_sync(app=app, assets=assets, ssp_id=2)

        # Check that the sync_to_regscale method was called with the correct arguments
        mock_sync.assert_called_once_with(app=app, assets=assets, ssp_id=2)


@patch("regscale.models.integration_models.nessus.NessusReport.sync_to_regscale")
def test_sync_nessus_reports(mock_sync):
    # Create some mock NessusReport objects to pass to the sync_nessus_reports function
    report1 = MagicMock(spec=NessusReport)
    report2 = MagicMock(spec=NessusReport)

    # Call the sync_nessus_reports function with the mock objects
    mock_sync([report1, report2], 123)

    # Check that the sync_to_regscale method was called with the expected arguments
    mock_sync.assert_called_once_with([report1, report2], 123)


def test_kev_lookup():
    cve = "CVE-1234-3456"
    data = pull_cisa_kev()
    avail = [dat["cveID"] for dat in data["vulnerabilities"]]
    index = randint(0, len(avail))
    assert lookup_kev(cve, data)[0] is None
    assert lookup_kev(avail[index], data)[0]


def test_cpe_lookup(cpe_items):
    name = "cpe:/a:gobalsky:vega:0.49.4"
    lookup_cpe_item_by_name(name, cpe_items)


def test_sync_vulns_data(sync_vuln_result):
    vulns = sync_vuln_result
    assert vulns
