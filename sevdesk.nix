{ buildPythonPackage
, fetchFromGitHub
, requests
, attrs
, cattrs
, httpx
, python-dateutil
, poetry-core
, exceptiongroup
}:

buildPythonPackage {
  pname = "SevDesk-Python-Client";
  version = "2023-07-16";
  src = fetchFromGitHub {
    owner = "Mic92";
    repo = "SevDesk-Python-Client";
    rev = "80840fa02b91dcaf87c9631094cbf43a419ef6eb";
    sha256 = "sha256-gBxfBPoBp5tIAexzIRSBM+05ebm1Q0ilHfCvlYabHr8=";
  };
  postPatch = ''
    sed -i -e 's/"^.*"/"*"/' pyproject.toml
    sed -i -e '/openapi-python-client/d' pyproject.toml
    cat pyproject.toml
  '';
  propagatedBuildInputs = [
    requests
    attrs
    cattrs
    httpx
    python-dateutil
    exceptiongroup
  ];
  nativeBuildInputs = [
    poetry-core
  ];
  format = "pyproject";
}
