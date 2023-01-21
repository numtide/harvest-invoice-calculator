with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    chromedriver
    python3.pkgs.selenium
  ];
}
