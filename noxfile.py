# type: ignore

import nox


@nox.session(
    venv_backend="uv",
    python=["3.10", "3.11", "3.12", "3.13"],
)
def tests(session: nox.Session) -> None:
    """Run the unit and regular tests."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--frozen",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest")
