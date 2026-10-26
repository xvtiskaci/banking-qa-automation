
from selenium.common.exceptions import NoSuchElementException
from managers.DriverManager import DriverManager


class ElementFinder:
    _SCRIPT = r"""
        const [strategy, locator, all] = arguments;
        const matches = [];
        const seen = new Set();
        const add = el => {
            if (el && !seen.has(el)) { seen.add(el); matches.push(el); }
        };
        function search(root) {
            let nodes = [];
            if (strategy === 'css selector') {
                nodes = Array.from(root.querySelectorAll(locator));
            } else if (strategy === 'id') {
                nodes = Array.from(root.querySelectorAll('#' + CSS.escape(locator)));
            } else if (strategy === 'name') {
                nodes = Array.from(root.querySelectorAll('[name="' + CSS.escape(locator) + '"]'));
            } else if (strategy === 'class name') {
                nodes = Array.from(root.querySelectorAll('.' + CSS.escape(locator)));
            } else if (strategy === 'tag name') {
                nodes = Array.from(root.querySelectorAll(locator));
            } else if (strategy === 'xpath') {
                // Evaluate on a document or element, never a ShadowRoot fragment.
                const contexts = root.nodeType === 11
                    ? Array.from(root.children) : [root];
                for (const context of contexts) {
                    let expression = locator;
                    if (root.nodeType === 11 && expression.startsWith('//'))
                        expression = '.' + expression;
                    try {
                        const snapshot = document.evaluate(
                            expression, context, null,
                            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                        for (let i = 0; i < snapshot.snapshotLength; i++)
                            nodes.push(snapshot.snapshotItem(i));
                    } catch (err) { throw err; }
                    // Relative .// XPath omits context itself; check it as well.
                    if (root.nodeType === 11 && expression.startsWith('.//')) {
                        const selfExpression = 'self::' + expression.slice(3);
                        const own = document.evaluate(selfExpression, context, null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        if (own) nodes.push(own);
                    }
                }
            } else if (strategy === 'link text' || strategy === 'partial link text') {
                nodes = Array.from(root.querySelectorAll('a')).filter(a =>
                    strategy === 'link text' ? a.textContent.trim() === locator
                                             : a.textContent.includes(locator));
            } else { throw new Error('Unsupported locator strategy: ' + strategy); }
            nodes.forEach(add);
            for (const node of root.querySelectorAll('*')) {
                if (node.shadowRoot) search(node.shadowRoot);
            }
        }
        search(document);
        return all ? matches : (matches[0] || null);
    """

    @staticmethod
    def find_elements(by, locator):
        driver = DriverManager.get_driver()
        return driver.execute_script(ElementFinder._SCRIPT, by, locator, True)

    @staticmethod
    def find_element(by, locator):
        driver = DriverManager.get_driver()
        try:
            return driver.find_element(by, locator)
        except NoSuchElementException:
            found = driver.execute_script(ElementFinder._SCRIPT, by, locator, False)
            if found is None:
                raise NoSuchElementException(
                    f'Element not found in document or open shadow roots: {by}={locator}')
            return found
