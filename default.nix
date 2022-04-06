with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    mypy
    python3
    black
  ];
}
