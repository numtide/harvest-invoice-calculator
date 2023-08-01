{
  description = "Flake utils demo";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/master";
  inputs.flake-parts.url = "github:hercules-ci/flake-parts";
  inputs.flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = inputs @ { flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];
      imports = [
        inputs.treefmt-nix.flakeModule
      ];
      perSystem = { config, pkgs, lib, ... }: {
        devShells.default = pkgs.callPackage ./shell.nix {
          treefmt = config.treefmt.build.wrapper;
        };
        packages = {
          harvest-exporter = pkgs.callPackage ./harvest-exporter.nix { };
          harvest-report = pkgs.callPackage ./harvest-report.nix { };
          wise-exporter = pkgs.callPackage ./wise-exporter.nix { };
          sevdesk-invoicer = pkgs.callPackage ./sevdesk-invoicer.nix { };
          sevdesk = pkgs.python3.pkgs.callPackage ./sevdesk.nix { };
          quipu-invoicer = pkgs.python3.pkgs.callPackage ./quipu-invoicer.nix { };

          working-days-calculator = pkgs.writers.writePython3Bin "working-days-calculator"
            {
              libraries = [ pkgs.python3Packages.pandas ];
              flakeIgnore = [ "E501" ];
            }
            (builtins.readFile ./working-days-calculator.py);

          default = config.packages.harvest-exporter;
        };
        treefmt = {
          # Used to find the project root
          projectRootFile = "flake.lock";

          programs.mypy = {
            enable = true;
            directories = {
              ".".modules = [
                "harvest"
                "harvest_exporter"
                "harvest_report"
                "rest"
              ];
              "sevdesk-invoicer" = { };
              "wise-exporter" = {
                extraPythonPackages = [ pkgs.python3.pkgs.rsa ];
              };
              "quipu-invoicer" = { };
            };
          };

          settings.formatter = {
            nix = {
              command = "sh";
              options = [
                "-eucx"
                ''
                  export PATH=${lib.makeBinPath [ pkgs.coreutils pkgs.findutils pkgs.statix pkgs.deadnix pkgs.nixpkgs-fmt ]}
                  deadnix --edit "$@"
                  # statix breaks flake.nix's requirement for making outputs a function
                  echo "$@" | xargs -P$(nproc) -n1 statix fix -i flake.nix node-env.nix
                  nixpkgs-fmt "$@"
                ''
                "--"
              ];
              includes = [ "*.nix" ];
            };
            python = {
              command = "sh";
              options = [
                "-eucx"
                ''
                  ${pkgs.lib.getExe pkgs.ruff} --fix "$@"
                  ${pkgs.lib.getExe pkgs.python3.pkgs.black} "$@"
                ''
                "--" # this argument is ignored by bash
              ];
              includes = [ "*.py" ];
            };
          };
        };
      };
    };
}
