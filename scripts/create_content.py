#!/usr/bin/env python
"""This script compiles the content of the repository."""
import subprocess as sp
import argparse
import shutil
import glob
import os


def compile_material(task):

    os.chdir(os.environ["PROJECT_DIR"] + f"/{task}")

    [sp.check_call([cmd, "main"]) for cmd in ["pdflatex", "bibtex", "pdflatex", "pdflatex"]]

    os.chdir(os.environ["PROJECT_DIR"])


if __name__ == '__main__':

    parser = argparse.ArgumentParser("Create material for Eckstein-Keane-Wolpin models")

    parser.add_argument("-f", "--figures", action="store_true", help="create and update figures")

    parser.add_argument("-p", "--presentation", action="store_true", help="create presentation")

    parser.add_argument("-d", "--document", action="store_true", help="create document")

    parser.add_argument("-a", "--all", action="store_true", help="create all content")

    args = parser.parse_args()

    if args.figures or args.all:

        os.chdir(os.environ["PROJECT_DIR"] + "/replication")

        [os.remove(fname) for fname in glob.glob("../material/fig-*.png")]

        sp.check_call(["python", "run.py"])

        [shutil.copy(fname, f"../material/{fname}") for fname in glob.glob("*.png")]

    if args.document or args.all:

        compile_material("handout")

    if args.presentation or args.all:

        compile_material("presentation")
