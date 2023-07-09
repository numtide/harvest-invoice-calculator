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
    rev = "7faaf06bdc6ca15ad1c90da1c6b178eca2445f29";
    sha256 = "sha256-GWXbbGj8GXLM/2ccu5V/j+xnk/aQKAyfrc7pYOKsFrQ=";
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
