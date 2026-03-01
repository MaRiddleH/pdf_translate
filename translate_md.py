# Copyright (c) Opendatalab. All rights reserved.
import os
import re
import time
from pathlib import Path
import dashscope
from dashscope import Generation
from tqdm import tqdm
from logger_config import setup_logger, get_env_config

# 设置日志
logger = setup_logger(__name__)


def get_translate_config():
    """
    从 .env 文件读取翻译配置。

    Returns:
        dict: 包含翻译配置的字典
    """
    return {
        "api_key": os.getenv("ALIYUN_KEY"),
        "model": os.getenv("TRANSLATE_MODEL", "qwen-plus"),
        "prompt": os.getenv("TRANSLATE_PROMPT"),
        "temperature": float(os.getenv("TRANSLATE_TEMPERATURE", 0.3)),
        "max_tokens": int(os.getenv("TRANSLATE_MAX_TOKENS", 2000)),
        "max_chunk_size": int(os.getenv("MAX_CHUNK_SIZE", 3000)),
        "chunk_delay": float(os.getenv("CHUNK_DELAY", 2)),
        "file_delay": float(os.getenv("FILE_DELAY", 5)),
    }


# Read API keys from .env file
def read_api_keys():
    """
    Read API keys from .env file
    """
    env_path = Path(".env")
    if not env_path.exists():
        logger.error(f"File {env_path} does not exist.")
        return None

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        aliyun_key = None

        for line in lines:
            line = line.strip()
            if line.startswith('ALIYUN_KEY='):
                aliyun_key = line.split('=', 1)[1]

        return aliyun_key
    except UnicodeDecodeError:
        # 尝试使用 gbk 编码读取（Windows 常见）
        try:
            with open(env_path, 'r', encoding='gbk') as f:
                content = f.read()
            for line in content.splitlines():
                line = line.strip()
                if line.startswith('ALIYUN_KEY='):
                    return line.split('=', 1)[1]
        except Exception:
            pass
        logger.error(f"Failed to read {env_path} with supported encodings.")
        return None


# Translate text using Aliyun model
def translate_text(text, config):
    """
    Translate text to Chinese using Aliyun model.

    Args:
        text: Text to translate
        config: Translation configuration dict

    Returns:
        Translated text
    """
    if not text.strip():
        return text

    # 构建提示词
    prompt = f"{config['prompt']}\n\n{text}"

    try:
        response = Generation.call(
            model=config["model"],
            prompt=prompt,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"]
        )
        if response.status_code == 200:
            return response.output.text.strip()
        else:
            logger.error(f"API Error: {response.code} - {response.message}")
            return text
    except Exception as e:
        logger.exception(f"Exception during translation: {e}")
        return text


# Split markdown content into chunks while preserving structure
def split_markdown_content(content, max_chunk_size=3000):
    """
    Split markdown content into chunks while preserving structure

    Args:
        content: Markdown content to split
        max_chunk_size: Maximum size of each chunk in characters

    Returns:
        List of chunks with preserved markdown structure
    """
    chunks = []
    current_chunk = []
    current_size = 0

    # Define markdown structure patterns
    patterns = {
        'header': r'^#{1,6}\s',
        'code_block': r'^```',
        'table': r'^\|',
        'list_item': r'^\s*[*+-]\s|^\s*\d+\.\s',
        'blockquote': r'^>',
        'horizontal_rule': r'^---$|^===+$'
    }

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        line_size = len(line) + 1  # +1 for newline

        # Check if this line starts a special structure
        structure_start = None
        for struct_type, pattern in patterns.items():
            if re.match(pattern, line):
                structure_start = struct_type
                break

        # Handle special structures that need to be kept together
        if structure_start == 'code_block':
            # Code block: include until closing ```
            code_block_lines = [line]
            code_block_size = line_size
            i += 1
            while i < len(lines) and not re.match(r'^```', lines[i]):
                code_block_lines.append(lines[i])
                code_block_size += len(lines[i]) + 1
                i += 1
            if i < len(lines):
                code_block_lines.append(lines[i])
                code_block_size += len(lines[i]) + 1
                i += 1

            # Check if code block fits in current chunk
            if current_size + code_block_size <= max_chunk_size:
                current_chunk.extend(code_block_lines)
                current_size += code_block_size
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                # Add code block as a separate chunk
                chunks.append('\n'.join(code_block_lines))
                current_chunk = []
                current_size = 0

        elif structure_start == 'table':
            # Table: include until non-table line
            table_lines = [line]
            table_size = line_size
            i += 1
            while i < len(lines) and re.match(r'^\|', lines[i]):
                table_lines.append(lines[i])
                table_size += len(lines[i]) + 1
                i += 1

            # Check if table fits in current chunk
            if current_size + table_size <= max_chunk_size:
                current_chunk.extend(table_lines)
                current_size += table_size
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                # Add table as a separate chunk
                chunks.append('\n'.join(table_lines))
                current_chunk = []
                current_size = 0

        else:
            # Regular line or other structures
            if current_size + line_size <= max_chunk_size:
                current_chunk.append(line)
                current_size += line_size
                i += 1
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                # Start new chunk with current line
                current_chunk = [line]
                current_size = line_size
                i += 1

    # Add remaining content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


# Translate markdown content with chunking
def translate_markdown_with_chunking(content, config):
    """
    Translate markdown content by splitting into chunks and translating each chunk

    Args:
        content: Markdown content to translate
        config: Translation configuration dict

    Returns:
        Translated markdown content
    """
    # Split content into chunks
    chunks = split_markdown_content(content, config["max_chunk_size"])
    logger.info(f"Split content into {len(chunks)} chunks")

    # Translate each chunk
    translated_chunks = []
    for i, chunk in enumerate(tqdm(chunks, desc="Translating chunks", unit="chunk")):
        tqdm.write(f"Translating chunk {i+1}/{len(chunks)}")
        translated_chunk = translate_text(chunk, config)
        translated_chunks.append(translated_chunk)
        # Add delay between chunks to avoid rate limiting
        time.sleep(config["chunk_delay"])

    # Combine translated chunks
    translated_content = '\n'.join(translated_chunks)
    return translated_content


# Translate all markdown files under aims directory
def translate_all_md_files():
    """
    Translate all markdown files under aims directory to Chinese
    """
    # Read translation configuration
    config = get_translate_config()

    # Read API keys
    if not config["api_key"]:
        config["api_key"] = read_api_keys()

    if not config["api_key"]:
        logger.error("Failed to read API keys from .env file.")
        return

    # Set API Key
    dashscope.api_key = config["api_key"]

    logger.info(f"Using translation model: {config['model']}")
    logger.info(f"Chunk size: {config['max_chunk_size']}, Temperature: {config['temperature']}")

    # Get aims directory path
    aims_dir = Path("./aims")
    if not aims_dir.exists():
        logger.error(f"Directory {aims_dir} does not exist.")
        return

    # Delete existing files ending with _zh.md
    deleted_files = []
    for file in aims_dir.rglob("*_zh.md"):
        try:
            file.unlink()
            deleted_files.append(file.name)
        except Exception as e:
            logger.error(f"Error deleting {file}: {e}")

    if deleted_files:
        logger.info(f"Deleted {len(deleted_files)} existing translated files: {', '.join(deleted_files[:5])}{'...' if len(deleted_files) > 5 else ''}")
    else:
        logger.info("No existing translated files found to delete.")

    # Find all markdown files under aims directory, excluding those ending with _zh.md
    md_files = []
    for file in aims_dir.rglob("*.md"):
        if not file.name.endswith("_zh.md"):
            md_files.append(file)

    if not md_files:
        logger.info(f"No markdown files found under {aims_dir} that need translation.")
        return

    logger.info(f"Found {len(md_files)} markdown files to translate.")

    # Translate each markdown file with progress bar
    for md_file in tqdm(md_files, desc="Translating files", unit="file"):
        try:
            # Read file content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Translate content with chunking
            translated_content = translate_markdown_with_chunking(content, config)

            if translated_content:
                # Write translated content back to a new file with _zh suffix
                translated_file = md_file.with_name(f"{md_file.stem}_zh{md_file.suffix}")
                with open(translated_file, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                tqdm.write(f"Successfully translated {md_file.name} to {translated_file.name}")
            else:
                tqdm.write(f"Failed to translate {md_file.name}")

            # Add a delay to avoid rate limiting
            time.sleep(config["file_delay"])

        except Exception as e:
            tqdm.write(f"Error translating {md_file.name}: {str(e)}")
            logger.exception(f"Error translating {md_file}: {e}")

    logger.info("Translation process completed.")


if __name__ == "__main__":
    translate_all_md_files()
