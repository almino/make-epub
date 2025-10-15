{ pkgs ? import <nixos-unstable> { }, ... }:

let
  python-packages = ps: with ps; [
    beautifulsoup4
    black
    # huggingface-hub
    # regex
    werkzeug
  ];
in

pkgs.mkShell {
  packages = with pkgs; [
    (python3.withPackages python-packages)
    sqlitebrowser
    uv
  ];
  shellHook = ''
    python -m venv .venv --copies
    uv sync
  '';
}
