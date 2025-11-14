{ pkgs ? import <nixos-unstable> { }, ... }:

let
  python-packages = ps: with ps; [
    beautifulsoup4
    black
    css-inline
    # huggingface-hub
    pypandoc
    pandoc-latex-environment
    # regex
    werkzeug
  ];
in

pkgs.mkShell {
  packages = with pkgs; [
    (python3.withPackages python-packages)
    pandoc
    sqlitebrowser
    texliveMedium
    uv
  ];
  shellHook = ''
    uv sync
    python -m venv .venv --copies
  '';
}
