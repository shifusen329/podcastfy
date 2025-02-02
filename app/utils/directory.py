"""Directory handling utilities."""

import os
import re
from typing import List, Tuple

def natural_sort_key(s: str) -> List[str]:
    """Key function for natural sorting of strings with numbers."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def get_directory_text_files(directory_path: str) -> List[str]:
    """
    Get a list of text file paths from a directory, sorted naturally.
    
    Args:
        directory_path (str): Path to directory containing text files
        
    Returns:
        List[str]: List of absolute paths to text files, sorted naturally
        
    Raises:
        ValueError: If directory doesn't exist or contains no text files
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Directory not found: {directory_path}")
    
    # Get all .txt files and sort them naturally
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    if not files:
        raise ValueError(f"No text files found in directory: {directory_path}")
    
    files.sort(key=natural_sort_key)
    
    # Return absolute paths
    return [os.path.abspath(os.path.join(directory_path, f)) for f in files]

def combine_directory_texts(directory_path: str, max_size: int = 20_000_000) -> Tuple[str, bool]:
    """
    Combine contents of text files up to max_size bytes, starting from most recent.
    Files are processed in reverse natural sort order to prioritize recent content.
    
    Args:
        directory_path (str): Path to directory containing text files
        max_size (int): Maximum size in bytes for combined content
        
    Returns:
        Tuple[str, bool]: (Combined text content, whether content was truncated)
        
    Raises:
        ValueError: If directory doesn't exist or contains no text files
    """
    file_paths = get_directory_text_files(directory_path)  # Already sorted naturally
    file_paths.reverse()  # Most recent first
    
    combined = []
    total_size = 0
    truncated = False
    
    for path in file_paths:
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
                if content:  # Only add non-empty content
                    content_size = len(content.encode('utf-8'))  # Get size in bytes
                    if total_size + content_size > max_size:
                        truncated = True
                        break
                    combined.append(content)
                    total_size += content_size
        except Exception as e:
            raise ValueError(f"Error reading file {path}: {str(e)}")
    
    return "\n\n".join(combined), truncated

def is_text_directory(path: str) -> bool:
    """
    Check if a path is a directory containing text files.
    
    Args:
        path (str): Path to check
        
    Returns:
        bool: True if path is a directory containing at least one .txt file
    """
    try:
        if not os.path.isdir(path):
            return False
        
        # Check if directory contains any .txt files
        return any(f.endswith('.txt') for f in os.listdir(path))
    except:
        return False
