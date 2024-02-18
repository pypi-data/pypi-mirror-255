import os
import json
import logging
import unittest
import shutil
from pathlib import Path, PosixPath
from latex2readme import Tex2Readme
from latex2readme import main_logger

test_logger = logging.getLogger("Testing")
formatter = logging.Formatter("%(name)s [%(levelname)s] - %(message)s")
stream = logging.StreamHandler()
stream.setFormatter(formatter)
test_logger.addHandler(stream)


class TestTex2Readme(unittest.TestCase):

    main_logger.setLevel(logging.ERROR)
    test_logger.setLevel(logging.INFO)

    t2r = None

    @classmethod
    def setUp(cls):
        cls.t2r = Tex2Readme()
        cls.t2r.dir = Path(os.path.dirname(__file__))
        cls.t2r.depth = 2

    def test_get_toc_success(self):
        with open(self.t2r.dir / "toc.json", "w") as toc:
            json.dump(
                {"0": {"name": "test", "desc": "test file description"}},
                indent=4,
                fp=toc,
            )
        self.t2r.get_toc(self.t2r.dir)
        self.assertEqual(self.t2r.toc["0"]["name"], "test")
        os.remove(self.t2r.dir / "toc.json")
        test_logger.info("TOC file loaded [PASS]")

    def test_get_toc_fail(self):
        self.t2r.get_toc(self.t2r.dir)
        self.assertEqual(self.t2r.toc, None)
        test_logger.info("TOC file not found [PASS]")

    def test_find_tex_files_success(self):
        with open(self.t2r.dir / "temp.tex", "w+") as tx:
            tx.write("temp")
        os.mkdir(self.t2r.dir / "nested")
        with open(self.t2r.dir / "nested/temp.tex", "w+") as tx:
            tx.write("temp")
        self.t2r.find_tex_files(self.t2r.dir)
        self.assertTrue("temp.tex" in str(list(self.t2r.tex_pdf_pairs.keys())[0]))
        os.remove(self.t2r.dir / "temp.tex")
        shutil.rmtree(self.t2r.dir / "nested")
        test_logger.info("Search for nested dir *.tex files [PASS]")

    def test_generate_missing_pdfs(self):
        with open(self.t2r.dir / "temp.tex", "w+") as tx:
            tx.write(testing_tex_body)

        self.t2r.tex_pdf_pairs[
            PosixPath(self.t2r.dir / "temp.tex")
        ] = PosixPath(self.t2r.dir / "temp.tex")
        self.t2r.generate_missing_pdfs(self.t2r.dir)
        self.assertTrue(os.path.isfile(self.t2r.dir / "temp.pdf"))
        test_logger.info("Generated missing PDFs [PASS]")
        self.t2r.remove_compilation_files(self.t2r.dir)
        os.remove("temp.tex")
        os.remove("temp.pdf")
        test_logger.info("Removed compilation files [PASS]")

    # noinspection DuplicatedCode
    def test__generate_images(self):
        with open(self.t2r.dir / "temp.tex", "w+") as tx:
            tx.write(testing_tex_body)
        self.t2r.tex_pdf_pairs[
            PosixPath(self.t2r.dir / "temp.tex")
        ] = PosixPath(self.t2r.dir / "temp.tex")
        self.t2r.generate_missing_pdfs(self.t2r.dir)
        self.t2r.remove_compilation_files(self.t2r.dir)
        self.t2r.generate_images(self.t2r.dir)
        self.assertTrue(os.path.isfile(self.t2r.dir / "img/temp_0.png"))
        shutil.rmtree("img")
        test_logger.info("Generated images sets from PDFs [PASS]")

    # noinspection DuplicatedCode
    def test__insert_image(self):
        with open(self.t2r.dir / "temp.tex", "w+") as tx:
            tx.write(testing_tex_body)
        self.t2r.tex_pdf_pairs[
            PosixPath(self.t2r.dir / "temp.tex")
        ] = PosixPath(self.t2r.dir / "temp.tex")
        self.t2r.generate_missing_pdfs(self.t2r.dir)
        self.t2r.remove_compilation_files(self.t2r.dir)
        self.t2r.generate_images(self.t2r.dir)
        self.t2r.insert_images(self.t2r.dir)
        shutil.rmtree("img")
        os.remove("temp.tex")
        os.remove("temp.pdf")
        os.remove("README.md")
        test_logger.info("Inserted image sets to README.md [PASS]")

    def test__insert_readme(self):
        self.t2r.toc = {
            "0": {"name": "testing file name", "desc": "some random description"}
        }
        with open(self.t2r.dir / "README.md", "w"):
            self.t2r.insert_toc(self.t2r.dir)
        with open(self.t2r.dir / "README.md", "r") as rdm:
            txt = rdm.read()
            self.assertTrue("testing file name" in txt)
        os.remove(self.t2r.dir / "README.md")
        test_logger.info("Inserted TOC to README.md [PASS]")

    @classmethod
    def tearDown(cls):
        pass


testing_tex_body = r"""\documentclass[a5paper]{article}
\usepackage{geometry}
\usepackage[utf8]{inputenc}
\setlength\parindent{0pt}
\geometry{a5paper}
\begin{document}
\begin{sloppypar}
\section*{Test Section}
Random text

\bigskip
Some math:

\[
\frac{a}{b} = c
\]

\end{sloppypar}
\end{document}
"""


if __name__ == "__main__":
    unittest.main(verbosity=0)
