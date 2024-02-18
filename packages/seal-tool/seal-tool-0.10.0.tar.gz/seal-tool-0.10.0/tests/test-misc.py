from tests.util import compare_frames, OBSERVED_PATH
from seal.__main__ import main

def test_check_quadrat_list(capsys):
    cmd = ['seal', 'misc', 'check-quadrat-list', './tests/datasets/qlists/invalid.csv',
        str(OBSERVED_PATH / 'invalid-modified.csv')]

    main(cmd)
    captured = capsys.readouterr().out

    assert captured.splitlines() == ['Unusual minimal x coordinate: -1',
        'Unusual minimal y coordinate: 1',
        'Unusual number of quadrats, 8 != 9, (3 * 3)',
        'Possibly redundant column',
        'Missing value(s)']
    compare_frames('invalid-modified.csv')
