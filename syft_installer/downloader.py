import hashlib
import os
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

import requests
from rich.progress import Progress, DownloadColumn, TransferSpeedColumn

from syft_installer.exceptions import DownloadError, PlatformError
from syft_installer.platform import get_binary_url


class Downloader:
    """Handle binary downloads and installation."""
    
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.session = requests.Session()
    
    def download_and_install(self, target_path: Path) -> None:
        """
        Download and install SyftBox binary.
        
        Args:
            target_path: Where to install the binary
        """
        # Get download URL for current platform
        url = get_binary_url()
        
        # Create target directory
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download tarball
            tarball_path = Path(temp_dir) / "syftbox.tar.gz"
            self._download_file(url, tarball_path)
            
            # Extract binary
            binary_path = self._extract_binary(tarball_path, temp_dir)
            
            # Install binary
            self._install_binary(binary_path, target_path)
    
    def _download_file(self, url: str, dest: Path) -> None:
        """Download file with progress bar."""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            
            # Use rich progress bar if available and in terminal
            if os.isatty(sys.stdout.fileno()):
                with Progress(
                    "[progress.description]{task.description}",
                    DownloadColumn(),
                    TransferSpeedColumn(),
                ) as progress:
                    task = progress.add_task("Downloading", total=total_size)
                    
                    with open(dest, "wb") as f:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))
            else:
                # Simple download without progress
                with open(dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            
        except requests.exceptions.RequestException as e:
            raise DownloadError(f"Failed to download binary: {str(e)}")
    
    def _extract_binary(self, tarball_path: Path, extract_dir: str) -> Path:
        """Extract binary from tarball."""
        try:
            with tarfile.open(tarball_path, "r:gz") as tar:
                tar.extractall(extract_dir)
            
            # The tarball extracts to a directory named like syftbox_client_darwin_amd64
            # Inside that directory is the syftbox binary
            extract_path = Path(extract_dir)
            
            # Find the extracted directory (should be only one)
            for item in extract_path.iterdir():
                if item.is_dir():
                    # Look for syftbox binary inside the directory
                    binary_path = item / "syftbox"
                    if binary_path.exists() and binary_path.is_file():
                        return binary_path
            
            # Fallback: look for syftbox binary directly in extract_dir
            direct_binary = extract_path / "syftbox"
            if direct_binary.exists() and direct_binary.is_file():
                return direct_binary
            
            raise DownloadError("Binary not found in tarball")
            
        except Exception as e:
            if "Binary not found" in str(e):
                raise
            raise DownloadError(f"Failed to extract binary: {str(e)}")
    
    def _install_binary(self, source: Path, dest: Path) -> None:
        """Install binary to target location."""
        try:
            # Copy binary
            import shutil
            shutil.copy2(source, dest)
            
            # Make executable
            os.chmod(dest, 0o755)
            
        except Exception as e:
            raise DownloadError(f"Failed to install binary: {str(e)}")
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_checksum