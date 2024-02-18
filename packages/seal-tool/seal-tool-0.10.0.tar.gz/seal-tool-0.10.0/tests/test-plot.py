from seal.__main__ import main

def test_basic_rtm_max1d():
    cl = ['seal', 'plot', '--taskfile', './tests/tasks/basic-rtm-max1d.conf']

    main(cl)

    # just check that things get plotted for now