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
    rev = "3ceb95e91e645d07867c0275cac4de7eff589eee";
    sha256 = "sha256-I7ZEcoQEGFVZJ+IGp5z5qlpNCeo0jf9f5K4lipKzIpM=";
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
