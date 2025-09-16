{
  description = "A basic flake with a shell";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  # inputs.nixpkgs.url = "github:NixOS/nixpkgs/1ae1ab8d01d53806bfaf96beddd86776d9cd205e";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pypi =
          ps: with ps; [
            aiofiles
            aiohttp
            beautifulsoup4
            debugpy
            fastapi
            httpx
            icecream
            jinja2
            lxml
            mypy
            pydantic-settings
            pyyaml
            requests
            scrapy
            sqlmodel
            uvicorn
            websockets
          ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.hurl
            pkgs.pyright
            pkgs.nodePackages.typescript
            (pkgs.python313.withPackages pypi)
            # pkgs.python310Packages.uvicorn
            # pkgs.python310Packages.fastapi
            # pkgs.python310Packages.jinja2
            # pkgs.python310Packages.aiohttp
            # pkgs.python310Packages.aiofiles
            # pkgs.python310Packages.requests
            # pkgs.python310Packages.beautifulsoup4
            # pkgs.python310Packages.lxml
            # pkgs.python310Packages.scrapy
            # pkgs.python310Packages.mypy
            # pkgs.python310Packages.pyyaml
            # pkgs.python310Packages.websockets
          ];
          buildInputs = with pkgs; [
            (writeShellScriptBin "hey" ''
              echo "start"

              (nohup bash -c 'sleep 1 && xdg-open http://localhost:8585' > /dev/null 2>&1 ) & \
              uvicorn main:app --host 0.0.0.0 --port 8585 --reload --env-file envs/molclass.env
            '')
            (writeShellScriptBin "cya" ''
              echo "stop"
            '')
          ];
          shellHook = ''
            echo "======================="
            echo "Available commands:"
            echo "  hey - Start services"
            echo "  cya - Stop services"
            echo "======================="
          '';

        };
      }
    );
}
