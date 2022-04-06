{ pkgs ? import <nixpkgs> {} }:
pkgs.python3.pkgs.buildPythonApplication {
  pname = "harvest-invoice-calculator";
  version = "0.0.1";
  src = ./.;
  installPhase = ''
  '';
  doCheck = true;
  nativeBuildInputs = [
    pkgs.python3.pkgs.black
    pkgs.python3.pkgs.mypy
  ];
  checkPhase = ''
    mypy harvest_invoice_calculator
    black --check .
  '';
}
