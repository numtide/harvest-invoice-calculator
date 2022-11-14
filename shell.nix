{ pkgs ? import <nixpkgs> {} }:
let
  harvest-exporter = pkgs.callPackage ./harvest-exporter.nix {};
  sevdesk-invoicer = pkgs.callPackage ./sevdesk-invoicer.nix {};
in pkgs.mkShell {
  nativeBuildInputs = sevdesk-invoicer.nativeBuildInputs ++ harvest-exporter.nativeBuildInputs;
  propagatedBuildInputs = sevdesk-invoicer.propagatedBuildInputs ++ harvest-exporter.propagatedBuildInputs;
  dontUseSetuptoolsShellHook = 1;
}
