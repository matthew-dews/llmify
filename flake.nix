{
  description = "A Nix flake for the llmify.py script";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";  # Adjust this if you're on a different system
      pkgs = import nixpkgs { inherit system; };
      pythonPackages = pkgs.python3Packages;
    in
    {
      packages.${system}.llmify = pythonPackages.buildPythonApplication {
        pname = "llmify";
        version = "1.0.0";  # Update as needed

        src = ./.;

        # Specify Python dependencies here
        propagatedBuildInputs = with pythonPackages; [
          # Add required Python packages, e.g.,
          # requests
        ];

        # Install the script
        installPhase = ''
          mkdir -p $out/bin
          cp llmify.py $out/bin/llmify
          chmod +x $out/bin/llmify
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
