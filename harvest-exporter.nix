{ pkgs ? import <nixpkgs> { } }:
pkgs.python3.pkgs.buildPythonApplication {
  pname = "harvest-exporter";
  version = "0.0.1";
  src = ./.;

  nativeBuildInputs = [
    pkgs.python3.pkgs.black
    pkgs.python3.pkgs.mypy
  ];

  doCheck = true;
  checkPhase = ''
    mypy harvest_exporter
    black --check .
  '';
}
