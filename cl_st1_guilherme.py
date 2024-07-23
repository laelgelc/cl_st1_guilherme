# Corpus Linguistics - Study 1 - Guilherme

## Prerequisites

#Make sure the prerequisites in [CL_LMDA_prerequisites](https://github.com/laelgelc/laelgelc/blob/main/CL_LMDA_prerequisites.ipynb) are satisfied.

### Additional prerequisites

#### WebVTT

#`webvtt-py` is a Python package for reading/writing WebVTT caption files.

#Please refer to:
#- [webvtt-py](https://pypi.org/project/webvtt-py/)

##### Installing `webvtt-py` on Anacoda Distribution

#As `webvtt-py` is not available in any of the conda channels, the following procedure should be followed on `Anaconda Prompt` to install it in the required environment, in this case `Env20240401`:

#Note:
#- You have to download and open this Jupyter Notebook on JupyterLab (provided as part of Anaconda Distribution) to visualise the procedure
#- Replace `Env20240401` by your actual environment name

#(base) C:\Users\eyamr>conda env list
# conda environments:
#
#base                  *  C:\Users\eyamr\anaconda3
#Env20240401              C:\Users\eyamr\anaconda3\envs\Env20240401


#(base) C:\Users\eyamr>conda activate Env20240401

#(Env20240401) C:\Users\eyamr>pip3 install webvtt-py
#<omitted>

#(Env20240401) C:\Users\eyamr>pip3 freeze
#<omitted>
#webvtt-py==0.5.0
#<omitted>

#(Env20240401) C:\Users\eyamr>conda deactivate

#(base) C:\Users\eyamr>

## WebVTT proof of concept

#Please refer to:
#- [CL_webvtt-py_Extraction](https://github.com/laelgelc/laelgelc/blob/main/CL_webvtt-py_Extraction.ipynb)

## Dataset

#Please download the following dataset (Right-click on the link and choose `Save link as` to download the corresponding file):
#- [cl_st1_guilherme-dataset.zip](https://laelgelcguilherme.s3.sa-east-1.amazonaws.com/cl_st1_guilherme-dataset.zip)

#Extract the .zip file in the directory where this Jupyter Notebook is being executed.

## Importing the required libraries

import webvtt
import pandas as pd
import demoji
import re
import os

## Data wrangling

### Defining the input and output directory names

input_directory = 'cl_st1_guilherme-dataset'
output_directory = input_directory + '-output'

### Defining a function to extract caption texts

def extract_caption_text(webvtt_file, caption_file):
    vtt = webvtt.read(webvtt_file)
    
    # Writing the text of the caption to the output file
    with open(caption_file, 'w', encoding='utf-8') as f:
        f.write('text' + '\n') # Includes the header that will be used in the dataframe
        for caption in vtt:
            f.write(caption.text + '\n')
    
    # Deduplicating the text of the caption using a dataframe
    df = pd.read_table(caption_file)
    df['text'] = df['text'].map(str)
    df.drop_duplicates(subset='text', keep='first', inplace=True)
    df = df.reset_index(drop=True)
    
    # Creating a single string containing all 'text' values separated by spaces
    text_line = ' '.join(df['text'])

    # Rewriting the output file with the single string
    with open(caption_file, 'w', encoding='utf-8') as f:
        f.write(text_line)

### Defining a function to recursively process the `input_directory` and store the results in `output_directory`

def process_directory(input_directory, output_directory):
    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith('.vtt'):
                # Constructing the corresponding caption filename
                base_name = os.path.splitext(filename)[0]
                caption_filename = base_name + '.txt'

                # Creating the output subdirectory structure
                relative_path = os.path.relpath(root, input_directory)
                output_subdir = os.path.join(output_directory, relative_path)
                os.makedirs(output_subdir, exist_ok=True)

                # Full paths for input and output files
                input_file_path = os.path.join(root, filename)
                output_file_path = os.path.join(output_subdir, caption_filename)

                # Calling 'extract_caption_text' function
                extract_caption_text(input_file_path, output_file_path)

### Processing the dataset

process_directory(input_directory, output_directory)

### Importing the texts into a dataframe

def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f'Error reading file {file_path}: {e}')
        return None

def process_output_directory(output_directory):
    # Initialize an empty list to store data
    data = []

    # Recursively iterate through the output_directory
    for root, _, files in os.walk(output_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_contents = read_file_contents(file_path)
            if file_contents is not None:
                data.append({'text': file_contents, 'filepath': file_path})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    return df

# Importing the texts into the dataframe 'df_tweets_filtered'. Even though this study does not relate to 'tweets', this dataframe name is adopted in order to enable code reuse in subsequent processing stages
df_tweets_filtered = process_output_directory(output_directory)

df_tweets_filtered

### Exporting the filtered data into a file for inspection

df_tweets_filtered.to_csv('tweets_emojified.tsv', sep='\t', index=False)

## Replacing emojis

### Demojifying the column `text`

# Defining a function to demojify a string
def demojify_line(input_line):
    demojified_line = demoji.replace_with_desc(input_line, sep='<em>')
    return demojified_line

df_tweets_filtered['text'] = df_tweets_filtered['text'].apply(demojify_line)

#### Exporting the filtered data into a file for inspection

df_tweets_filtered.to_csv('tweets_demojified1.tsv', sep='\t', index=False)

### Separating the demojified strings with spaces

# Defining a function to separate the demojified strings with spaces
def preprocess_line(input_line):
    # Add a space before the first delimiter '<em>', if it is not already preceded by one
    preprocessed_line = re.sub(r'(?<! )<em>', ' <em>', input_line)
    # Add a space after the first delimiter '<em>', if it is not already followed by one
    preprocessed_line = re.sub(r'<em>(?! )', '<em> ', preprocessed_line)
    return preprocessed_line

# Separating the demojified strings with spaces
df_tweets_filtered['text'] = df_tweets_filtered['text'].apply(preprocess_line)

#### Exporting the filtered data into a file for inspection

df_tweets_filtered.to_csv('tweets_demojified2.tsv', sep='\t', index=False)

### Formatting the demojified strings

# Defining a function to format the demojified string
def format_demojified_string(input_line):
    # Defining a function to format the demojified string using RegEx
    def process_demojified_string(s):
            # Lowercase the string
            s = s.lower()
            # Replace spaces and colons followed by a space with underscores
            s = re.sub(r'(: )| ', '_', s)
            # Add the appropriate prefixes and suffixes
            s = f'EMOJI{s}e'
            return s

    # Use RegEx to find and process each demojified string
    processed_line = re.sub(r'<em>(.*?)<em>', lambda match: process_demojified_string(match.group(1)), input_line)
    return processed_line

# Formatting the demojified strings
df_tweets_filtered['text'] = df_tweets_filtered['text'].apply(format_demojified_string)

### Replacing the `pipe` character by the `-` character in the `text` column

#Further on, a few columns of the dataframe are going to be exported into the file `tweets.txt` whose columns need to be delimited by the `pipe` character. Therefore, it is recommended that any occurrences of the `pipe` character in the `text` column are replaced by another character.

# Defining a function to replace the 'pipe' character by the '-' character
def replace_pipe_with_hyphen(input_string):
    modified_string = re.sub(r'\|', '-', input_string)
    return modified_string

# Replacing the 'pipe' character by the '-' character
df_tweets_filtered['text'] = df_tweets_filtered['text'].apply(replace_pipe_with_hyphen)


#### Exporting the filtered data into a file for inspection

df_tweets_filtered.to_csv('tweets_demojified3.tsv', sep='\t', index=False)

## Tokenising

#Please refer to [What is tokenization in NLP?](https://www.analyticsvidhya.com/blog/2020/05/what-is-tokenization-nlp/).

# Defining a function to tokenise a string
def tokenise_string(input_line):
    # Replace URLs with placeholders
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\b'
    placeholder = '<URL>'  # Choose a unique placeholder
    urls = re.findall(url_pattern, input_line)
    tokenised_line = re.sub(url_pattern, placeholder, input_line)  # Replace URLs with placeholders
    
    # Replace curly quotes with straight ones
    tokenised_line = tokenised_line.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    # Separate common punctuation marks with spaces
    tokenised_line = re.sub(r'([.\!?,"\'/()])', r' \1 ', tokenised_line)
    # Add a space before '#'
    tokenised_line = re.sub(r'(?<!\s)#', r' #', tokenised_line)  # Add a space before '#' if it is not already preceded by one
    # Reduce extra spaces by a single space
    tokenised_line = re.sub(r'\s+', ' ', tokenised_line)
    
    # Replace the placeholders with the respective URLs
    for url in urls:
        tokenised_line = tokenised_line.replace(placeholder, url, 1)
    
    return tokenised_line

# Tokenising the strings
df_tweets_filtered['text'] = df_tweets_filtered['text'].apply(tokenise_string)

## Creating the files `file_index.txt` and `tweets.txt`

### Creating column `text_id`

df_tweets_filtered['text_id'] = 't' + df_tweets_filtered.index.astype(str).str.zfill(6)

### Creating column `conversation`

df_tweets_filtered['conversation'] = 'v:' + df_tweets_filtered['filepath']

#### Replacing space by the `_` character

#**Important**: Since the strings in the original columns contain spaces, Pandas creates `file_index.txt` with the columns enclosed with `"` - this caracter causes issues in `examples.sh` when it is executed. Therefore, spaces should be replaced by another character such as underscore.

# Defining a function to replace space by the '_' character
def replace_space_with_underscore(input_string):
    modified_string = re.sub(r' ', '_', input_string)
    return modified_string

# Replacing space by the '_' character
df_tweets_filtered['conversation'] = df_tweets_filtered['conversation'].apply(replace_space_with_underscore)

### Creating column `date`

#The date for all texts are defined as the date Guilherme sent the dataset, 16th April, 2024.

df_tweets_filtered['date'] = 'd:' + '2024-04-16'

### Creating column `text_url`

#No URL was considered for all texts.

df_tweets_filtered['text_url'] = 'url:' + 'no_url'

### Creating column `user`

#`silas_malafaia` was considered for all texts.

df_tweets_filtered['user'] = 'u:' + 'silas_malafaia'

### Creating column `content`

df_tweets_filtered['content'] = 'c:' + df_tweets_filtered['text']

### Reordering the created columns

#Please refer to:
#- [Python - List Comprehension 1](https://www.w3schools.com/python/python_lists_comprehension.asp)
#- [Python - List Comprehension 2](https://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/)

# Reorder the columns (we use list comprehension to create a list of all columns except 'text_id', 'variable', 'date' and 'text_url')
df_tweets_filtered = df_tweets_filtered[['text_id', 'conversation', 'date', 'text_url', 'user', 'content'] + [col for col in df_tweets_filtered.columns if col not in ['text_id', 'conversation', 'date', 'text_url', 'user', 'content']]]

df_tweets_filtered

### Creating the file `file_index.txt`

df_tweets_filtered[['text_id', 'conversation', 'date', 'text_url']].to_csv('file_index.txt', sep=' ', index=False, header=False, encoding='utf-8', lineterminator='\n')

### Creating the file `tweets.txt`

folder = 'tweets'
try:
    os.mkdir(folder)
    print(f'Folder {folder} created!')
except FileExistsError:
    print(f'Folder {folder} already exists')

#Note: The parameters `doublequote=False` and `escapechar=' '` are required to avoid that the column content is doublequoted with '"' in sentences that use characters that need to be escaped such as double quote '"' itself - this causes a malformed response from TreeTagger.

df_tweets_filtered[['text_id', 'conversation', 'date', 'user', 'content']].to_csv(f'{folder}/tweets.txt', sep='|', index=False, header=False, encoding='utf-8', lineterminator='\n', doublequote=False, escapechar=' ')
