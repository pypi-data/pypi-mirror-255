class TestHello:
    def test_hello(self):
        from inksplash import chameleon

        styled = chameleon.bg_black(chameleon.italic("Hello"))
        assert isinstance(styled, str)
