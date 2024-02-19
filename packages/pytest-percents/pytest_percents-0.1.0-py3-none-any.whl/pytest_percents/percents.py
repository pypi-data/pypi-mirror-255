def pytest_runtest_setup(item):
    print(f"Setting up test: {item.name}")
