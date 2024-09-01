#!/bin/bash

# check if we have enough params
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <base_tex_dir> <base_pdf_dir>"
    exit 1
fi

# get paths
base_tex_dir="$1"
base_pdf_dir="$2"

# create if not exist
if [ ! -d "$base_pdf_dir" ]; then
    mkdir -p "$base_pdf_dir"
fi

shard_count=$(find "$base_tex_dir" -maxdepth 1 -type d -name 'TEX*' | wc -l)

for ((shard=1; shard<=shard_count; shard++)); do
    tex_dir="$base_tex_dir/TEX${shard}"
    pdf_dir="$base_pdf_dir/PDF${shard}"

    if [ ! -d "$pdf_dir" ]; then
        mkdir -p "$pdf_dir"
    fi

    for tex_file in "$tex_dir"/*.tex; do

        base_name=$(basename "$tex_file" .tex)

        timeout 10s pdflatex -interaction=nonstopmode -output-directory "$pdf_dir" "$tex_file"

        pdf_file="$pdf_dir/$base_name.pdf"
        if [ -f "$pdf_file" ]; then
            for ext in "aux" "log" "out" "tex"; do
                file_to_delete="$pdf_dir/$base_name.$ext"
                if [ -f "$file_to_delete" ]; then
                    rm "$file_to_delete"
                fi
            done
        else
            echo "Failed to compile $tex_file within the time limit."
        fi
    done
done