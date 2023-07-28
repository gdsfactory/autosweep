TEST_CLASSES = {}


def register_test(test):
    TEST_CLASSES[test.__name__] = test