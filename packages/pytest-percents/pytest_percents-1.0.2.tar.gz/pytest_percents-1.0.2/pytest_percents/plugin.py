def pytest_runtest_setup(item):
    with open("text.py", "w") as f:
        f.write(f"Setting up test: {item.name}")
