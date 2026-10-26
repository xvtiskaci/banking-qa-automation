
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / 'pages'
STEPS = ROOT / 'steps'
BROWSER_TESTS = ROOT / 'tests'


def _tree(path):
    return ast.parse(path.read_text(encoding='utf-8'), filename=str(path))


def test_procredit_has_exactly_five_named_page_objects():
    names = {f.name for f in PAGES.glob('procredit*.py')}
    assert names == {
        'procreditbank_login_page.py',
        'procreditbank_dashboard_page.py',
        'procreditbank_accounts_page.py',
        'procreditbank_transfers_page.py',
        'procreditbank_domestic_payment_page.py',
    }


def test_browser_test_folder_contains_only_browser_scenarios():
    test_files = list(BROWSER_TESTS.glob('test_*.py'))
    assert len(test_files) == 6
    assert all('unit' not in f.name for f in test_files)
    for path in test_files:
        tree = _tree(path)
        assert any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == 'mark'
            and node.func.attr == 'site'
            for node in ast.walk(tree)
        ), f'{path.name} must mark its browser site'


def test_each_browser_test_method_invokes_exactly_one_steps_scenario():
    count = 0
    invoked = set()
    for path in BROWSER_TESTS.glob('test_*.py'):
        tree = _tree(path)
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name.startswith('Test')):
            for method in (n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')):
                count += 1
                assert len(method.body) == 1, (path.name, method.name, 'only one Steps call allowed')
                statement = method.body[0]
                assert isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
                target = statement.value.func
                assert isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                assert target.value.id.endswith('Steps'), (path.name, method.name)
                assert not statement.value.args and not statement.value.keywords
                invoked.add((target.value.id, target.attr))
    assert count == 6
    assert len(invoked) == 6, 'Each browser test must invoke its own unique scenario'


def test_every_steps_class_has_only_one_static_scenario_method():
    for path in STEPS.glob('*steps.py'):
        tree = _tree(path)
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
            assert len(methods) == 1, (path.name, cls.name)
            assert any(isinstance(d, ast.Name) and d.id == 'staticmethod'
                       for d in methods[0].decorator_list), (path.name, cls.name)
            assert not any(isinstance(n, ast.FunctionDef)
                           for n in ast.walk(methods[0]) if n is not methods[0]), (path.name, cls.name)


def test_no_obsolete_procredit_page_imports():
    forbidden = ('pages.procredit_dashboard_page', 'pages.procredit_accounts_page',
                 'pages.procredit_transfers_page', 'pages.procredit_domestic_transfer_page',
                 'steps.procredit_insufficient_funds_steps', 'pages.procreditbank_otp_page')
    for folder in ('pages', 'steps', 'tests'):
        for path in (ROOT / folder).glob('*.py'):
            content = path.read_text(encoding='utf-8')
            assert not any(token in content for token in forbidden), path
