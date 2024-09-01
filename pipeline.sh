python ./dataset/download_source.py --request_num 2 --arxiv_ids ./dataset/arxiv_ids.txt --source_path ./dataset/downloads --tex_path ./dataset/TEX
python ./dataset/synthesize_latex.py --tex_path ./dataset/TEX --save_file ./dataset/SYNS_TEX --length_options 1400,1600,1800 --total_files 10 --files_per_shard 10
bash ./dataset/generate_pdfs.sh ./dataset/SYNS_TEX ./dataset/SYNS_PDF 
python ./dataset/crop_images.py --pdf_path ./dataset/SYNS_PDF --save_path ./dataset/IMAGE
python ./dataset/split_dataset.py --save_imgs ./dataset/data/images --save_labels ./dataset/data/labels --tex_path ./dataset/SYNS_TEX --img_path ./dataset/IMAGE

    
