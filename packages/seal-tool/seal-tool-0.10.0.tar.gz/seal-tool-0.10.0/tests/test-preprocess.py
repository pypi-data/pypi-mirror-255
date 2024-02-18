from tests.util import compare_frames, compare_stdout, OBSERVED_PATH
from seal.__main__ import main

def test_preprocess(capsys):
    cl = ['seal',
        'preprocess',
        '--no-drop-nas',
        '--checks',
        'dups', 'coords', 'family', 'morph-species', 'nas', 'quartets', 'refs', 'strs', 'species-name', 'species-phase-morph',
        '--dataset',
        './tests/datasets/preprocess.csv',
        '--output',
        str(OBSERVED_PATH / 'preprocessed.csv')]

    main(cl)
    captured = capsys.readouterr().out
    import pathlib
    pathlib.Path('./ptest.txt').write_text(captured)

    compare_frames('preprocessed.csv')
    compare_stdout(captured, 'preprocess.stdout')
