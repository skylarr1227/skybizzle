from seplib.tests.utils.strings import random_string
from seplib.utils import Result


class TestResult(object):
    def test_result_defaults(self):
        s = random_string()
        result = Result(success=True, value=s)
        assert result.success is True
        assert result.value == s
        assert result.error is None

        s2 = random_string()
        error = random_string()
        result2 = Result(success=False, value=s2, error=error)

        assert result2.success is False
        assert result2.error == error
        assert result2.value == s2
