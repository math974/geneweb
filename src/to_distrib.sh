#!/usr/bin/env bash

python_modules_path="src/python"
distrib_path="./distribution/gw"
binaries=(
    "ged2gwb"
    "consang"
)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --py-modules)
            python_modules_path="$2"
            shift 2
            ;;
        --distrib-path)
            distrib_path="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo $(pwd)
for bin in "${binaries[@]}"; do
    echo -n "Processing $python_modules_path/$bin  "
    if [ -d "$python_modules_path/$bin" ]; then
        echo -e "-- Found\033[2m"
        echo "Copy $python_modules_path/$bin/* to $distrib_path/${bin}_module"
        mkdir -p "$distrib_path/${bin}_module"
        cp -r "$python_modules_path/$bin"/* "$distrib_path/${bin}_module"
        if [ -f "$distrib_path/$bin" ] && [ ! -e "$distrib_path/${bin}.old" ]; then
            mv "$distrib_path/$bin" "$distrib_path/${bin}.old"
        fi
        echo "#!/usr/bin/env bash" > "$distrib_path/$bin"
        echo "absolute_path=\$(dirname \"\$0\")" >> "$distrib_path/$bin"
        echo "PYTHONPATH=\$absolute_path python3 -m \"${bin}_module\" \"\$@\"" >> "$distrib_path/$bin"

        chmod +x "$distrib_path/$bin"
    else
        echo "-- Not found"
    fi
    echo -en "\033[0m"
done

cp -r "$python_modules_path"/lib "$distrib_path"/lib
cp -r "$python_modules_path"/gedcom "$distrib_path"/gedcom