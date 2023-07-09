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
  version = "2023-07-09";
  src = fetchFromGitHub {
    owner = "Mic92";
    repo = "SevDesk-Python-Client";
    rev = "41cf376d021a1eb2355e4d6eaf0c31d604c3d13e";
    sha256 = "sha256-djeNJpMrd4yQW38i2JBGnDm//HWGYjfuOGFnLQ6Wytw=";
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
