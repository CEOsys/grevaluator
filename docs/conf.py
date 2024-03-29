import os
import time
import sys

sys.path.insert(0, os.path.abspath("../apps/"))
sys.path.insert(0, os.path.abspath("../apps/adherence_evaluator"))

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]


if os.getenv("SPELLCHECK"):
    extensions += ("sphinxcontrib.spelling",)
    spelling_show_suggestions = True
    spelling_lang = "en_US"

source_suffix = ".rst"
master_doc = "index"
project = "ceosys"
author = (
    "Gregor Lichtner, Carlo Jurth, Thomas Bienert, Claudia Spies, Falk von Dincklage"
)
year = f'2020-{time.strftime("%Y")}'
copyright = "{0}, {1}".format(year, author)
version = release = "0.1"

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autodoc_mock_imports = ["dotenv", "config"]

pygments_style = "trac"
templates_path = ["_templates"]
extlinks = {
    "issue": ("https://github.com/glichtner/ceosys/%s", "#"),
    "pr": ("https://github.com/glichtner/ceosys/pull/%s", "PR #"),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = "sphinx_rtd_theme"

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = "%s-%s" % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = True
napoleon_use_param = True

add_module_names = False

# Mocking required environment variables
os.environ["GUIDELINE_SERVER"] = "https://guideline-server.mock"
os.environ["PATIENTDATA_SERVER"] = "https://patientdata-server.mock"
os.environ["CEOSYS_DATA_PATH"] = "/dev/null"
os.environ[
    "CEOSYS_BASE_PATH"
] = ".."  # TODO: pass mapping table to evaluator in order to use any value here
os.environ["MAGICAPP_USE"] = "0"
os.environ["MAGICAPP_EMAIL"] = "user@example.com"
os.environ["MAGICAPP_PASSWORD"] = "password"
os.environ["MAGICAPP_SERVER"] = "https://magicapp.mock"
