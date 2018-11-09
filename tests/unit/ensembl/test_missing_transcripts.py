import pytest
import os
from transform.ensembl.missing_transcripts import transform
from bmeg.vertex import Transcript


@pytest.fixture
def missing_transcript_ids_filename(request):
    """ get the full path of the test output """
    return os.path.join(request.fspath.dirname, 'source/ensembl/missing_transcript_ids.txt')


def test_simple(emitter_directory, missing_transcript_ids_filename, helpers):
    """ get the missing transcripts """
    transform(output_dir=emitter_directory,
              prefix='missing',
              missing_transcript_ids_filename=missing_transcript_ids_filename)
    transcript_count = helpers.assert_vertex_file_valid(Transcript, '{}/missing.Transcript.Vertex.json'.format(emitter_directory))
    assert transcript_count == 3