with import <nixpkgs> {};

( let
    pint = pkgs.python35Packages.buildPythonPackage rec {
      name = "pint-${version}";
      version = "0.7.2";

      src = pkgs.fetchurl{
        url = "https://pypi.python.org/packages/source/P/Pint/Pint-0.7.2.tar.gz";
        sha256 = "38b97d352a6376bb4e957095c8b75c1c2aa8edbf9a7ccf058d69b147862e77ad";
      };

      meta = {
        homepage = "gla";
        description = "gla";
        license = "gla";
        maintainers = "gla";
      };
    };

  in pkgs.python35.buildEnv.override {
    
    extraLibs = [ pkgs.python35Packages.ipython 
                  pkgs.python35Packages.uncertainties
                  pkgs.python35Packages.matplotlib
                  pint];
}
).env

