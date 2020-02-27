#!/usr/bin/env python
"""This script compiles the handout."""
import subprocess as sp
import argparse
import shutil
import glob
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser("Create material for Eckstein-Keane-Wolpin models")

    parser.add_argument("-d", "--document", action="store_true", help="create document")

    parser.add_argument("-f", "--figures", action="store_true", help="create and update figures")

    parser.add_argument("-a", "--all", action="store_true", help="create all content")

    args = parser.parse_args()

    if args.figures or args.all:

        os.chdir(os.environ["PROJECT_DIR"] + "/figures")

        [os.remove(fname) for fname in glob.glob("../handout/material/*.png")]

        sp.check_call(["python", "figures.py"])

        [shutil.copy(fname, f"../handout/material/{fname}") for fname in glob.glob("*.png")]

    if args.document or args.all:

        os.chdir(os.environ["PROJECT_DIR"] + "/handout")

        [sp.check_call([cmd, "main"]) for cmd in ["pdflatex", "bibtex", "pdflatex", "pdflatex"]]

        shutil.move("main.pdf", "../ekw-handout.pdf")

        sp.check_call(["git", "clean", "-xdf"])
