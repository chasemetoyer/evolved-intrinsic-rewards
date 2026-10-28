#!/bin/sh
# Build paper/arxiv-upload.tar.gz: the files arXiv needs to compile the paper with pdfLaTeX, including the .bbl
# (arXiv does not run BibTeX when a .bbl is present). Run from anywhere; rebuilds the PDF first.
set -e
cd "$(dirname "$0")/.."
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null
rm -rf arxiv && mkdir -p arxiv/tables arxiv/figs
cp main.tex main.bbl numbers.tex arxiv/
cp tables/*.tex arxiv/tables/
cp figs/*.pdf arxiv/figs/
(cd arxiv && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null \
  && rm -f main.aux main.log main.out main.pdf)
tar -czf arxiv-upload.tar.gz -C arxiv .
rm -rf arxiv
echo "wrote paper/arxiv-upload.tar.gz (compiled cleanly from the bundle alone)"
