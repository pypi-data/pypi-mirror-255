# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_tree_sitter_epics']

package_data = \
{'': ['*'],
 'py_tree_sitter_epics': ['tree-sitter-epics/*',
                          'tree-sitter-epics/common/*',
                          'tree-sitter-epics/epics-cmd/*',
                          'tree-sitter-epics/epics-cmd/bindings/node/*',
                          'tree-sitter-epics/epics-cmd/bindings/rust/*',
                          'tree-sitter-epics/epics-cmd/queries/*',
                          'tree-sitter-epics/epics-cmd/src/*',
                          'tree-sitter-epics/epics-cmd/src/tree_sitter/*',
                          'tree-sitter-epics/epics-cmd/test/corpus/*',
                          'tree-sitter-epics/epics-db/*',
                          'tree-sitter-epics/epics-db/bindings/node/*',
                          'tree-sitter-epics/epics-db/bindings/rust/*',
                          'tree-sitter-epics/epics-db/queries/*',
                          'tree-sitter-epics/epics-db/src/*',
                          'tree-sitter-epics/epics-db/src/tree_sitter/*',
                          'tree-sitter-epics/epics-db/test/corpus/*',
                          'tree-sitter-epics/epics-msi-substitution/*',
                          'tree-sitter-epics/epics-msi-substitution/bindings/node/*',
                          'tree-sitter-epics/epics-msi-substitution/bindings/rust/*',
                          'tree-sitter-epics/epics-msi-substitution/queries/*',
                          'tree-sitter-epics/epics-msi-substitution/src/*',
                          'tree-sitter-epics/epics-msi-substitution/src/tree_sitter/*',
                          'tree-sitter-epics/epics-msi-substitution/test/corpus/*',
                          'tree-sitter-epics/epics-msi-template/*',
                          'tree-sitter-epics/epics-msi-template/bindings/node/*',
                          'tree-sitter-epics/epics-msi-template/bindings/rust/*',
                          'tree-sitter-epics/epics-msi-template/queries/*',
                          'tree-sitter-epics/epics-msi-template/src/*',
                          'tree-sitter-epics/epics-msi-template/src/tree_sitter/*',
                          'tree-sitter-epics/epics-msi-template/test/corpus/*',
                          'tree-sitter-epics/snl/*',
                          'tree-sitter-epics/snl/bindings/node/*',
                          'tree-sitter-epics/snl/bindings/rust/*',
                          'tree-sitter-epics/snl/queries/*',
                          'tree-sitter-epics/snl/src/*',
                          'tree-sitter-epics/snl/src/tree_sitter/*',
                          'tree-sitter-epics/snl/test/corpus/*',
                          'tree-sitter-epics/streamdevice-proto/*',
                          'tree-sitter-epics/streamdevice-proto/bindings/node/*',
                          'tree-sitter-epics/streamdevice-proto/bindings/rust/*',
                          'tree-sitter-epics/streamdevice-proto/queries/*',
                          'tree-sitter-epics/streamdevice-proto/src/*',
                          'tree-sitter-epics/streamdevice-proto/src/tree_sitter/*',
                          'tree-sitter-epics/streamdevice-proto/test/corpus/*']}

setup_kwargs = {
    'name': 'py-tree-sitter-epics',
    'version': '0.1.6',
    'description': 'Facilitate tree-sitter-epics parsing in python',
    'long_description': '# PY-TREE-SITTER-EPICS\n\nBased on [Tree sitter ](https://github.com/tree-sitter/tree-sitter), [tree-sitter-epics](https://github.com/epics-extensions/tree-sitter-epics) and [Py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter), this module is used to serialize any [EPICS](https://epics-controls.org/) files into a Python object usable in a script.\n\n*⚠️ For now it is only developped for EPICS CA database but it will support more files in the future.*\n\n## Installation\n\nThe module is available on [Pypi](https://github.com/tree-sitter/tree-sitter). This package currently only works with Python \\>3.10. The library dependencis is tree-sitter-epics\n\n``` console\npip3 install py-tree-sitter-epics\n```\n\nYou may need to use this line\n\n``` console\npip3 install py-tree-sitter-epics --break-system-packages\n```\n\n## Using\n\nThis example show how to use the module. It is parsing a file building a python object containing all the fields, infos and links to finally displaying all those infos.\n\n``` python\nfrom py_tree_sitter_epics import epicsdb\n\nwith Path.open("/tmp/myExample.db") as file:\n        code = file.read()\n#build the parser\ndb_parser = epicsdb.DbParser()\n#parse the code\ndb_parser.parse(code)\n#build record list from the parser\nrecord_list = db_parser.build_records_list()\nfor record in reccord_list:\n    #print a complete result\n    record.print_to_text()\n```\n',
    'author': 'Alexis Gaget',
    'author_email': 'alexis.gaget@cea.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
