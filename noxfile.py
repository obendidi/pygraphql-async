import nox


@nox.session(python=["3.8", "3.7", "3.6"])
def tests(session):
    session.run("poetry", "install", "-E", "trio", external=True)
    session.run("poetry", "run", "pytest")
