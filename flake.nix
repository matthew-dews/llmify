{
  description = "A Nix flake for the llmify.py script";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";  # Adjust this if you're on a different system
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python3;
    in
    {
      packages.${system}.llmify = python.lib.buildPythonApplication {
        pname = "llmify";
        version = "1.0.0";  # Update as needed

        src = ./.;

        # If your script requires additional Python packages, specify them here
        propagatedBuildInputs = with python.pkgs; [
          # Add required Python packages, e.g., requests
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
