"""Directory processing utilities for Podcastfy.

This module provides functionality for processing directories of input files,
including recursive directory traversal and file type filtering.
"""

import os
from typing import List
import logging

logger = logging.getLogger(__name__)

class DirectoryProcessor:
    """Handles directory traversal and file filtering for content processing."""
    
    def __init__(self, recursive: bool = False, file_types: List[str] = None):
        """Initialize DirectoryProcessor.
        
        Args:
            recursive (bool): Whether to process subdirectories
            file_types (List[str]): List of file extensions to process (e.g. ['.pdf', '.txt'])
                                  If None, process all files
        """
        self.recursive = recursive
        # If file_types is None, process all files
        # Otherwise ensure extensions start with dot and are lowercase
        self.file_types = None if not file_types else [
            ext if ext.startswith('.') else f'.{ext}'.lower()
            for ext in file_types
        ]
    
    def process_directory(self, directory_path: str) -> List[str]:
        """Get list of files matching criteria in directory.
        
        Args:
            directory_path (str): Path to directory to process
            
        Returns:
            List[str]: List of matching file paths
            
        Raises:
            ValueError: If directory_path doesn't exist or isn't a directory
        """
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        if not os.path.isdir(directory_path):
            raise ValueError(f"Path is not a directory: {directory_path}")
            
        matching_files = []
        try:
            if self.recursive:
                for root, _, files in os.walk(directory_path):
                    matching_files.extend(self._filter_files(root, files))
            else:
                files = os.listdir(directory_path)
                matching_files.extend(self._filter_files(directory_path, files))
                
            # Sort for consistent ordering
            matching_files.sort()
            
            if not matching_files:
                logger.warning(
                    f"No matching files found in {directory_path} "
                    f"(types: {', '.join(self.file_types)})"
                )
            else:
                logger.info(
                    f"Found {len(matching_files)} matching files in {directory_path}"
                )
                
            return matching_files
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            raise
    
    def _filter_files(self, root: str, files: List[str]) -> List[str]:
        """Filter files by extension.
        
        Args:
            root (str): Directory containing the files
            files (List[str]): List of filenames to filter
            
        Returns:
            List[str]: List of full paths to matching files
        """
        matching = []
        for filename in files:
            # Skip hidden files
            if filename.startswith('.'):
                continue
                
            # If no file_types specified, accept all files
            # Otherwise check if file extension matches any in file_types
            if self.file_types is None or any(
                filename.lower().endswith(ext) for ext in self.file_types
            ):
                full_path = os.path.join(root, filename)
                if os.path.isfile(full_path):  # Verify it's a file
                    matching.append(full_path)
                    
        return matching
