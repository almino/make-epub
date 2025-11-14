{ pkgs ? import <nixos-unstable> { }, ... }:

let
  python-packages = ps: with ps; [
    beautifulsoup4
    black
    css-inline
    jupyter
    notebook
    numpy
    pandas
    pandoc-latex-environment
    pymupdf
    pypandoc
    werkzeug
  ];
  shellPython = pkgs.python3.withPackages python-packages;
in

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3Packages.virtualenv # run virtualenv .
    # python3Packages.black
    # python3Packages.pandas
    python3Packages.pymupdf
  ];
  packages = with pkgs; [
    pandoc
    sqlitebrowser
    texliveMedium
    uv
  ] ++ [ shellPython ];
  shellHook = ''
    python -m venv .venv --copies
    uv sync --active --no-install-project --managed-python --quiet --python .venv/bin/python
  '';
}
