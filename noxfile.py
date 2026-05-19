import nox

# Use uv by default for faster environment creation
nox.options.default_venv_backend = "uv"
nox.options.sessions = ["tests", "lint"]

@nox.session(python=["3.12", "3.13", "3.14"])
def tests(session):
    """Run the test suite across multiple Python versions."""
    # Install the current package and its dependencies using uv
    session.install(".")
    # Install test dependencies
    session.install("pytest", "pytest-cov", "matplotlib")
    
    # Run pytest
    # posargs allows passing extra arguments to pytest, e.g., nox -s tests -- -v
    session.run("pytest", *session.posargs)

@nox.session(python="3.12")
def lint(session):
    """Run static analysis and formatting checks."""
    session.install("black", "mypy", "pandas-stubs")
    session.install(".")
    session.run("black", "--check", "src", "tests")
    session.run("mypy", "src")

@nox.session(python="3.14")
def docs(session):
    """Build the documentation."""
    session.install(".[dev]") # Install with dev extras if defined, or just dependencies
    session.install("mkdocs", "mkdocs-material", "mkdocstrings[python]")
    session.run("mkdocs", "build")
