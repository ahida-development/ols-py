def pytest_addoption(parser):
    parser.addoption(
        "--ols4",
        action="store_true",
        default=False,
        help="Use the ols4 EBI instance when testing requests",
    )
