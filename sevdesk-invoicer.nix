{ pkgs ? import <nixpkgs> { } }:
let
  sevdesk = pkgs.python3.pkgs.callPackage ./sevdesk.nix { };
in
pkgs.python3.pkgs.buildPythonApplication {
  pname = "sevdesk-invoicer";
  version = "0.0.1";
  src = ./sevdesk-invoicer;
  format = "pyproject";
  propagatedBuildInputs = [
    sevdesk
  ];
  nativeBuildInputs = [
    pkgs.python3.pkgs.setuptools
    pkgs.python3.pkgs.black
    pkgs.python3.pkgs.mypy
  ];

  doCheck = true;
  checkPhase = ''
    mypy sevdesk_invoicer
    black --check .
  '';
}
