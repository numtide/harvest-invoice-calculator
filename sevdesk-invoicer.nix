{ pkgs ? import <nixpkgs> {} }:
let
  sevdesk = pkgs.python3.pkgs.buildPythonPackage {
    pname = "SevDesk-Python-Client";
    version = "2022-04-06";
    src = pkgs.fetchFromGitHub {
      owner = "HpLightcorner";
      repo = "SevDesk-Python-Client";
      rev = "2347f5c1b8d4376640bacead08be2266a5221fbd";
      sha256 = "sha256-i4IvTs67iZsTjcLbFElRktBMAWcbSll0F+QA8L0jYNY=";
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
