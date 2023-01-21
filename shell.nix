{ pkgs ? import <nixpkgs> { }, treefmt ? null }:
let
  harvest-exporter = pkgs.callPackage ./harvest-exporter.nix { };
  sevdesk-invoicer = pkgs.callPackage ./sevdesk-invoicer.nix { };
in
pkgs.mkShell {
  packages = sevdesk-invoicer.nativeBuildInputs
    ++ harvest-exporter.nativeBuildInputs
    ++ pkgs.lib.optional (treefmt != null) treefmt;
  propagatedBuildInputs = sevdesk-invoicer.propagatedBuildInputs ++ harvest-exporter.propagatedBuildInputs;
  dontUseSetuptoolsShellHook = 1;
}
