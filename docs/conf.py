import os
import time
import sys
sys.path.insert(0, os.path.abspath("../apps/"))
sys.path.insert(0, os.path.abspath("../apps/compliance_evaluator"))

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'scanpydoc.elegant_typehints',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]


if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'ceosys'
author = 'Gregor Lichtner, Carlo Jurth, Thomas Bienert, Claudia Spies, Falk von Dincklage'
year = f'2020-{time.strftime("%Y")}'
copyright = '{0}, {1}'.format(year, author)
version = release = '0.1'

autosummary_generate = True  # Turn on sphinx.ext.autosummary
autodoc_mock_imports = ["dotenv", "config", "pint", "pandas", "fastapi"]

pygments_style = 'trac'
templates_path = ['_templates']
extlinks = {
    'issue': ('https://github.com/glichtner/ceosys/%s', '#'),
    'pr': ('https://github.com/glichtner/ceosys/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = True
napoleon_use_param = True

add_module_names = False

# workaround for https://github.com/sphinx-doc/sphinx/issues/7493
# see https://icb-scanpydoc.readthedocs-hosted.com/en/latest/scanpydoc.elegant_typehints.html
qualname_overrides = {
    "compliance_evaluator.cgr_compliance.evaluator.ComplianceEvaluator": "cgr_compliance.ComplianceEvaluator",
    "compliance_evaluator.cgr_compliance.quantity.Quantity": "cgr_compliance.Quantity",
    "compliance_evaluator.cgr_compliance.quantity.Medication": "cgr_compliance.Medication"
}
