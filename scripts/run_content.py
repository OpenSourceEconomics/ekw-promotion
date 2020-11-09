#!/usr/bin/env python
"""This script compiles the content of the repository."""
import subprocess as sp
import argparse
import shutil
import glob
import os

from PyPDF2 import PdfFileMerger


def compile_material(task):

    os.chdir(os.environ["PROJECT_DIR"] + f"/{task}")

    [
        sp.check_call([cmd, "main"])
        for cmd in ["pdflatex", "biber", "pdflatex", "pdflatex"]
    ]

    os.chdir(os.environ["PROJECT_DIR"])


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Create material for Eckstein-Keane-Wolpin models")

    parser.add_argument(
        "-g", "--graphs", action="store_true", help="create and update graphs"
    )

    parser.add_argument("-s", "--slides", action="store_true", help="create slides")

    parser.add_argument("-p", "--paper", action="store_true", help="create paper")

    parser.add_argument("-f", "--full", action="store_true", help="create full content")

    parser.add_argument("-a", "--appendix", action="store_true", help="create appendix")

    args = parser.parse_args()

    if args.graphs or args.full:

        os.chdir(os.environ["PROJECT_DIR"] + "/replication")

        [os.remove(fname) for fname in glob.glob("../material/fig-*.png")]

        sp.check_call(["python", "run.py"])
        sp.check_call(["python", "kw_97_simulations.py"])

    if args.appendix or args.full:

        compile_material("appendix")

        shutil.copy("appendix/main.pdf", "ekw-appendix.pdf")

    if args.paper or args.full:

        compile_material("paper")

        shutil.copy("paper/main.pdf", "ekw-paper.pdf")

    if os.path.exists("ekw-paper.pdf") and os.path.exists("ekw-appendix.pdf"):
        pdf_merger = PdfFileMerger()
        file_handles = []

        for path in ["ekw-paper.pdf", "ekw-appendix.pdf"]:
            pdf_merger.append(path)
        with open("ekw-promotion.pdf", "wb") as fileobj:
            pdf_merger.write(fileobj)

    if args.slides or args.full:

        compile_material("slides")

        shutil.copy("slides/main.pdf", "ekw-slides.pdf")
