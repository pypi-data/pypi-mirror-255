from logging import Logger
import pandas as pd
import re


def extract_variant_table(xml_in_file: str, variant_type: str, log: Logger):
    # Narrow down to variant table entries
    with open(xml_in_file, "r") as f:
        xml_lines = f.readlines()

    in_range_trigger = False
    variant_lines = []
    for line in xml_lines:
        if "Gene (Chr. Position, hg38)" in line:
            in_range_trigger = True
        if in_range_trigger == True:
            if "</Table>" in line:
                in_range_trigger = False
                break
            if in_range_trigger == True:
                line = re.sub(r"<T.>", "", line)
                line = re.sub(r"</T.>", "", line)
                line = re.sub(r"<T./>", "", line)
                if line.strip() not in ["", "p."]:
                    variant_lines.append(line.strip())

    # If the test is negative we will have a table with only NA values
    # We return an empty df which we check for later when scraping annotations
    if set(variant_lines[6:]) == {"NA"}:
        log.info(f"No variants present in {variant_type} table")
        return pd.DataFrame()

    # Group by column
    gene_column = [i for i in variant_lines[5::5]]
    type_column = [i for i in variant_lines[6::5]]
    description_column = [i for i in variant_lines[7::5]]
    vaf_column = [i for i in variant_lines[8::5]]
    info_column = [i for i in variant_lines[9::5]]

    variant_df = pd.DataFrame(
        {
            "gene": gene_column,
            "type": type_column,
            "description": description_column,
            "vaf": vaf_column,
            "info": info_column,
        }
    )

    # Drop by variant type
    if variant_type == "copy number":
        variant_df = variant_df[variant_df["type"] == "CNV"]
    elif variant_type == "structural":
        variant_df = variant_df[variant_df["type"] == "Translocation"]
    elif variant_type == "short":
        variant_df = variant_df[variant_df["type"].isin(["Missense", "Frameshift", "Stop gained"])]

    return variant_df
