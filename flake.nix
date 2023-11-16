{
  description = "A basic flake with a shell";
  # inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/1ae1ab8d01d53806bfaf96beddd86776d9cd205e";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.default = pkgs.mkShell {
        packages = [
          pkgs.nodePackages.typescript
          pkgs.nodePackages.pyright
          pkgs.python310Full
          pkgs.python310Packages.uvicorn
          pkgs.python310Packages.fastapi
          pkgs.python310Packages.jinja2
          pkgs.python310Packages.aiohttp
          pkgs.python310Packages.aiofiles
          pkgs.python310Packages.requests
          pkgs.python310Packages.beautifulsoup4
          pkgs.python310Packages.lxml
          pkgs.python310Packages.scrapy
          pkgs.python310Packages.mypy
          pkgs.python310Packages.pyyaml
          pkgs.python310Packages.websockets
        ];
      };
    });
}
