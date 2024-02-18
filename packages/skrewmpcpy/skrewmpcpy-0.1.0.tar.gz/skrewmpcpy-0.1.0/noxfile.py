# mypy: ignore-errors
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()

nox.options.sessions = ["ruff", "tests"]


@nox.session(tags=["check"])
def ruff(session) -> None:
    """Check code for linter warnings and formatting issues."""
    check_files = ["src", "tests"]
    session.install("ruff ~= 0.1.9")
    session.run("ruff", "check", "--exclude", "_version.py", *check_files)


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".[test]")
    session.run("pytest", *session.posargs)


@nox.session
def coverage(session: nox.Session) -> None:
    session.install(".[test]")
    session.run("coverage", "run", "-m", "pytest", *session.posargs)


@nox.session(reuse_venv=True)
def docs(session: nox.Session) -> None:
    """
    Build the docs. Pass "--serve" to serve. Pass "-b linkcheck" to check links.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="Serve after building")
    parser.add_argument(
        "-b", dest="builder", default="html", help="Build target (default: html)"
    )
    args, posargs = parser.parse_known_args(session.posargs)

    if args.builder != "html" and args.serve:
        session.error("Must not specify non-HTML builder with --serve")

    extra_installs = ["sphinx-autobuild"] if args.serve else []

    session.install("-e.[docs]", *extra_installs)
    session.chdir("docs")

    if args.builder == "linkcheck":
        session.run(
            "sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck", *posargs
        )
        return

    shared_args = (
        "-n",  # nitpicky mode
        "-T",  # full tracebacks
        f"-b={args.builder}",
        ".",
        f"_build/{args.builder}",
        *posargs,
    )

    if args.serve:
        session.run("sphinx-autobuild", *shared_args)
    else:
        session.run("sphinx-build", "--keep-going", *shared_args)


@nox.session
def build_api_docs(session: nox.Session) -> None:
    """
    Build (regenerate) API docs.
    """

    session.install("sphinx")
    session.chdir("docs")
    session.run(
        "sphinx-apidoc",
        "-o",
        "api/",
        "--module-first",
        "--no-toc",
        "--force",
        "../src/skrewmpcpy",
    )


@nox.session
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    build_path = DIR.joinpath("build")
    if build_path.exists():
        shutil.rmtree(build_path)

    session.install("build")
    session.run("python", "-m", "build")


@nox.session
def release(session: nox.Session) -> None:
    """
    Kicks off an automated release process by creating and pushing a new tag.

    Invokes bump2version with the posarg setting the version.

    Usage:
    $ nox -s release -- [major|minor|patch]
    """
    parser = argparse.ArgumentParser(description="Release a semver version.")
    parser.add_argument(
        "version",
        type=str,
        nargs=1,
        help="The type of semver release to make.",
        choices={"major", "minor", "patch"},
    )
    args: argparse.Namespace = parser.parse_args(args=session.posargs)
    version: str = args.version.pop()

    # If we get here, we should be good to go
    # Let's do a final check for safety
    confirm = input(
        f"You are about to bump the {version!r} version. Are you sure? [y/n]: "
    )

    # Abort on anything other than 'y'
    if confirm.lower().strip() != "y":
        session.error(f"You said no when prompted to bump the {version!r} version.")

    session.install("bump2version")

    session.log(f"Bumping the {version!r} version")
    session.run("bump2version", version)

    session.log("Pushing the new tag")
    session.run("git", "push", external=True)
    session.run("git", "push", "--tags", external=True)
