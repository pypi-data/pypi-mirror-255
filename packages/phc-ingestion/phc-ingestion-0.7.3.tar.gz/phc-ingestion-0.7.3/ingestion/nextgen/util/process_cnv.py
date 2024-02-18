import pandas as pd
from logging import Logger

from ingestion.nextgen.util.variant_table import extract_variant_table
from ingestion.nextgen.util.interpretation import map_interpretation


def process_cnv(xml_in_file: str, cnv_in_file: str, root_path: str, prefix: str, log: Logger):
    copy_number_path_name = f"{root_path}/{prefix}.copynumber.csv"
    sample_id = prefix

    copy_number_variant_rows = []
    copy_number_variant_table = extract_variant_table(
        xml_in_file=xml_in_file, variant_type="copy number", log=log
    )

    with open(cnv_in_file, "r") as f:
        cnv_rows = f.readlines()

    for row in cnv_rows[1:]:
        working = row.strip().split("\t")

        chromosome = "chr" + working[0]
        start_position = working[1]
        end_position = working[2]
        gene = working[3]
        gene_id_only = gene.split("_")[0]
        if gene_id_only.endswith("CN"):
            gene_id_only = gene_id_only[:-2]

        copy_number = working[4]
        status = working[5]
        if status == "normal":
            status = "neutral"

        # Hard-code
        attributes = {}

        # Scrape interpretation
        interpretation = None
        if not copy_number_variant_table.empty:
            for index, row in copy_number_variant_table.iterrows():
                ref_gene = row["gene"].split(" ")[0]
                ref_coord = row["gene"].split(" ")[1]

                if (
                    ref_gene == gene_id_only
                    and ref_coord == f"({chromosome}:{start_position}_{end_position})"
                ):
                    interpretation = map_interpretation(row["info"], log)

        if not interpretation:
            interpretation = "unknown"

        copy_number_variant_rows.append(
            f"{sample_id},{gene_id_only},{copy_number},{status},{attributes},{chromosome},{start_position},{end_position},{interpretation}\n"
        )

    log.info(f"Saving file to {copy_number_path_name}")
    with open(copy_number_path_name, "w") as f:
        f.write(
            "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation\n"
        )
        for cnv_text_row in copy_number_variant_rows:
            f.write(cnv_text_row)

    return copy_number_path_name
