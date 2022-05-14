{
  description = "Flake utils demo";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/master";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      rec {
        packages = {
          harvest-exporter = pkgs.callPackage ./harvest-exporter.nix {};
          sevdesk-invoicer = pkgs.callPackage ./sevdesk-invoicer.nix {};
          sevdesk = pkgs.callPackage ./sevdesk.nix {};
        };
        devShell = pkgs.callPackage ./shell.nix {};
        defaultPackage = packages.harvest-exporter;
      }
    );
}
