from tools.xplat_utils import Utils


# --------------------
## create the output directory
#
# @return the full path to the outdir
def create_outdir():
    return Utils.create_outdir()


# --------------------
## return the module name for this given arg
#
# @param var   the
# @return the cfg variable value or an error message
def get_cfg(var):
    # if var is invalid, AttributeError is thrown
    return Utils.get_cfg(var)


# --------------------
## return the pytest options for coverage
#
# @return the module name or an error message
def cov_opts():
    return Utils.cov_opts()


# --------------------
## set the version string in the module's version.json file
# and create the build_info file
#
# @return the version string and the long version of it
def gen_files(verbose):
    Utils.set_params(verbose)
    Utils.gen_files()


# --------------------
def do_clean(verbose):
    Utils.set_params(verbose)
    Utils.do_clean()


# --------------------
def do_check(verbose):
    Utils.set_params(verbose)
    Utils.do_check()


# --------------------
def do_lint(verbose):
    Utils.set_params(verbose)
    Utils.do_lint()


# --------------------
def do_doc(verbose):
    Utils.set_params(verbose)
    Utils.do_doc()


# --------------------
def do_publish(verbose):
    Utils.set_params(verbose)
    Utils.do_publish()


# --------------------
def do_coverage(verbose):
    Utils.set_params(verbose)
    Utils.do_coverage()


def do_post_ver(verbose):
    Utils.set_params(verbose)
    Utils.do_post_ver()
