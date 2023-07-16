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
    rev = "dd5f7b0ebd607be969daa67413aee55edbbbc525";
    sha256 = "sha256-J77KcdHFwEmK4Q/DlxvTBDpLnJh6/buSJqaX4Lj2n2g=";
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
