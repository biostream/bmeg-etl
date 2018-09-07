
##################
### Gene Ontology

class: Workflow
cwlVersion: v1.0

$namespaces:
  bmeg: http://bmeg.io

inputs:
  SIF:
    type: File
    bmeg:key: source/PathwayCommons10.All.hgnc.sif.gz
    bmeg:url: http://www.pathwaycommons.org/archives/PC2/v10/PathwayCommons10.All.hgnc.sif.gz
  GENEMAP:
    type: File
    bmeg:key: source/hgnc_complete_set.txt
    bmeg:url: ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt

steps:
  pathway-commons-transform:
    run: pathway-commons/pathway-commons-transform.cwl
    in:
      SIF: SIF
      GENEMAP: GENEMAP
    out:
      - OUTPUT

outputs:
  OUTPUT:
    type: File
    outputSource: pathway-commons-transform/OUTPUT
    bmeg:key: biostream/pathway-commons.sif.json
