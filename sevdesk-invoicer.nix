{ pkgs ? import <nixpkgs> { } }:
let
  sevdesk = pkgs.python3.pkgs.callPackage ./sevdesk.nix { };
in
pkgs.python3.pkgs.buildPythonApplication {
  pname = "sevdesk-invoicer";
  version = "0.0.1";
  src = ./sevdesk-invoicer;
  pyproject = true;
  propagatedBuildInputs = [
    sevdesk
  ];
  nativeBuildInputs = [
    pkgs.python3.pkgs.setuptools
  ];

  doCheck = false;
}
