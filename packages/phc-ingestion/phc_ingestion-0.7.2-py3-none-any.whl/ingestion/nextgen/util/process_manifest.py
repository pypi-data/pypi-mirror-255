import re
from ruamel.yaml import YAML
from logging import Logger


def transform_date(date: str):
    """mm/dd/yyyy -> yyyy-mm-dd"""
    date_list = date.split("/")
    new_date = f"{date_list[2]}-{date_list[0]}-{date_list[1]}"
    return new_date


def search_and_grab(array: list, search_item: str, grab_index: int):
    """Searches through an array for a string, and returns the item at the specified index after the search item"""
    return array[array.index([i for i in array if re.search(search_item, i)][0]) + grab_index]


def extract_xml_text(xml_in_file: str):
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    patient_info_lines = []
    for line in xml_lines:
        if "Diagnostic Genomics Laboratory " in line:
            in_range_trigger = True
        if "PCM Result:" in line:
            in_range_trigger = False
            break
        if in_range_trigger == True:
            patient_info_lines.append(line.strip())

    return patient_info_lines


def extract_interpretation_text(xml_in_file: str):
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    interpretation_lines = []
    for line in xml_lines:
        if "INTERPRETATION" in line:
            in_range_trigger = True
        if "References" in line:
            in_range_trigger = False
            break
        if in_range_trigger == True:
            interpretation_lines.append(line.strip())

    return interpretation_lines


def get_cell_purity(interpretation_lines: list):
    cell_purity_value = None
    for line in interpretation_lines:
        if "CD138+" in line:
            cell_purity_value = float(re.search(r"\d\d\.\d\d\%", line).group(0)[:-2])
            return cell_purity_value
    if not cell_purity_value:
        return float(00.00)


def extract_patient_data(patient_info_lines: list):
    patient_data = {}
    patient_data["patientInfo"] = {}

    for line in patient_info_lines:
        if "patientLastName" not in patient_data and "Patient Name" in line:
            patientNameArray = line.split(" ")
            first = search_and_grab(patientNameArray, "Name:", 2)
            last = search_and_grab(patientNameArray, "Name:", 1).strip(", ")
            patient_data["patientInfo"]["firstName"] = first
            patient_data["patientInfo"]["lastName"] = last
            patient_data["patientLastName"] = last

        if "patientDOB" not in patient_data and "Birthdate" in line:
            dobArray = line.split(" ")
            dob = search_and_grab(dobArray, "Birthdate:", 1)
            patient_data["patientDOB"] = transform_date(dob)
            patient_data["patientInfo"]["dob"] = transform_date(dob)

        if "mrn" not in patient_data and "MRN #" in line:
            mrnArray = line.split(" ")
            mrn = search_and_grab(mrnArray, "MRN", 2)
            patient_data["mrn"] = mrn
            patient_data["patientInfo"]["identifiers"] = [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": mrn,
                }
            ]

        if "gender" not in patient_data["patientInfo"] and "Gender" in line:
            genderArray = line.split(" ")
            gender = search_and_grab(genderArray, "Gender", 1)
            if gender == "F":
                gender = "female"
            elif gender == "M":
                gender = "male"
            else:
                gender = "other"
            patient_data["patientInfo"]["gender"] = gender

    return patient_data


def extract_test_data(patient_info_lines: list, interpretation_lines: list):
    # Initialize manifest and hard-code some values
    manifest = {}
    manifest["testType"] = "Plasma Cell Myeloma Panel"
    manifest["name"] = "IU Diagnostic Genomics"
    manifest["reference"] = "GRCh38"

    manifest["ihcTests"] = []
    manifest["tumorTypePredictions"] = []
    manifest["orderingMDNPI"] = ""

    manifest["bodySiteSystem"] = "http://lifeomic.com/fhir/sequence-body-site"
    manifest["indicationSystem"] = "http://lifeomic.com/fhir/sequence-indication"

    manifest["medFacilID"] = ""
    manifest["medFacilName"] = "IU Health"

    for line in patient_info_lines:
        if "reportDate" not in manifest and "Laboratory" in line:
            reportArray = line.split(" ")
            report_date = search_and_grab(reportArray, "Laboratory", 1)
            manifest["reportDate"] = transform_date(report_date)
            manifest["indexedDate"] = manifest["reportDate"]

        if "collDate" not in manifest and "Collected" in line:
            collArray = line.split(" ")
            coll_date = search_and_grab(collArray, "Collected", 1)
            manifest["collDate"] = transform_date(coll_date)

        if "receivedDate" not in manifest and "Received" in line:
            recArray = line.split(" ")
            rec_date = search_and_grab(recArray, "Received", 1)
            manifest["receivedDate"] = transform_date(rec_date)

        if "reportID" not in manifest and "Accession" in line:
            reportArray = line.split(" ")
            report_id = search_and_grab(reportArray, "Accession", 2)
            manifest["reportID"] = report_id

        if "orderingMDName" not in manifest and "Physician Name:" in line:
            physArray = line.split(" ")
            phys_last = search_and_grab(physArray, "Name:", 1)
            phys_first = search_and_grab(physArray, "Name:", 2)
            manifest["orderingMDName"] = f"{phys_last} {phys_first}"

        if "indication" not in manifest and "Reason for Referral" in line:
            indicationArray = line.split(" ")
            indication = search_and_grab(indicationArray, "Referral", 1)
            # Accounting for two-word indication
            if "</" not in search_and_grab(indicationArray, "Referral", 2):
                indication = f'{indication} {search_and_grab(indicationArray, "Referral", 2)}'
            manifest["indication"] = indication
            manifest["indicationDisplay"] = indication

        if "bodySite" not in manifest and "Specimen:" in line:
            bodySiteArray = line.split(" ")
            body_site_one = search_and_grab(bodySiteArray, "Specimen:", 1)
            body_site_two = search_and_grab(bodySiteArray, "Specimen:", 2)
            manifest["bodySite"] = f"{body_site_one} {body_site_two}"
            manifest["bodySiteDisplay"] = f"{body_site_one} {body_site_two}"

    cell_purtiy = get_cell_purity(interpretation_lines)
    if cell_purtiy != 00.00:
        manifest["cellPurity"] = cell_purtiy

    return manifest


def process_manifest(
    xml_in_file: str,
    source_file_id: str,
    prefix: str,
    structural_status: bool,
    log: Logger,
):
    test_text = extract_xml_text(xml_in_file)
    interpretation_text = extract_interpretation_text(xml_in_file)
    manifest = extract_test_data(test_text, interpretation_text)
    manifest.update(extract_patient_data(test_text))

    manifest["reportFile"] = f".lifeomic/nextgen/{prefix}/{prefix}.pdf"
    manifest["sourceFileId"] = source_file_id
    manifest["resources"] = [
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.pdf"},
    ]

    manifest["files"] = [
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.copynumber.csv",
            "sequenceType": "somatic",
            "type": "copyNumberVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.somatic.nrm.filtered.vcf.gz",
            "sequenceType": "somatic",
            "type": "shortVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.germline.nrm.filtered.vcf.gz",
            "sequenceType": "germline",
            "type": "shortVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.somatic.updated.bam",
            "sequenceType": "somatic",
            "type": "read",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.germline.updated.bam",
            "sequenceType": "germline",
            "type": "read",
        },
    ]
    if structural_status == True:
        manifest["files"].append(
            {
                "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.structural.csv",
                "sequenceType": "somatic",
                "type": "structuralVariant",
            },
        )

    return manifest
