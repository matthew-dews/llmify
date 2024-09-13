{
  description = "A Nix flake for the llmify.py script";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pythonPackages = pkgs.python3Packages;
    in
    {
      packages.${system}.llmify = pythonPackages.buildPythonApplication rec {
        pname = "llmify";
        version = "1.0.0";

        src = ./.;

        format = "other";  # Skip the default build process that expects setup.py

        propagatedBuildInputs = with pythonPackages; [
          # Add required Python packages here
          # Example: requests
          # requests
        ];

        # Override build phases
        buildPhase = "echo 'No build required'";
        installPhase = ''
          mkdir -p $out/bin
          cp llmify.py $out/bin/llmify
          chmod +x $out/bin/llmify
        '';

        # Ensure the script runs with the correct interpreter and PYTHONPATH
        postFixup = ''
          wrapProgram $out/bin/llmify --prefix PYTHONPATH : ${pythonPackages.concatPackages propagatedBuildInputs}/lib/python${pythonPackages.pythonVersion}/site-packages
        '';

        meta = with pkgs.lib; {
          description = "llmify Python script";
          homepage = "https://github.com/corinfinite/llmify";
        #   license = licenses.mit;  # Choose the appropriate license
        #   maintainers = [ maintainers.yourusername ];
        };
      };
    };
}
