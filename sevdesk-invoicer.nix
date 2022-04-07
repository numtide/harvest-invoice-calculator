{ pkgs ? import <nixpkgs> {} }:
let
  sevdesk = pkgs.python3.pkgs.buildPythonPackage {
    pname = "SevDesk-Python-Client";
    version = "2022-04-06";
    src = pkgs.fetchFromGitHub {
      owner = "Mic92";
      repo = "SevDesk-Python-Client";
      rev = "dba3fab846958423132420d5b6b175a4bff39912";
      sha256 = "sha256-DrUnWIqV6kw/jwcfI8Zu5IKH4pIxQCVZv5IWNICcdPE=";
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
