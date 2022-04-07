{ pkgs ? import <nixpkgs> {} }:
let
  sevdesk = pkgs.python3.pkgs.buildPythonPackage {
    pname = "SevDesk-Python-Client";
    version = "2022-04-06";
    src = pkgs.fetchFromGitHub {
      owner = "Mic92";
      repo = "SevDesk-Python-Client";
      rev = "e599524ffcee7c37a4cc7219dfd9c06ae056b950";
      sha256 = "sha256-OGI/e8W6PhfzAF6IlnVDO6O+k0mcLS/Ink+Nc0IxEsA=";
    };
    postPatch = ''
      sed -i -e 's/"^.*"/"*"/' pyproject.toml
      sed -i -e '/openapi-python-client/d' pyproject.toml
      cat pyproject.toml
    '';
    propagatedBuildInputs = with pkgs.python3.pkgs; [
      requests
      attrs
      cattrs
      httpx
      python-dateutil
    ];
    nativeBuildInputs = with pkgs.python3.pkgs; [
      poetry-core
    ];
    format = "pyproject";
  };
in pkgs.python3.pkgs.buildPythonApplication {
  pname = "sevdesk-invoicer";
  version = "0.0.1";
  src = ./sevdesk-investor;
  propagatedBuildInputs = [
    sevdesk
  ];
  nativeBuildInputs = [
    pkgs.python3.pkgs.black
    pkgs.python3.pkgs.mypy
  ];

  doCheck = true;
  checkPhase = ''
    mypy sevdesk_invoicer
    black --check .
  '';
}
