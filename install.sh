#!/bin/sh
# sumdisplay install helper - GPL-2.0-or-later
set -eu
HERE=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
BIN_DIR=${SUMDISP_BIN_DIR:-"$HOME/bin"}
METHOD=standalone
ALIASES=no

for arg in "$@"; do
    case "$arg" in
        --pip) METHOD=pip ;;
        --aliases) ALIASES=yes ;;
        --help|-h)
            echo 'Uso: ./install.sh [--pip] [--aliases]';
            echo 'Por defecto instala sumdisp en ~/bin (o SUMDISP_BIN_DIR).';
            echo '--pip instala paquete Python en directorio de usuario.';
            echo '--aliases crea enlaces disp, pantalla, setBright, ajustaBrillo y sumdisplay.';
            exit 0 ;;
        *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
    esac
done

if [ "$METHOD" = pip ]; then
    if ! python3 -m pip install --user --no-deps --no-build-isolation "$HERE"; then
        echo 'Si Ubuntu bloquea pip (PEP 668), usá ./install.sh sin --pip.' >&2;
        echo 'También podés utilizar un entorno virtual.' >&2;
        exit 1;
    fi
    echo 'Instalación pip completa. Verificá: sumdisp --version';
    exit 0;
fi
mkdir -p -- "$BIN_DIR"
install -m 755 -- "$HERE/sumdisp" "$BIN_DIR/sumdisp"
if [ "$ALIASES" = yes ]; then
    for name in sumdisplay disp pantalla setBright ajustaBrillo; do
        if [ -e "$BIN_DIR/$name" ] && [ ! -L "$BIN_DIR/$name" ]; then
            echo "No reemplazo archivo existente: $BIN_DIR/$name" >&2;
        else
            ln -sfn sumdisp "$BIN_DIR/$name";
        fi
    done
fi
printf 'Instalado: %s/sumdisp\n' "$BIN_DIR"
printf 'Ejecutá: %s/sumdisp --version\n' "$BIN_DIR"
