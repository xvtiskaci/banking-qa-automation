"""Offline checks for responsive banking navigation (no bank traffic)."""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def _source(path):
    return (ROOT / path).read_text(encoding='utf-8')


def test_mobile_navigation_uses_href_not_fragile_li_nesting():
    page = _source('pages/procreditbank_transfers_page.py')
    assert "//a[@href='/dashboard/transfers']" in page
    assert "/dashboard/transfers/domestic-payment" in page
    assert "normalize-space(.)='საქართველოში'" in page
    assert "//li[a[@href='/dashboard/transfers']]" not in page


def test_mobile_negative_transfer_ensures_correct_menu_visible():
    flow = _source(
        'steps/procreditbank_negative_transfer_steps.py'
    )

    assert "ensure_mobile_menu_open(section='transfers')" in flow
    assert 'transfers.open_mobile_domestic_transfer()' in flow
    assert "purpose='transfer'" in flow

    mobile_test = _source(
        'tests/test_procreditbank_mobile_negative_transfer.py'
    )

    assert '@pytest.mark.procredit_mobile' in mobile_test
    assert '@pytest.mark.livebank' in mobile_test

    conftest = _source('tests/conftest.py')

    assert 'PRO_CREDIT_NEGATIVE_SUBMIT' in conftest
    assert 'PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT' in conftest
    assert 'HEADLESS' in conftest


def test_mobile_width_set_from_marker():
    fixture = _source('tests/conftest.py')
    assert 'request.node.get_closest_marker("procredit_mobile")' in fixture
    assert '"width": 414' in fixture
    assert '"height": 896' in fixture


class _Item:
    def __init__(self, label, state, hidden=False):
        self.label, self.state, self.hidden = label, state, hidden

    def is_displayed(self):
        if self.hidden:
            return False
        return self.label == 'toggle' or self.state['expanded']

    def is_enabled(self):
        return True

    def click(self):
        self.state['clicks'].append(self.label)
        if self.label == 'toggle':
            self.state['expanded'] = True


class _Driver:
    def __init__(self, state):
        self.state = state

    def find_elements(self, by, locator):
        if locator == 'toggle':
            return [_Item('toggle', self.state, hidden=True),
                    _Item('toggle', self.state)]
        if locator == 'georgia':
            return [_Item('georgia', self.state, hidden=True),
                    _Item('georgia', self.state)]
        return []

    def execute_script(self, script, element):
        assert 'scrollIntoView' in script
        self.state['scrolled'].append(element.label)


def _build_page(state):
    """Compile actual Page methods with fake Selenium dependencies."""
    tree = ast.parse(_source('pages/procreditbank_transfers_page.py'))
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef)
               and x.name == 'ProcreditTransfersPage')
    methods = [x for x in cls.body if isinstance(x, ast.FunctionDef)
               and x.name in {'_visible_enabled', 'open_mobile_domestic_transfer'}]
    copy_class = ast.ClassDef(name='ProcreditTransfersPage', bases=[], keywords=[],
                              body=methods, decorator_list=[])
    fake_driver = _Driver(state)

    def wait_until(predicate, message=None):
        result = predicate(fake_driver)
        if not result:
            raise AssertionError(message)
        return result

    ns = {'staticmethod': staticmethod,
          'DriverManager': SimpleNamespace(get_driver=lambda: fake_driver),
          'DriverUtils': SimpleNamespace(wait_until=wait_until)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[copy_class], type_ignores=[])),
                 '<page-under-test>', 'exec'), ns)
    page = ns['ProcreditTransfersPage']()
    page._ProcreditTransfersPage__mobile_transfers_toggle = SimpleNamespace(by='xpath', locator='toggle')
    page._ProcreditTransfersPage__mobile_domestic_transfer = SimpleNamespace(by='xpath', locator='georgia')
    return page


def test_closed_dropdown_expands_then_opens_georgia():
    state = {'expanded': False, 'clicks': [], 'scrolled': []}
    _build_page(state).open_mobile_domestic_transfer()
    assert state['clicks'] == ['toggle', 'georgia']
    assert state['scrolled'] == ['toggle', 'georgia']


def test_open_dropdown_does_not_collapse():
    state = {'expanded': True, 'clicks': [], 'scrolled': []}
    _build_page(state).open_mobile_domestic_transfer()
    assert state['clicks'] == ['georgia']
    assert state['scrolled'] == ['georgia']


def test_hidden_duplicate_links_are_ignored():
    state = {'expanded': False, 'clicks': [], 'scrolled': []}
    _build_page(state).open_mobile_domestic_transfer()
    assert state['clicks'] == ['toggle', 'georgia']
