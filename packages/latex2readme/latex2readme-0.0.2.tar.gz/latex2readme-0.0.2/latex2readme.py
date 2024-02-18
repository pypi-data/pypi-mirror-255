# Copyright 2024 Leon Hergešić Adamović
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import shutil
import fnmatch
import logging
import argparse
from pathlib import Path
from natsort import natsorted
from pdf2image import convert_from_path

main_logger = logging.getLogger("Tex2Readme")
formatter = logging.Formatter("%(name)s %(levelname)-8s %(message)s")
stream = logging.StreamHandler()
stream.setFormatter(formatter)
main_logger.addHandler(stream)

main_logger.setLevel(logging.INFO)


class Tex2Readme:
    """
    If toc.json file is not provided, pdfs are
    added without defined order.

    toc.json example:
    {
        "0": {
            "name": "<filename>",
            "desc": "<description>"
        }
    }

    "name" fields in toc.json must match filenames they
    represent exactly.
    """

    def __init__(self, depth=4):
        self.depth = int(depth)
        self.img_dir = Path("img")
        self.dir = Path(os.getcwd())
        self.tex_pdf_pairs = dict()
        self.dir_list = list()
        self.toc = None

    def get_child_dirs(self):
        for r, d, f in os.walk(self.dir):
            current_depth = r.count(os.path.sep) - str(self.dir).count(os.path.sep)
            if current_depth <= self.depth:
                if str(self.img_dir) not in str(r):
                    if fnmatch.filter(os.listdir(Path(r)), "*.tex"):
                        self.dir_list.append(Path(r))

    @staticmethod
    def _dir_has_tex(directory: str) -> bool:
        for filename in os.listdir(directory):
            if filename.endswith(".tex"):
                return True
        return False

    def _relpath(self, filepath) -> str:
        return os.path.relpath(filepath, self.dir)

    def log_dir(self, directory: str):
        print("")
        main_logger.info("Editing: ./" + str(self._relpath(directory)))

    def get_toc(self, directory: Path):
        try:
            with open(directory / "toc.json") as toc:
                self.toc = json.load(toc)
                main_logger.info(f"toc.json exists")
        except FileNotFoundError:
            main_logger.warning("No 'toc.json' found")

    def find_tex_files(self, directory: Path):
        for file in fnmatch.filter(os.listdir(directory), "*.tex"):
            full_path = Path(directory / file)
            if os.path.exists(pdf_path := str(full_path)[:-3] + "pdf"):
                main_logger.info(
                    f"Found: {self._relpath(full_path)} with corresponding .pdf"
                )
                self.tex_pdf_pairs[os.path.join(directory, full_path)] = pdf_path
            else:
                main_logger.info(
                    f"Found: {self._relpath(full_path)} without corresponding .pdf"
                )
                self.tex_pdf_pairs[os.path.join(directory, full_path)] = None

    def generate_missing_pdfs(self, directory: Path):
        for tex_path, pdf_path in self.tex_pdf_pairs.items():
            if pdf_path is None:
                if str(directory) in tex_path:
                    main_logger.info(f"Generating pdf from: {self._relpath(tex_path)}")
                    if main_logger.level > logging.DEBUG:
                        os.system(
                            f"pdflatex"
                            f" --output-directory={os.path.dirname(tex_path)}"
                            f" {tex_path}"
                            f" > /dev/null 2>&1"
                        )
                    else:
                        os.system(
                            f"pdflatex"
                            f" --output-directory={os.path.dirname(tex_path)}"
                            f" {tex_path}"
                        )
                    self.tex_pdf_pairs[tex_path] = str(tex_path)[:-3] + "pdf"

                else:
                    main_logger.info(f"Skipping: {pdf_path}")

    @staticmethod
    def remove_compilation_files(directory: Path):
        compilation_files = ["*.log", "*.aux", "*.fdb_latexmk", "*.fls", "*.synctex.gz"]
        for ext in compilation_files:
            for filepath in Path(directory).rglob(ext):
                main_logger.info(f"Removing: {filepath}")
                os.remove(filepath)

    def reset_img_dir(self, directory: Path):
        try:
            shutil.rmtree(directory / self.img_dir)
        except FileNotFoundError:
            main_logger.info(f"{directory / self.img_dir} dir does not exist")
        os.mkdir(directory / self.img_dir)

    def generate_images(self, directory: Path):
        for pdf_path in self.tex_pdf_pairs.values():
            if str(directory) in pdf_path:
                pdf_images = convert_from_path(pdf_path)
                img_name = Path(pdf_path).stem
                for idx in range(len(pdf_images)):
                    pdf_images[idx].save(
                        directory / self.img_dir / str(img_name + "_" + str(idx) + ".png"),
                        "PNG",
                    )
                    main_logger.info(f"Generated: {img_name}_{str(idx)}.png")

    def _get_image_set(self, filename, directory: Path):
        return [d for d in os.listdir(directory / self.img_dir) if filename in d]

    @staticmethod
    def reset_md_file(directory: Path):
        with open(directory / "README.md", "w"):
            pass
        main_logger.info(f"Cleared: {str(directory)}/README.md")

    def insert_images(self, directory: Path):
        for pdf in self.tex_pdf_pairs.values():
            if str(directory) in pdf:
                pdf_filename = Path(pdf).stem
                main_logger.info(f"Seeking images for doc: {pdf_filename}")
                images = natsorted(self._get_image_set(pdf_filename, directory=directory))
                main_logger.info(f"Found image set: {images}")

                with open(directory / "README.md", "a") as rdm:
                    rdm.write(f"\n## {pdf_filename}\n")
                    for i, img in enumerate(images):
                        rdm.write(f"![{pdf_filename}]({self.img_dir}/{img})\n")
                        main_logger.info(f"Inserted:  {pdf_filename}_{i}.png")

    def insert_toc(self, directory: Path):
        if self.toc is not None:
            toc = list()
            for i, script in self.toc.items():
                script_name = str(script["name"])
                script_desc = str(script["desc"])
                toc.append(f"* [{script_name}](#{script_name}) {script_desc}\n")

            with open(directory / "README.md", "r+") as rdm:
                lines = rdm.readlines()
                rdm.seek(0)
                rdm.writelines(toc)
                rdm.writelines(lines)

            main_logger.info(f"Inserted toc to: {str(directory) + '/README.md'}")

    def generate(self):
        self.get_child_dirs()
        for directory in self.dir_list:
            self.log_dir(directory)
            self.find_tex_files(directory)
            self.get_toc(directory)
            self.generate_missing_pdfs(directory)
            self.remove_compilation_files(directory)
            self.reset_img_dir(directory)
            self.generate_images(directory)
            self.reset_md_file(directory)
            self.insert_images(directory)
            self.insert_toc(directory)


def run():
    parser = argparse.ArgumentParser(
        description="Convert .tex docs to pdfs inserted into README.md"
    )
    parser.add_argument(
        "--depth",
        default=2,
        help="number of subdirectories that script looks for .tex docs (default: 2)",
    )
    args = parser.parse_args()

    t2r = Tex2Readme(depth=args.depth)
    t2r.generate()


if __name__ == "__main__":
    run()
