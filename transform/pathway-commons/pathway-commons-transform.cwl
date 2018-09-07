
cwlVersion: v1.0
class: CommandLineTool
hints:
  DockerRequirement:
    dockerPull: bmeg/bmeg-etl:latest


baseCommand:
  - python
  - /opt/sif_convert.py
  - "--output"
  - "pathwaycommons.json"

inputs:
  SIF:
    type: File
    inputBinding:
      prefix: "--sif"
  GENEMAP:
    type: File
    inputBinding:
      prefix: "--gene-map"

outputs:
  OUTPUT:
    type: File
    outputBinding:
      glob: "pathwaycommons.json"
