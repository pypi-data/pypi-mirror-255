# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? import <nixpkgs> { }
, py-ver ? 311
}:
let
  python-name = "python${toString py-ver}";
  python = builtins.getAttr python-name pkgs;
in
pkgs.mkShell {
  buildInputs = [
    pkgs.gitMinimal
    python
  ];
  shellHook = ''
    set -e
    python3 src/vetox/__main__.py run-parallel
    exit
  '';
}
