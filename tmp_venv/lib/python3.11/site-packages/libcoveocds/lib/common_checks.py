import collections
import re
from collections.abc import Hashable


def _update_documents_counter(obj, counter):
    if not isinstance(obj, dict):
        return 0
    documents = obj.get("documents", [])
    counter.update(
        document["documentType"]
        for document in documents
        if isinstance(document, dict) and document.get("documentType")
    )
    return len(documents)


def get_releases_aggregates(json_data):
    if not isinstance(json_data, dict):
        return {}
    releases = json_data.get("releases", [])
    if not isinstance(releases, list):
        return {}
    releases = [release for release in releases if isinstance(release, dict)]

    ### Populated by for-loop

    unique_ocids = set()
    tags = collections.Counter()
    unique_lang = set()
    unique_initation_type = set()
    unique_release_ids = set()
    duplicate_release_ids = set()

    # for matching with contracts
    unique_award_id = set()

    planning_ocids = set()
    tender_ocids = set()
    awardid_ocids = set()
    award_ocids = set()
    contractid_ocids = set()
    contract_ocids = set()
    implementation_contractid_ocids = set()
    implementation_ocids = set()

    release_dates = []
    tender_dates = []
    award_dates = []
    contract_dates = []

    release_tender_item_ids = set()
    release_award_item_ids = set()
    release_contract_item_ids = set()
    unique_item_ids = set()

    ### Populated by process_org()

    unique_buyers_identifier = {}
    unique_buyers_name_no_id = set()
    unique_suppliers_identifier = {}
    unique_suppliers_name_no_id = set()
    unique_procuring_identifier = {}
    unique_procuring_name_no_id = set()
    unique_tenderers_identifier = {}
    unique_tenderers_name_no_id = set()

    unique_organisation_schemes = set()
    organisation_identifier_address = set()
    organisation_name_no_id_address = set()
    organisation_identifier_contact_point = set()
    organisation_name_no_id_contact_point = set()

    # Populated by get_item_scheme()
    item_identifier_schemes = set()

    # Populated by/with _update_documents_counter()
    planning_doctype = collections.Counter()
    planning_doc_count = 0
    tender_doctype = collections.Counter()
    tender_doc_count = 0
    tender_milestones_doctype = collections.Counter()
    tender_milestones_doc_count = 0
    award_doctype = collections.Counter()
    award_doc_count = 0
    contract_doctype = collections.Counter()
    contract_doc_count = 0
    implementation_doctype = collections.Counter()
    implementation_doc_count = 0
    implementation_milestones_doctype = collections.Counter()
    implementation_milestones_doc_count = 0

    def process_org(org, unique_id, unique_name):
        if not isinstance(org, dict):
            return

        if (identifier := org.get("identifier")) and (org_id := identifier.get("id")):
            unique_id[org_id] = org.get("name", "") or ""
            scheme = identifier.get("scheme")
            if scheme:
                unique_organisation_schemes.add(scheme)
            if org.get("address"):
                organisation_identifier_address.add(org_id)
            if org.get("contactPoint"):
                organisation_identifier_contact_point.add(org_id)
        else:
            name = org.get("name")
            if name:
                unique_name.add(name)
            if org.get("address"):
                organisation_name_no_id_address.add(name)
            if org.get("contactPoint"):
                organisation_name_no_id_contact_point.add(name)

    def get_item_scheme(item):
        classification = item.get("classification")
        if classification:
            scheme = classification.get("scheme")
            if scheme:
                item_identifier_schemes.add(scheme)

    for release in releases:
        # ### Release Section ###
        ocid = release.get("ocid")
        release_id = release.get("id")
        if not ocid:
            continue
        if release_id:
            if release_id in unique_release_ids:
                duplicate_release_ids.add(release_id)
            unique_release_ids.add(release_id)

        unique_ocids.add(release["ocid"])
        if tag := release.get("tag"):
            if isinstance(tag, Hashable):
                tags.update([tag])
            elif isinstance(tag, list):
                # https://github.com/OpenDataServices/flatten-tool/issues/479
                if len(tag) == 1 and isinstance(tag[0], list):
                    tags.update(tag[0])
                else:
                    tags.update(item for item in tag if isinstance(item, Hashable))
        if initiation_type := release.get("initiationType"):
            unique_initation_type.add(initiation_type)

        if release_date := release.get("date"):
            release_dates.append(str(release_date))

        if language := release.get("language"):
            unique_lang.add(language)
        if buyer := release.get("buyer"):
            process_org(buyer, unique_buyers_identifier, unique_buyers_name_no_id)

        # ### Planning Section ###
        planning = release.get("planning", {})
        if planning and isinstance(planning, dict):
            planning_ocids.add(ocid)
            planning_doc_count += _update_documents_counter(planning, planning_doctype)

        # ### Tender Section ###
        tender = release.get("tender", {})
        if tender and isinstance(tender, dict):
            tender_ocids.add(ocid)
            tender_doc_count += _update_documents_counter(tender, tender_doctype)
            if (tender_period := tender.get("tenderPeriod")) and (start_date := tender_period.get("startDate", "")):
                tender_dates.append(str(start_date))
            if procuring_entity := tender.get("procuringEntity"):
                process_org(procuring_entity, unique_procuring_identifier, unique_procuring_name_no_id)
            for tenderer in tender.get("tenderers") or []:
                process_org(tenderer, unique_tenderers_identifier, unique_tenderers_name_no_id)
            for item in tender.get("items") or []:
                if not isinstance(item, dict):
                    continue
                if item_id := item.get("id"):
                    unique_item_ids.add(item_id)
                if item_id and release_id:
                    release_tender_item_ids.add((ocid, release_id, item_id))
                get_item_scheme(item)
            for milestone in tender.get("milestones") or []:
                tender_milestones_doc_count += _update_documents_counter(milestone, tender_milestones_doctype)

        # ### Award Section ###
        for award in release.get("awards") or []:
            if not isinstance(award, dict):
                continue
            award_id = award.get("id")
            award_ocids.add(ocid)
            if award_id:
                unique_award_id.add(award_id)
                awardid_ocids.add((award_id, ocid))
            if award_date := award.get("date", ""):
                award_dates.append(str(award_date))
            for item in award.get("items") or []:
                if not isinstance(item, dict):
                    continue
                if item_id := item.get("id"):
                    unique_item_ids.add(item_id)
                if item_id and release_id and award_id:
                    release_award_item_ids.add((ocid, release_id, award_id, item_id))
                get_item_scheme(item)
            for supplier in award.get("suppliers") or []:
                process_org(supplier, unique_suppliers_identifier, unique_suppliers_name_no_id)
            award_doc_count += _update_documents_counter(award, award_doctype)

        # ### Contract section
        for contract in release.get("contracts") or []:
            contract_id = contract.get("id")
            contract_ocids.add(ocid)
            if contract_id:
                contractid_ocids.add((contract_id, ocid))
            if (period := contract.get("period")) and (start_date := period.get("startDate", "")):
                contract_dates.append(start_date)
            for item in contract.get("items") or []:
                if not isinstance(item, dict):
                    continue
                if item_id := item.get("id"):
                    unique_item_ids.add(item_id)
                if item_id and release_id and contract_id:
                    release_contract_item_ids.add((ocid, release_id, contract_id, item_id))
                get_item_scheme(item)
            contract_doc_count += _update_documents_counter(contract, contract_doctype)
            if implementation := contract.get("implementation"):
                implementation_ocids.add(ocid)
                if contract_id:
                    implementation_contractid_ocids.add((contract_id, ocid))
                implementation_doc_count += _update_documents_counter(implementation, implementation_doctype)
                for milestone in implementation.get("milestones") or []:
                    implementation_milestones_doc_count += _update_documents_counter(
                        milestone, implementation_milestones_doctype
                    )

    unique_org_identifier_count = len(
        set(unique_buyers_identifier)
        | set(unique_suppliers_identifier)
        | set(unique_procuring_identifier)
        | set(unique_tenderers_identifier)
    )
    unique_org_name_count = len(
        unique_buyers_name_no_id
        | unique_suppliers_name_no_id
        | unique_procuring_name_no_id
        | unique_tenderers_name_no_id
    )

    unique_currency = set()

    def get_currencies(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "currency":
                    if isinstance(value, list):
                        for versioned_value in value:
                            if "value" in versioned_value:
                                unique_currency.add(versioned_value["value"])
                    else:
                        unique_currency.add(value)
                get_currencies(value)
        if isinstance(obj, list):
            for item in obj:
                get_currencies(item)

    get_currencies(json_data)

    return {
        "release_count": len(releases),
        "unique_ocids": sorted(unique_ocids, key=lambda x: str(x)),
        "unique_initation_type": sorted(unique_initation_type, key=lambda x: str(x)),
        "duplicate_release_ids": sorted(duplicate_release_ids, key=lambda x: str(x)),
        "tags": dict(tags),
        "unique_lang": sorted(unique_lang, key=lambda x: str(x)),
        "unique_award_id": sorted(unique_award_id, key=lambda x: str(x)),
        "planning_count": len(planning_ocids),
        "tender_count": len(tender_ocids),
        "award_count": len(awardid_ocids),
        "processes_award_count": len(award_ocids),
        "contract_count": len(contractid_ocids),
        "processes_contract_count": len(contract_ocids),
        "implementation_count": len(implementation_contractid_ocids),
        "processes_implementation_count": len(implementation_ocids),
        "min_release_date": min(release_dates) if release_dates else "",
        "max_release_date": max(release_dates) if release_dates else "",
        "min_tender_date": min(tender_dates) if tender_dates else "",
        "max_tender_date": max(tender_dates) if tender_dates else "",
        "min_award_date": min(award_dates) if award_dates else "",
        "max_award_date": max(award_dates) if award_dates else "",
        "min_contract_date": min(contract_dates) if contract_dates else "",
        "max_contract_date": max(contract_dates) if contract_dates else "",
        "unique_buyers_identifier": unique_buyers_identifier,
        "unique_buyers_name_no_id": sorted(unique_buyers_name_no_id, key=lambda x: str(x)),
        "unique_suppliers_identifier": unique_suppliers_identifier,
        "unique_suppliers_name_no_id": sorted(unique_suppliers_name_no_id, key=lambda x: str(x)),
        "unique_procuring_identifier": unique_procuring_identifier,
        "unique_procuring_name_no_id": sorted(unique_procuring_name_no_id, key=lambda x: str(x)),
        "unique_tenderers_identifier": unique_tenderers_identifier,
        "unique_tenderers_name_no_id": sorted(unique_tenderers_name_no_id, key=lambda x: str(x)),
        "unique_buyers": sorted(
            set(
                [f"{name} ({org_id})" for org_id, name in unique_buyers_identifier.items()]
                + list(unique_buyers_name_no_id)
            )
        ),
        "unique_suppliers": sorted(
            set(
                [f"{name} ({org_id})" for org_id, name in unique_suppliers_identifier.items()]
                + list(unique_suppliers_name_no_id)
            )
        ),
        "unique_procuring": sorted(
            set(
                [f"{name} ({org_id})" for org_id, name in unique_procuring_identifier.items()]
                + list(unique_procuring_name_no_id)
            )
        ),
        "unique_tenderers": sorted(
            set(
                [f"{name} ({org_id})" for org_id, name in unique_tenderers_identifier.items()]
                + list(unique_tenderers_name_no_id)
            )
        ),
        "unique_buyers_count": len(unique_buyers_identifier) + len(unique_buyers_name_no_id),
        "unique_suppliers_count": len(unique_suppliers_identifier) + len(unique_suppliers_name_no_id),
        "unique_procuring_count": len(unique_procuring_identifier) + len(unique_procuring_name_no_id),
        "unique_tenderers_count": len(unique_tenderers_identifier) + len(unique_tenderers_name_no_id),
        "unique_org_identifier_count": unique_org_identifier_count,
        "unique_org_name_count": unique_org_name_count,
        "unique_org_count": unique_org_identifier_count + unique_org_name_count,
        "unique_organisation_schemes": sorted(unique_organisation_schemes, key=lambda x: str(x)),
        "organisations_with_address": len(organisation_identifier_address) + len(organisation_name_no_id_address),
        "organisations_with_contact_point": len(organisation_identifier_contact_point)
        + len(organisation_name_no_id_contact_point),
        "total_item_count": len(release_tender_item_ids)
        + len(release_award_item_ids)
        + len(release_contract_item_ids),
        "tender_item_count": len(release_tender_item_ids),
        "award_item_count": len(release_award_item_ids),
        "contract_item_count": len(release_contract_item_ids),
        "unique_item_ids_count": len(unique_item_ids),
        "item_identifier_schemes": sorted(item_identifier_schemes, key=lambda x: str(x)),
        "unique_currency": sorted(unique_currency, key=lambda x: str(x)),
        "planning_doc_count": planning_doc_count,
        "tender_doc_count": tender_doc_count,
        "tender_milestones_doc_count": tender_milestones_doc_count,
        "award_doc_count": award_doc_count,
        "contract_doc_count": contract_doc_count,
        "implementation_doc_count": implementation_doc_count,
        "implementation_milestones_doc_count": implementation_milestones_doc_count,
        "planning_doctype": dict(planning_doctype),
        "tender_doctype": dict(tender_doctype),
        "tender_milestones_doctype": dict(tender_milestones_doctype),
        "award_doctype": dict(award_doctype),
        "contract_doctype": dict(contract_doctype),
        "implementation_doctype": dict(implementation_doctype),
        "implementation_milestones_doctype": dict(implementation_milestones_doctype),
        "contracts_without_awards": [
            contract
            for release in releases
            for contract in release.get("contracts") or []
            if contract.get("awardID") not in unique_award_id
        ],
    }


def get_records_aggregates(json_data):
    if not isinstance(json_data, dict):
        return {}
    records = json_data.get("records", [])
    if not isinstance(records, list):
        return {}
    records = [record for record in records if isinstance(record, dict)]

    return {
        "count": len(records),
        "unique_ocids": {record["ocid"] for record in records if "ocid" in record},
    }


def get_bad_ocid_prefixes(json_data):
    """Yield tuples with ('ocid', 'path/to/ocid') for ocids with malformed prefixes."""
    if not isinstance(json_data, dict):
        return []

    prefix_regex = re.compile(r"^ocds-[a-z0-9]{6}")

    def _is_bad_prefix(item):
        if (
            isinstance(item, dict)
            and (ocid := item.get("ocid"))
            and isinstance(ocid, str)
            and not prefix_regex.match(ocid)
        ):
            return ocid
        return None

    if records := json_data.get("records"):
        bad_prefixes = []
        if isinstance(records, list):
            for i, record in enumerate(records):
                if not isinstance(record, dict):
                    continue

                if ocid := _is_bad_prefix(record):
                    bad_prefixes.append((ocid, f"records/{i}/ocid"))

                releases = record.get("releases")
                if isinstance(releases, list):
                    for j, release in enumerate(releases):
                        if ocid := _is_bad_prefix(release):
                            bad_prefixes.append((ocid, f"records/{i}/releases/{j}/ocid"))

                compiled_release = record.get("compiledRelease")
                if ocid := _is_bad_prefix(compiled_release):
                    bad_prefixes.append((ocid, f"records/{i}/compiledRelease/ocid"))
        return bad_prefixes

    if releases := json_data.get("releases"):
        bad_prefixes = []
        if isinstance(releases, list):
            for j, release in enumerate(releases):
                if ocid := _is_bad_prefix(release):
                    bad_prefixes.append((ocid, f"releases/{j}/ocid"))
        return bad_prefixes

    return []
