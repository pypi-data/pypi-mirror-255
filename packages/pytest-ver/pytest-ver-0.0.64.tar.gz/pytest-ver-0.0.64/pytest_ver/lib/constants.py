# -------------------
## Holds various constants
class Constants:
    ## the module version
    version = None

    ## trace document file name
    trace_fname = 'trace'

    ## summary document file name
    summary_fname = 'summary'

    ## test report document file name - with results
    tp_report_fname = 'test_report'

    ## test protocol document file name - no results
    tp_protocol_fname = 'test_protocol'

    # -------------------
    ## initialize the version string
    #
    # @return None
    @staticmethod
    def init():
        import os
        import json

        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'version.json')
        with open(path, 'r', encoding='utf-8') as fp:
            j = json.load(fp)
            Constants.version = j['version']
