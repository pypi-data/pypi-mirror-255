import os

import pytest

from seeq import spy


def get_example_export_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Documentation',
                                         'Support Files', 'Example Export.zip'))


def get_workbook_template_tests_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), 'Workbook Template Tests.zip'))


def get_report_and_dashboard_templates_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Documentation',
                                         'Support Files', 'Report and Dashboard Templates.zip'))


def get_workbook_templates_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Documentation',
                                         'Support Files', 'Workbook Templates.zip'))


def load_example_export():
    return spy.workbooks.load(get_example_export_path())


@pytest.mark.system
def test_load_folder():
    workbooks = load_example_export()
    assert len(workbooks) == 2


@pytest.mark.system
def test_load_zipfile():
    workbooks = spy.workbooks.load(get_example_export_path())
    assert len(workbooks) == 2
