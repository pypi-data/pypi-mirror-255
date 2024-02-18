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
    python3 tests/vetox.py run-parallel
    exit
  '';
}
