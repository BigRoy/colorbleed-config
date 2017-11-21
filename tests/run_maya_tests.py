"""Use Mayapy for testing

Usage:
    $ mayapy run_maya_tests.py

"""

if __name__ == "__main__":
    import sys
    import nose
    import logging
    import warnings

    from nose_exclude import NoseExclude

    # todo(roy): Ensure consistent tests with different maya settings
    # A new scene is currently based on your user preferences; if your
    # preferences are set to a wrong value (e.g. FPS is different) they could
    # influence whether a publish would pass or not
    # Skip pymel initializing all mel commands
    # os.environ["PYMEL_SKIP_MEL_INIT"] = "1"

    from maya import standalone
    standalone.initialize()

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    log = logging.getLogger()

    # Discard default Maya logging handler
    log.handlers[:] = []

    argv = sys.argv[:]
    argv.extend([

        # Sometimes, files from Windows accessed
        # from Linux cause the executable flag to be
        # set, and Nose has an aversion to these
        # per default.
        "--exe",

        "--verbose",
        # "--with-doctest",

        # "--with-coverage",
        # "--cover-html",
        # "--cover-tests",
        # "--cover-erase",
    ])

    nose.main(module="tests",
              argv=argv,
              addplugins=[NoseExclude()])
