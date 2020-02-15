#!/usr/bin/env python
"""This script compiles the handout."""
import subprocess as sp
import shutil
import os

if __name__ == '__main__':

    [os.system(type_ + " main") for type_ in ["pdflatex", "bibtex", "pdflatex", "pdflatex"]]

    shutil.move("main.pdf", "handout-eckstein-keane-wolpin.pdf")

    sp.check_call(["git", "clean", "-xdf"])
