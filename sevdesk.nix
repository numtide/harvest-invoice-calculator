{ buildPythonPackage
, fetchFromGitHub
, requests
, attrs
, cattrs
, httpx
, python-dateutil
, poetry-core
}:

buildPythonPackage {
  pname = "SevDesk-Python-Client";
  version = "2022-04-06";
  src = fetchFromGitHub {
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
  propagatedBuildInputs = [
    requests
    attrs
    cattrs
    httpx
    python-dateutil
  ];
  nativeBuildInputs =  [
    poetry-core
  ];
  format = "pyproject";
}
