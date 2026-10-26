{
  description = "Observatorio de Turismo Sostenible — Laboratorio 10 (CC3084, UVG)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { self, nixpkgs }:
    let
      sistemas = [
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];
      paraCada = f: nixpkgs.lib.genAttrs sistemas (system: f nixpkgs.legacyPackages.${system});

      # Mismas dependencias que requirements.txt.
      # plotly de nixpkgs-unstable es 6.x: con 7.x Streamlit deja de entregar
      # el evento de seleccion que enlaza V3 -> V1/V2 y V5 -> V6.
      pythonDe =
        pkgs:
        pkgs.python3.withPackages (ps: [
          ps.streamlit
          ps.plotly
          ps.altair
          ps.pandas
          ps.numpy
          ps.scikit-learn
          ps.statsmodels
        ]);

      # Inter para que el PDF tenga la misma tipografia en cualquier maquina.
      fuentesDe = pkgs: pkgs.makeFontsConf { fontDirectories = [ pkgs.inter ]; };

      herramientasDocs = pkgs: [
        pkgs.pandoc
        pkgs.python3Packages.weasyprint
      ];
    in
    {
      packages = paraCada (pkgs: {
        # nix run .#docs [archivo.md ...]  — por defecto docs/documento_diseno.md
        docs = pkgs.writeShellApplication {
          name = "docs";
          runtimeInputs = herramientasDocs pkgs;
          text = ''
            export FONTCONFIG_FILE=${fuentesDe pkgs}
            [ "$#" -eq 0 ] && set -- docs/documento_diseno.md
            for origen in "$@"; do
              destino="''${origen%.md}.pdf"
              pandoc "$origen" \
                --from markdown \
                --to html5 \
                --standalone \
                --metadata lang=es \
                --lua-filter docs/pdf/portada.lua \
                --css docs/pdf/estilo.css \
                --pdf-engine weasyprint \
                --output "$destino"
              echo "$destino"
            done
          '';
        };

        # nix run  — levanta el tablero
        tablero = pkgs.writeShellApplication {
          name = "tablero";
          runtimeInputs = [ (pythonDe pkgs) ];
          text = ''exec streamlit run app/app.py "$@"'';
        };

        default = self.packages.${pkgs.stdenv.hostPlatform.system}.tablero;
      });

      devShells = paraCada (pkgs: {
        default = pkgs.mkShell {
          packages = [ (pythonDe pkgs) ] ++ herramientasDocs pkgs;
          FONTCONFIG_FILE = fuentesDe pkgs;
        };
      });

      formatter = paraCada (pkgs: pkgs.nixfmt-rfc-style);
    };
}
