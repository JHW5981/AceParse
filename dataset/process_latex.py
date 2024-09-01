import os
import regex as re
import random

def extract_and_process_newcommands(latex_code):
    # Define a regex pattern to find all \newcommand lines
    pattern = r'\\newcommand.*\n'
    
    # Remove all \newcommand lines from the LaTeX code
    cleaned_code = re.sub(pattern, '', latex_code)
    
    # Process each \newcommand line
    command_replacements = []
    patterns = [
        # 1. 不带参数的命令: \newcommand{\commandname}{replacement text}
        r'\\newcommand{\\(\w+)}{((?:[^{}]|{(?2)})*)}',
        # 2. 带参数的命令: \newcommand{\commandname}[n]{replacement text}
        r'\\newcommand{\\(\w+)}\[(\d+)\]{((?:[^{}]|{(?3)})*)}',
        # 3. 带默认参数的命令: \newcommand{\\(\w+)}\[(\d+)\]\[([^\]]*)\]{([^{}]*)}'
        r'\\newcommand{\\(\w+)}\[(\d+)\]\[([^\]]*)\]{((?:[^{}]|{(?4)})*)}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, latex_code)
        for match in matches:
            if len(match) == 2:  # 不带参数的命令
                command, replacement_text = match
                command_replacements.append(('\\' + command, [], replacement_text))
            elif len(match) == 3:  # 带参数的命令
                command, num_params, replacement_text = match
                command_replacements.append(('\\' + command, ['#' + str(i + 1) for i in range(int(num_params))], replacement_text))
            elif len(match) == 4:  # 带默认参数的命令
                command, num_params, default_value, replacement_text = match
                params = ['#' + str(i + 1) for i in range(int(num_params))]
                command_replacements.append(('\\' + command, params, replacement_text))
                
    return command_replacements, cleaned_code

def extract_and_process_defs(latex_code):
    # Define a regex pattern to find all \def lines
    pattern = r'\\def\s*\\.*\n'
    
    # Remove all \def lines from the LaTeX code
    cleaned_code = re.sub(pattern, '', latex_code)
    
    # Process each \def line
    command_replacements = []
    patterns = [
        # 1. 不带参数的命令: \def\commandname{replacement text}
        r'\\def\\(\w+)\{((?:[^{}]|{(?2)})*)\}',

        # 2. 带参数的命令: \def\commandname#1{replacement text}
        r'\\def\\(\w+)((?:#\d+)+)\{((?:[^{}]|{(?3)})*)\}',

        # 3. 带多个参数的命令: \def\commandname#1#2{replacement text}
        r'\\def\\(\w+)((?:#\d+)+)\{((?:[^{}]|{(?3)})*)\}',

        # 4. 带分隔符的参数: \def\commandname#1.#2{replacement text}
        r'\\def\\(\w+)((?:#\d+[^#{}]*)+)\{((?:[^{}]|{(?3)})*)\}',

        # 5. 带可选参数和必选参数的命令: \def\commandname[#1]#2{replacement text}
        r'\\def\\(\w+)\[(#\d+)\]((?:#\d+)+)\{((?:[^{}]|{(?4)})*)\}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, latex_code)
        for match in matches:
            command = match[0]
            if len(match) == 2:  # 不带参数的命令
                replacement_text = match[1]
                command_replacements.append(('\\' + command, [], replacement_text))
            elif len(match) == 3:  # 带一个参数的命令
                params = re.findall(r'#\d+', match[1])
                replacement_text = match[2]
                command_replacements.append(('\\' + command, params, replacement_text))
            elif len(match) == 4:  # 带多个参数或带分隔符的命令
                params = re.findall(r'#\d+', match[1])
                replacement_text = match[3]
                command_replacements.append(('\\' + command, params, replacement_text))
    
    return command_replacements, cleaned_code

def extract_and_process_mathoperators(latex_code):
    # Define a regex pattern to find all \DeclareMathOperator lines
    pattern = r'\\DeclareMathOperator.*\n'
    
    # Remove all \DeclareMathOperator lines from the LaTeX code
    cleaned_code = re.sub(pattern, '', latex_code)
    
    # Process each \DeclareMathOperator line
    command_replacements = []
    patterns = [
        # 1. 不带星号的命令: \DeclareMathOperator{\commandname}{operator}
        r'\\DeclareMathOperator{\\(\w+)}{((?:[^{}]|{(?2)})*)}',

        # 2. 带星号的命令: \DeclareMathOperator*{\commandname}{operator}
        r'\\DeclareMathOperator\*{\\(\w+)}{((?:[^{}]|{(?2)})*)}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, latex_code)
        for match in matches:
            cmd_name = match[0]  # Command name like 'sinh', 'limsup'
            operator = match[1]  # Operator text like 'sinh', 'lim sup'
            command_replacements.append(('\\' + cmd_name, [], operator))
    
    return command_replacements, cleaned_code

def convert_sections_to_bold(text):
    # 替换 \section{xxx} 为 \textbf{xxx}
    text = re.sub(r'\\section\{(.*?)\}', r'\\textbf{\1}', text)
    # 替换 \subsection{xxx} 为 \textbf{xxx}
    text = re.sub(r'\\subsection\{(.*?)\}', r'\\textbf{\1}', text)
    # 替换 \subsubsection{xxx} 为 \textbf{xxx}
    text = re.sub(r'\\subsubsection\{(.*?)\}', r'\\textbf{\1}', text)
    return text

def clean_text(text):
    def replace_ref_cite(match):
        # 随机选择替换为方括号引用或圆括号引用
        if random.random() < 0.5:
            return f'[{random.randint(1, 100)}]'
        else:
            return f'({match.group(2).replace("_", " ")})'
    
    def replace_footnote(match):
        # 替换脚注为方括号引用
        return f'$^{{{random.randint(1, 100)}}}$'
    
    # 清除所有的注释
    text = re.sub(r'(?<!\\)%.*', '', text)
    # 这步完成之后，将每行最后的空格都清除
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)    
    # 替换引用
    text = re.sub(r'\\(ref|Cref|cite|citep|cref|eqref)\{([^}]+)\}', replace_ref_cite, text)
    # 替换脚注
    text = re.sub(r'\\footnote\{([^}]+)\}', replace_footnote, text)
    # 删除 \label{...}
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    # 替换标题
    text = convert_sections_to_bold(text)
    return text

def process_tuple(input_tuple):
    return sorted(input_tuple, key=lambda item: len(item[0]), reverse=True)

def get_latex(path):
    tex = ""
    tex_names = []
    for i in os.listdir(path):
        if i.endswith(".tex"):
            tex_names.append(i)
    for tex_name in tex_names:
        try:
            with open(os.path.join(path, tex_name), "r") as fp:
                tex += fp.read()
        except:
            raise RuntimeError(f"file {tex_name} unable to decode the file with UTF-8 encoding.")
    tex = clean_text(tex)
    command_replacements1, tex = extract_and_process_newcommands(tex)
    command_replacements2, tex = extract_and_process_defs(tex)
    command_replacements3, tex = extract_and_process_mathoperators(tex)
    command_replacements = [*command_replacements1, *command_replacements2, *command_replacements3]
    command_replacements = process_tuple(command_replacements)

    return tex, command_replacements

def replace_commands_in_text(tex, command_replacements):
    def replace_command(command, params, replacement, text):
        if len(params) == 0:
            # 没有参数的命令替换
            pattern = r'(?<!\\)' + re.escape(command) + r'\b'
            return re.sub(pattern, re.escape(replacement), text)
        else:
            # 处理带参数的命令
            param_patterns = ''.join([r'\{((?:[^{}]|\{[^{}]*\})*)\}' for _ in params])
            pattern = re.escape(command) + param_patterns
            
            def replacement_function(match):
                replaced = re.escape(replacement)
                for i, param in enumerate(params):
                    replaced = replaced.replace(f'#{i + 1}', match.group(i + 1))
                return replaced
            
            return re.sub(pattern, replacement_function, text)
    
    # 对所有命令进行替换
    for command, params, replacement in command_replacements:
        tex = replace_command(command, params, replacement, tex)
    
    return tex


def extract_and_replace_tables(text, command_replacements):
    # 匹配 \begin{table} 和 \end{table} 之间的内容
    pattern = re.compile(r'(\\begin\{table\*?\})(.*?)(\\end\{table\*?\})', re.DOTALL)
    # 查找所有匹配的表格内容
    matches = pattern.findall(text)

    # 替换每个匹配内容
    replaced_matches = [
        f"{match[0]}{replace_commands_in_text(match[1], command_replacements)}{match[2]}"
        for match in matches
    ]
    # 删除表格标记和替换内容
    new_text = pattern.sub("", text)
    return replaced_matches, new_text

def extract_and_replace_formulas(text, command_replacements):
    # 匹配不同的公式环境，包括 equation、equation*、align、align* 等
    pattern = re.compile(r'(\\begin\{(?:equation|align|gather)\*?\}|\\\[)(.*?)(\\end\{(?:equation|align|gather)\*?\}|\\\])', re.DOTALL)
    
    # 查找所有匹配的公式内容
    matches = pattern.findall(text)
    

    # 替换每个匹配内容
    replaced_matches = [
        f"{match[0]}{replace_commands_in_text(match[1], command_replacements)}{match[2]}"
        for match in matches
    ]
    
    # 删除原始公式环境
    new_text = pattern.sub("", text)
    
    return replaced_matches, new_text

def extract_and_replace_items(text, command_replacements):
    # 修正后的正则表达式
    pattern = re.compile(r'(\\begin\{(itemize|enumerate)\})(.*?)(\\end\{\2\})', re.DOTALL)
    
    # 查找所有匹配的内容
    matches = pattern.findall(text)

    # 替换每个匹配内容
    replaced_matches = [
        f"{match[0]}{replace_commands_in_text(match[2], command_replacements)}{match[3]}"
        for match in matches
    ]
    
    # 删除标记和替换内容
    new_text = pattern.sub("", text)
    
    return replaced_matches, new_text


def extract_and_replace_algorithms(text, command_replacements):
    pattern = re.compile(r'(\\begin\{algorithm\*?\})(.*?)(\\end\{algorithm\*?\})', re.DOTALL)
    # 查找所有匹配的表格内容
    matches = pattern.findall(text)

    # 替换每个匹配内容
    replaced_matches = [
        f"{match[0]}{replace_commands_in_text(match[1], command_replacements)}{match[2]}"
        for match in matches
    ]
    # 删除表格标记和替换内容
    new_text = pattern.sub("", text)
    return replaced_matches, new_text

def extract_and_replace_environments(text, command_replacements):
    # 首先去掉\begin{document}和\end{document}
    text = text.replace('\\begin{document}', "")
    text = text.replace('\\end{document}', "")
    # 首先去掉\begin{abstract}和\end{abstract}
    text = text.replace('\\begin{abstract}', "")
    text = text.replace('\\end{abstract}', "")
    # 使用正则表达式来匹配 \begin{xxx}...\end{xxx} 结构
    pattern = re.compile(r'(\\begin\{([^\}]+)\})(.*?)(\\end\{\2\})', re.DOTALL)
    
    # 查找所有匹配的环境结构
    matches = pattern.findall(text)

    # 替换每个匹配内容中的命令，并将匹配到的整个结构保存
    replaced_matches = [
        f"{match[0]}{replace_commands_in_text(match[2], command_replacements)}{match[3]}"
        for match in matches
    ]
    
    # 删除所有匹配的环境结构
    new_text = pattern.sub("", text)
    
    return replaced_matches, new_text

def remove_blank_lines(text):
    # 将文本按行分割，并去掉空行
    lines = text.splitlines()
    cleaned_lines = [line for line in lines if line.strip()]
    return "\n".join(cleaned_lines)

# 过滤函数
def filter_old_fashion(data, old_fashion):
    # 使用 or ('|') 合并所有正则表达式
    pattern = re.compile("|".join(old_fashion))
    filtered_data = {}
    
    for key, lst in data.items():
        # 先去除每个项中的空行，再过滤掉包含 old_fashion 中任意元素的列表项
        cleaned_list = [remove_blank_lines(item) for item in lst]
        filtered_data[key] = [item for item in cleaned_list if not pattern.search(item)]
    
    return filtered_data

def extract_all(tex, command_replacements):
    algorithm_list = []
    formula_list = []
    table_list = []
    item_list = []
    else_list = []
    sentence_list = []
    
    algorithms, tex = extract_and_replace_algorithms(tex, command_replacements)
    formulas, tex = extract_and_replace_formulas(tex, command_replacements)
    tables, tex = extract_and_replace_tables(tex, command_replacements)
    items, tex = extract_and_replace_items(tex, command_replacements)
    elses, tex = extract_and_replace_environments(tex, command_replacements)

    # 初步筛选具有结构化的内容
    contain_dollars = [i for i in tex.split('\n') if '$' in i]
    sentences = []
    for line in contain_dollars:
        sentences.extend(line.split('. '))
    sentences = [i.strip() + '.' if len(i) > 10 and len(i) < 1000 and not i.endswith('.') else i.strip() for i in sentences]
    
    sentence_list.extend(sentences)
    algorithm_list.extend(algorithms)
    formula_list.extend(formulas)
    table_list.extend(tables)
    item_list.extend(items)
    else_list.extend(elses)
    
    old_fashion = [
        r"\\cal(?=\s|\{)", 
        r"\\rm(?=\s|\{)", 
        r"\\bf(?=\s|\{)", 
        r"\\it(?=\s|\{)",   
        r"\\sf(?=\s|\{)", 
        r"\\tt(?=\s|\{)", 
        r"\\sl(?=\s|\{)", 
        r"\\sc(?=\s|\{)",  
        r"\\em(?=\s|\{)", 
        r"\\centerline(?=\s|\{)", 
        r"\\over(?=\s|\{)", 
        r"\\atop(?=\s|\{)"
    ]

    data = {
        "algorithms": algorithm_list,
        "formulas": formula_list,
        "tables": table_list,
        "items": item_list,
        "elses": else_list,
        "sentences": sentence_list
    }
    
    # 筛选后的数据
    filtered_data = filter_old_fashion(data, old_fashion)
    
    return filtered_data
    
    
    
    
