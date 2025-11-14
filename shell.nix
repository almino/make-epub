{ pkgs ? import <nixos-unstable> { }, ... }:

let
  python-packages = ps: with ps; [
    beautifulsoup4
    black
    css-inline
    pymupdf
    pypandoc
    pandoc-latex-environment
    werkzeug
  ];
  shellPython = pkgs.python3.withPackages python-packages;
in

pkgs.mkShell {
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
