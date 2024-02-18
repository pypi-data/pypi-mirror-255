#!/usr/bin/python3

import os
from setuptools import setup, find_packages, Extension

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
# https://levelup.gitconnected.com/how-to-deploy-a-cython-package-to-pypi-8217a6581f09
# https://pypi.org/project/cython-package-example/
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


extensions = [
    Extension("wrapper.test", ["src/wrapper/test.pyx"]),
    Extension("wrapper.core.test2", ["src/wrapper/core/test2.pyx"]),
    Extension("wrapper.Process", ["src/wrapper/Process.pyx"]),
    Extension("wrapper.core.DocumentSearch", ["src/wrapper/core/DocumentSearch.pyx"]),
    Extension("wrapper.core.DocumentSearchTD", ["src/wrapper/core/DocumentSearchTD.pyx"]),
    Extension("wrapper.core.DocumentSearchSB", ["src/wrapper/core/DocumentSearchSB.pyx"]),
    Extension("wrapper.core.File", ["src/wrapper/core/File.pyx"]),
    Extension("wrapper.core.Image", ["src/wrapper/core/Image.pyx"]),
    Extension("wrapper.core.PDF", ["src/wrapper/core/PDF.pyx"]),
    Extension("wrapper.core.Video", ["src/wrapper/core/Video.pyx"]),
    Extension("wrapper.infra.AbsctractGenerator", ["src/wrapper/infra/AbsctractGenerator.pyx"]),
    Extension("wrapper.infra.DocumentSimilarityCalculator", ["src/wrapper/infra/DocumentSimilarityCalculator.pyx"]),
    Extension("wrapper.infra.ImageObjectsExtractor", ["src/wrapper/infra/ImageObjectsExtractor.pyx"]),
    Extension("wrapper.infra.LanguageDetector", ["src/wrapper/infra/LanguageDetector.pyx"]),
    Extension("wrapper.infra.NERExtractor", ["src/wrapper/infra/NERExtractor.pyx"]),
    Extension("wrapper.infra.PreProcessing", ["src/wrapper/infra/PreProcessing.pyx"]),
    Extension("wrapper.infra.TextExtractor", ["src/wrapper/infra/TextExtractor.pyx"]),
    Extension("wrapper.infra.TextFeatureExtractor", ["src/wrapper/infra/TextFeatureExtractor.pyx"]),
    Extension("wrapper.infra.VideoObjectsExtractor", ["src/wrapper/infra/VideoObjectsExtractor.pyx"]),
    Extension("wrapper.infra.WordFixer", ["src/wrapper/infra/WordFixer.pyx"]),
    Extension("tests.ProcessPDFImageTest", ["tests/ProcessPDFImageTest.pyx"]),
    # Extension("cypack.utils", ["src/cypack/utils.pyx"]),
    # Extension("cypack.answer", ["src/cypack/answer.pyx"]),
    # Extension("cypack.fibonacci", ["src/cypack/fibonacci.pyx"]),
    # Extension(
    #     "cypack.sub.wrong",
    #     ["src/cypack/sub/wrong.pyx", "src/cypack/sub/helper.c"]
    # ),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None

if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")

with open("requirements-dev.txt") as fp:
    dev_requires = fp.read().strip().split("\n")

setup(
    ext_modules=extensions,
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "docs": ["sphinx", "sphinx-rtd-theme"]
    },
    options={'bdist_wheel': {'plat_name': 'manylinux2014_x86_64'}}
)