{
  nixpkgs,
  python_version,
  pythonOverrideUtils,
}: let
  lib = {
    buildEnv = nixpkgs."${python_version}".buildEnv.override;
    inherit (nixpkgs."${python_version}".pkgs) buildPythonPackage;
    inherit (nixpkgs.python3Packages) fetchPypi;
  };

  utils = pythonOverrideUtils;
  pkgs_overrides = override: python_pkgs: builtins.mapAttrs (_: override python_pkgs) python_pkgs;

  arch-lint = import ./arch_lint.nix {
    inherit nixpkgs python_version;
  };

  layer_1 = python_pkgs:
    python_pkgs
    // {
      arch-lint = arch-lint.pkg;
      more-itertools = import ./more-itertools.nix lib python_pkgs;
      types-deprecated = import ./deprecated/stubs.nix lib;
      types-simplejson = import ./simplejson/stubs.nix lib;
    };
  python_pkgs = utils.compose [layer_1] nixpkgs."${python_version}Packages";
in {
  inherit lib python_pkgs;
}
