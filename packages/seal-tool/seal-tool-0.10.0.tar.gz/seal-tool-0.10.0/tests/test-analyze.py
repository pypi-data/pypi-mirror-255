from tests.util import compare_frames, compare_text
from seal.__main__ import main

# todo: split to multiple taskfiles & multiple tests w/ 1-2 asserts
def test_basic_rtm_max1d():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/basic-rtm-max1d.conf']

    main(cl)

    compare_frames('basic-rtm-max1d-a1.csv')
    compare_frames('basic-rtm-max1d-a2.csv')
    #compare_frames('basic-rtm-max1d-a2-add.csv') todo: add expected data
    compare_frames('basic-rtm-max1d-a3.csv')
    compare_frames('basic-rtm-max1d-a3-add.csv')
    compare_frames('basic-rtm-max1d-a4.csv')
    compare_frames('basic-rtm-max1d-a4-add.csv')
    compare_frames('basic-rtm-max1d-a5.csv')
    compare_frames('basic-rtm-max1d-a6.csv')
    compare_frames('basic-rtm-max1d-a6-add.csv')
    compare_frames('basic-rtm-max1d-a7.csv')

    compare_text('basic-rtm-max1d-a1-add.txt')


def test_basic_stm_max1d():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/basic-stm-max1d.conf']

    main(cl)

    compare_frames('basic-stm-max1d-a1.csv')
    compare_frames('basic-stm-max1d-a2.csv')
    #compare_frames('basic-stm-max1d-a2-add.csv') todo: add expected data
    compare_frames('basic-stm-max1d-a3.csv')
    compare_frames('basic-stm-max1d-a3-add.csv')
    compare_frames('basic-stm-max1d-a4.csv')
    compare_frames('basic-stm-max1d-a4-add.csv')
    compare_frames('basic-stm-max1d-a5.csv')
    compare_frames('basic-stm-max1d-a6.csv')
    compare_frames('basic-stm-max1d-a6-add.csv')
    compare_frames('basic-stm-max1d-a7.csv')

    compare_text('basic-stm-max1d-a1-add.txt')


def test_subgrids_os_diagonal():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/subgrids-os-diagonal.conf']

    main(cl)

    compare_frames('subgrids-os-diagonal-a1.csv')
    compare_frames('subgrids-os-diagonal-a2.csv')
    #compare_frames('subgrids-os-diagonal-a2-add.csv') todo: add expected data
    compare_frames('subgrids-os-diagonal-a3.csv')
    compare_frames('subgrids-os-diagonal-a3-add.csv')
    compare_frames('subgrids-os-diagonal-a4.csv')
    compare_frames('subgrids-os-diagonal-a4-add.csv')
    compare_frames('subgrids-os-diagonal-a5.csv')
    compare_frames('subgrids-os-diagonal-a6.csv')
    compare_frames('subgrids-os-diagonal-a6-add.csv')
    compare_frames('subgrids-os-diagonal-a7.csv')

    compare_text('subgrids-os-diagonal-a1-add.txt')


def test_jaccard_os_diagonal_1lvl():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/test-jaccard-os-diagonal-1lvl.conf']

    main(cl)

    compare_frames('test-jaccard-os-diagonal-1lvl-a7.csv')


def test_jaccard_rtm_max1d():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/basic-rtm-max1d-a7.conf']

    main(cl)

    compare_frames('basic-rtm-max1d-a7-a7.csv')


def test_jaccard_stm_max1d():
    cl = ['seal', 'analyze', '--taskfile', './tests/tasks/basic-stm-max1d-a7.conf']

    main(cl)

    compare_frames('basic-stm-max1d-a7-a7.csv')
