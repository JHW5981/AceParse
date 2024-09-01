python download_source.py --request_num 2 --arxiv_ids ./arxiv_ids.txt --source_path ./downloads --tex_path ./TEX
python synthesize_latex.py --tex_path ./TEX --save_file ./SYNS_TEX --length_options 1400,1600,1800 --total_files 10 --files_per_shard 10
bash generate_pdfs.sh ./SYNS_TEX ./SYNS_PDF 
python crop_images.py --pdf_path ./SYNS_PDF --save_path ./IMAGE

