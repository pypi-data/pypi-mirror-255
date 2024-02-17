# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest

from .test_helpers import TestHelperFunctions, TestURLfor
from .test_pagination import TestPagination
from .test_signals import SignalsTestCase
from .test_templates import TestLazyRendering, TestTemplateLoading


def suite():
    "Nereid Application test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests([
            unittest.TestLoader().loadTestsFromTestCase(TestTemplateLoading),
            unittest.TestLoader().loadTestsFromTestCase(TestLazyRendering),
            unittest.TestLoader().loadTestsFromTestCase(TestURLfor),
            unittest.TestLoader().loadTestsFromTestCase(TestHelperFunctions),
            unittest.TestLoader().loadTestsFromTestCase(SignalsTestCase),
            unittest.TestLoader().loadTestsFromTestCase(TestPagination),
    ])
    return test_suite
