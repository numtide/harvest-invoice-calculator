{ pkgs ? import <nixpkgs> { } }:
pkgs.python3.pkgs.buildPythonApplication {
  pname = "harvest-report";
  version = "0.0.1";
  src = ./.;

  nativeBuildInputs = [
    pkgs.python3.pkgs.mypy
  ];

  doCheck = true;
  postPatch = ''
    sed -i "/harvest-exporter/d" setup.cfg
  '';

  makeWrapperArgs = [
    "--prefix"
    "PATH"
    ":"
    (pkgs.lib.makeBinPath [ pkgs.pandoc pkgs.texlive.combined.scheme-small ])
  ];

  checkPhase = ''
    mypy harvest_report
  '';
}
