
cwlVersion: v1.0
class: CommandLineTool
hints:
  DockerRequirement:
    dockerPull: bmeg/bmeg-etl:latest

baseCommand:
  - python
  - /opt/pubmed.py

arguments:
  - "-l"

inputs:
  blank:
    type: boolean?
    default: False

stdout: pubmed-url.list

outputs:
  DATA:
    type: stdout
