{ pkgs ? import <nixpkgs> { }, treefmt ? null }:
let
  harvest-exporter = pkgs.callPackage ./harvest-exporter.nix { };
  sevdesk-invoicer = pkgs.callPackage ./sevdesk-invoicer.nix { };
in
pkgs.mkShell {
  shellHook = ''
    export PATH=$PATH:./bin
  '';
  packages = sevdesk-invoicer.nativeBuildInputs
    ++ harvest-exporter.nativeBuildInputs
    ++ pkgs.lib.optional (treefmt != null) treefmt
    ++ [
    pkgs.python3Packages.rsa
    pkgs.texlive.combined.scheme-small
    pkgs.pandoc
  ];
  propagatedBuildInputs = sevdesk-invoicer.propagatedBuildInputs ++ harvest-exporter.propagatedBuildInputs;
  dontUseSetuptoolsShellHook = 1;
}
