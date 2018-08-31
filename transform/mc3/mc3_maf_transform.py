
""" transform a maf file into vertexs[variant, allele]   """
from bmeg.vertex import Biosample, Callset, Gene
from bmeg.edge import AlleleCall

from bmeg.maf.maf_transform import main, get_value, MAFTransformer
from bmeg.maf.maf_transform import transform as parent_transform

TUMOR_SAMPLE_BARCODE = "Tumor_Sample_Barcode"  # 15
NORMAL_SAMPLE_BARCODE = "Matched_Norm_Sample_Barcode"  # 16

MC3_EXTENSION_MAF_KEYS = [
    'Verification_Status', 'Validation_Status', 'Mutation_Status', 'Sequencing_Phase', 'Sequence_Source', 'Validation_Method', 'Score', 'BAM_File', 'Sequencer', 'Tumor_Sample_UUID', 'Matched_Norm_Sample_UUID', 'HGVSc', 'HGVSp', 'HGVSp_Short', 'Transcript_ID', 'Exon_Number', 'Allele', 'Gene', 'Feature', 'Feature_type', 'Consequence', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'ALLELE_NUM', 'DISTANCE', 'STRAND',
    'SYMBOL', 'SYMBOL_SOURCE', 'HGNC_ID', 'BIOTYPE', 'CANONICAL', 'CCDS', 'ENSP', 'SWISSPROT', 'TREMBL', 'UNIPARC', 'RefSeq', 'SIFT', 'PolyPhen', 'EXON', 'INTRON', 'DOMAINS', 'GMAF', 'AFR_MAF', 'AMR_MAF', 'ASN_MAF', 'EAS_MAF', 'EUR_MAF', 'SAS_MAF', 'AA_MAF', 'EA_MAF', 'CLIN_SIG', 'SOMATIC', 'PUBMED', 'MOTIF_NAME', 'MOTIF_POS', 'HIGH_INF_POS', 'MOTIF_SCORE_CHANGE', 'IMPACT', 'PICK', 'VARIANT_CLASS', 'TSL', 'HGVS_OFFSET', 'PHENO', 'MINIMISED', 'ExAC_AF', 'ExAC_AF_AFR', 'ExAC_AF_AMR', 'ExAC_AF_EAS', 'ExAC_AF_FIN', 'ExAC_AF_NFE', 'ExAC_AF_OTH', 'ExAC_AF_SAS', 'GENE_PHENO', 'FILTER', 'COSMIC', 'CENTERS', 'CONTEXT', 'DBVS', 'NCALLERS'
]

MC3_EXTENSION_CALLSET_KEYS = [
    't_depth', 't_ref_count', 't_alt_count', 'n_depth', 'n_ref_count', 'n_alt_count', 'FILTER',
    'Match_Norm_Seq_Allele1', 'Match_Norm_Seq_Allele2',
    'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2',
]


class MC3_MAFTransformer(MAFTransformer):

    def barcode_to_sampleid(self, barcode):
        """ create tcga sample barcode """
        return "-".join(barcode.split("-")[0:4])

    def create_gene_gid(self, line):  # pragma nocover
        """ override, create gene_gid from line """
        ensembl_id = line.get('Gene', None)
        return Gene.make_gid(gene_id=ensembl_id)

    def allele_call_maker(self, allele, line=None):
        """ create call from line """
        info = {}
        for k in MC3_EXTENSION_CALLSET_KEYS:
            info[k] = get_value(line, k, None)
        return AlleleCall(info)

    def callset_maker(self, allele, source, centerCol, method, line):
        """ create callset from line """
        barcode = line[TUMOR_SAMPLE_BARCODE]
        sample = barcode
        sample = self.barcode_to_sampleid(barcode)
        sample = Biosample.make_gid(sample)
        sample_callsets = []
        sample_calls = []
        if centerCol in line:
            for c in line[centerCol].split("|"):
                center = c.replace("*", "")
                # callset_id = "%s:%s" % (sample, center)
                callset = Callset(sample,
                                  line[NORMAL_SAMPLE_BARCODE],
                                  center, source)
                sample_callsets.append(callset)
                sample_calls.append((self.allele_call_maker(allele, line),
                                     callset.gid()))
        else:
            callset = Callset(sample,
                              line[NORMAL_SAMPLE_BARCODE],
                              method, source)
            sample_callsets.append(callset)
            sample_calls.append((self.allele_call_maker(allele, line),
                                 callset.gid()))
        return sample_calls, sample_callsets

    def create_allele_dict(self, line, genome='GRCh37'):
        ''' return properly named allele dictionary, populated from line'''
        allele_dict = super(MC3_MAFTransformer, self).create_allele_dict(line, genome)
        annotations = {}
        for key in MC3_EXTENSION_MAF_KEYS:
            value = line.get(key, None)
            if value:
                annotations[key] = value

        allele_dict['annotations'].mc3 = annotations
        return allele_dict


def transform(mafpath, prefix, emitter_name='json', skip=0):
    """ called from tests """
    return parent_transform(mafpath, prefix, emitter_name, skip, transformer=MC3_MAFTransformer())


if __name__ == '__main__':  # pragma: no cover
    """ called from cli """
    main(transformer=MC3_MAFTransformer())
