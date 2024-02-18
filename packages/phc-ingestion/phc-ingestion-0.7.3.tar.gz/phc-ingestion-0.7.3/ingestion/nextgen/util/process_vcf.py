import gzip
import shutil
from logging import Logger
from ingestion.nextgen.util.variant_table import extract_variant_table


class Variant:
    def __init__(self, fields):
        self.chr_pos = fields[0]
        self.info = []
        self.frmt = fields[2]
        self.smpl = fields[3]

    def move_af_value(self):
        # Relocate and transform AF from the FORMAT section to the INFO section for each variant
        zipped = dict(zip(self.frmt, self.smpl))
        af = float(zipped.get("AF", 999.99))
        if af == 999.99:
            raise RuntimeError(f"Failed to find AF for variant: {self.chr_pos}")

        self.info.append("AF=" + "{:.4f}".format(af))

    def afdp_to_dp(self):
        # Rename AFDP to just DP in FORMAT for each variant
        if "AFDP" in self.frmt:
            self.frmt = list(map(lambda x: x.replace("AFDP", "DP"), self.frmt))
        else:
            raise RuntimeError(f"Failed to find AFDP for variant: {self.chr_pos}")

    def calculate_af(self):
        # Recalculate AF values from AD, includes biallelic/multiallelic handling for future decomposition
        # i.e. chr8	127790148	.	CTTT	C,CT	7243.73	.	SOR=0.309	GT:AD:DP	1/2:5,189,62:256

        zipped = dict(zip(self.frmt, self.smpl))
        ad = zipped.get("AD", 999.99)
        if ad == 999.99:
            raise RuntimeError(f"Failed to find AD for variant: {self.chr_pos}")

        ad_split = ad.split(",")
        total_dp = sum([int(i) for i in ad_split])

        afs = []
        # Start at the first REF allele
        for ad in ad_split[1:]:
            if ad == "0":
                af = 0.0
            else:
                af = float(int(ad) / total_dp)
            afs.append("{:.4f}".format(af))

        self.info.append(f'AF={",".join(afs)}')

    def prune_var(self):
        # Pruning FORMAT to only include GT, AD, and DP values.
        # Pruning VARIANT column to only include the corresponding values.
        zipped = dict(zip(self.frmt, self.smpl))
        frmt_smpl_dict = {frmt: smpl for frmt, smpl in zipped.items() if frmt in ["GT", "AD", "DP"]}
        self.pruned_info = self.info[0]
        self.pruned_frmt = ":".join(list(frmt_smpl_dict.keys()))
        self.pruned_smpl = ":".join(list(frmt_smpl_dict.values()))


def transform_vcf(
    vcf_in_file: str,
    headers: list,
    variants: list,
    sequence_type: str,
    xml_in_file: str,
    log: Logger,
):
    short_variant_table = extract_variant_table(
        xml_in_file=xml_in_file, variant_type="short", log=log
    )

    log.info(f"Performing file transformations on {vcf_in_file}")
    approved_chr_list = ["chr" + str(i) for i in range(1, 23)] + ["chrX", "chrY", "chrM"]
    vcf_out = []

    for header in headers:
        # Add AF/INFO and DP/FORMAT to header if somatic (already in germline headers)
        if "#CHROM" in header and sequence_type == "somatic":
            vcf_out.append(
                '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele frequency, for each ALT allele, in the same order as listed">'
            )
            vcf_out.append('##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read depth">')
            vcf_out.append(
                '##INFO=<ID=VENDSIG,Number=1,Type=String,Description="Vendor Significance">'
            )
        vcf_out.append(header.strip())

    for var in variants:
        split_var = var.split("\t")
        if len(split_var) != 10:
            raise RuntimeError(
                f"Variant does not contain correct number of fields. Should be 10 when {len(split_var)} were detected: {var}"
            )
        if split_var[0] not in approved_chr_list:
            continue

        chr_pos = f"{split_var[0]} {split_var[1]}"
        info_string = split_var[7]
        # Ignore structural variants
        if "SVTYPE" in info_string:
            continue

        info = split_var[7].split(";")
        frmt = split_var[8].split(":")
        smpl = split_var[9].split(":")
        working = Variant([chr_pos, info, frmt, smpl])

        if sequence_type == "somatic":
            working.move_af_value()
            working.afdp_to_dp()
            working.prune_var()

        elif sequence_type == "germline":
            working.calculate_af()
            working.prune_var()

        if sequence_type == "somatic" and not short_variant_table.empty:
            split_var[7] = add_vendsig_to_info(
                working.pruned_info, short_variant_table, split_var[0], int(split_var[1])
            )
        else:
            split_var[7] = f"{working.pruned_info};VENDSIG=Unknown"
        split_var[8] = working.pruned_frmt
        split_var[9] = working.pruned_smpl
        vcf_out.append("\t".join(split_var))

    vcf_out = "\n".join(vcf_out) + "\n"
    return vcf_out


def export_vcf(vcf_out: str, vcf_path: str, log: Logger):
    log.info(f"VCF transformation complete. Writing to {vcf_path}")
    with gzip.open(f"{vcf_path}", "wt") as w:
        w.write(vcf_out)


def process_vcf(
    vcf_in_file: str, root_path: str, prefix: str, sequence_type: str, xml_in_file: str, log: Logger
):
    line_count = 0
    vcf_path = f"{root_path}/{prefix}.modified.{sequence_type}.vcf.gz"

    headers = []
    variants = []

    with gzip.open(vcf_in_file, "rt") as f:
        lines = f.readlines()
        line_count = len(lines)
        if line_count == 0:
            log.error(f"Input VCF file {vcf_in_file} is empty")
            log.info(f"Copying file to {vcf_path}")
            shutil.copy(vcf_in_file, vcf_path)
            return {"vcf_path_name": vcf_path, "vcf_line_count": line_count}

        else:
            for line in lines:
                if line.startswith("#"):
                    headers.append(line)
                else:
                    variants.append(line)

            if len(variants) == 0:
                log.error(f"Input VCF file {vcf_in_file} contains headers but no variants")
                log.info(f"Copying file to {vcf_path}")
                shutil.copy(vcf_in_file, vcf_path)
                return {"vcf_path_name": vcf_path, "vcf_line_count": line_count}

            else:
                vcf_out = transform_vcf(
                    vcf_in_file, headers, variants, sequence_type, xml_in_file, log
                )
                export_vcf(vcf_out, vcf_path, log)

    return {"vcf_path_name": vcf_path, "vcf_line_count": line_count}


def map_vendsig(vendsig: str) -> str:
    if vendsig in ["Pathogenic"]:
        return "VENDSIG=Pathogenic"
    elif vendsig in ["Likely Pathogenic"]:
        return "VENDSIG=Likely pathogenic"
    elif vendsig in ["VUS"]:
        return "VENDSIG=Uncertain significance"
    else:
        raise RuntimeError(f"Unable to map vendor significance: {vendsig}")


def add_vendsig_to_info(info: str, short_var_table, chrom: str, pos: str) -> str:
    mapped_vendsig = None
    for index, row in short_var_table.iterrows():
        ref_chrom = row["gene"].split(" ")[1].split(":")[0].strip("(")
        ref_pos = int(row["gene"].split(" ")[1].split(":")[1])

        if ref_chrom == chrom:
            if ref_pos == pos or ref_pos + 1 == pos or ref_pos - 1 == pos:
                mapped_vendsig = map_vendsig(row["info"])

    if not mapped_vendsig:
        mapped_vendsig = "VENDSIG=Unknown"

    new_vcf_info = f"{info.strip()};{mapped_vendsig}"
    return new_vcf_info
