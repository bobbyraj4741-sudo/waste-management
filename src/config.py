"""Central configuration: paths, source-file names, and column mappings.

Every stage of the pipeline imports from here so that the raw column names of
the 2024 Waste Data Interrogator live in exactly one place. If the Environment
Agency changes a field name in a future release, only this file needs editing.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Directory layout
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"

for _d in (DATA_INTERIM, DATA_PROCESSED, FIGURES, RESULTS, DOCS):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
# Source workbooks (2024 Waste Data Interrogator, Environment Agency)
# --------------------------------------------------------------------------- #
RECEIVED_XLSB = DATA_RAW / "2024 Waste Data Interrogator - Wastes Received (Excel) - Version 2.xlsb"
REMOVED_XLSB = DATA_RAW / "2024 Waste Data Interrogator - Wastes Removed (Excel) - Version 2.xlsb"

RECEIVED_SHEET = "2024 Waste Received"
REMOVED_SHEET = "2024 Waste Removed"

# --------------------------------------------------------------------------- #
# Raw -> canonical column names.
#
# The two workbooks share most columns but differ on the "counterparty" side:
# the Received sheet records where waste came FROM (origin), the Removed sheet
# records where waste went TO (destination). We map both onto neutral
# `counterparty_*` names and keep a `direction` flag ("received"/"removed").
# --------------------------------------------------------------------------- #
COMMON_RENAME = {
    "Facility RPA": "facility_rpa",
    "Facility Sub Region": "facility_sub_region",
    "Facility WPA": "facility_wpa",
    "Facility District": "facility_district",
    "Permit": "permit",
    "Site Name": "site_name",
    "Operator": "operator",
    "Permit Type": "permit_type",
    "Easting": "easting",
    "Easting ": "easting",  # Received sheet has a trailing space
    "Northing": "northing",
    "Post Code": "post_code",
    "Form": "form",
    "Basic Waste Cat": "basic_waste_cat",
    "EWC Chapter": "ewc_chapter",
    "EWC Sub Chapter": "ewc_sub_chapter",
    "EWC Waste Desc": "ewc_waste_desc",
    "Waste Code": "waste_code",
    "Site Category": "site_category",
    "Facility Type": "facility_type",
    "Fate": "fate",
    "R and D code": "r_and_d_code",
    "SOC Category": "soc_category",
    "SOC Sub Category": "soc_sub_category",
}

RECEIVED_RENAME = {
    **COMMON_RENAME,
    "Recorded Origin": "counterparty",
    "Origin WPA": "counterparty_wpa",
    "Origin Region": "counterparty_region",
    "Tonnes Received": "tonnes",
}

REMOVED_RENAME = {
    **COMMON_RENAME,
    "Recorded Destination": "counterparty",
    "Destination WPA": "counterparty_wpa",
    "Destination Region": "counterparty_region",
    "Tonnes Removed": "tonnes",
}

# Canonical columns we keep in the cleaned analysis table.
CANONICAL_COLUMNS = [
    "direction",           # "received" | "removed"
    "permit",              # regulated facility id (node key)
    "site_name",
    "operator",
    "permit_type",
    "site_category",
    "facility_type",
    "facility_region",     # Facility RPA (the facility's own region)
    "facility_wpa",
    "facility_district",
    "easting",
    "northing",
    "post_code",
    "form",
    "basic_waste_cat",
    "ewc_chapter",
    "ewc_sub_chapter",
    "ewc_waste_desc",
    "waste_code",
    "counterparty",        # origin (received) or destination (removed) place name
    "counterparty_wpa",
    "counterparty_region",
    "fate",                # Recovery / Landfill / Incineration / Treatment / Transfer (D) / ...
    "r_and_d_code",        # R.. = recovery operation, D.. = disposal operation
    "tonnes",
    "soc_category",
    "soc_sub_category",
]

# --------------------------------------------------------------------------- #
# Domain groupings used to derive interpretable indicators.
# `fate` is the cleanest recovery-vs-disposal signal in the dataset.
# --------------------------------------------------------------------------- #
RECOVERY_FATES = {"recovery"}
DISPOSAL_FATES = {"landfill", "incineration"}      # incineration w/o recovery ~ disposal
TRANSFER_FATES = {"transfer (d)"}
TREATMENT_FATES = {"treatment"}

# R/D code prefix: "R" = recovery operation, "D" = disposal operation (EU Waste
# Framework Directive Annexes I & II). Used as a secondary recovery signal.
RECOVERY_CODE_PREFIX = "R"
DISPOSAL_CODE_PREFIX = "D"

RANDOM_STATE = 42
