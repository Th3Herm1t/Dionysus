import os
import argparse
from typing import List, Optional, Tuple
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama

def get_file_info(file_name: str) -> Tuple[str, str]:
    """Determine the color and icon for a file based on its extension."""
    file_ext = os.path.splitext(file_name)[1].lower()
    
    file_types = {
        ('.py', '.pyc', '.pyo'): (Fore.YELLOW, '🐍'),
        ('.txt', '.md', '.rst'): (Fore.GREEN, '📄'),
        ('.jpg', '.png', '.gif', '.bmp'): (Fore.MAGENTA, '🖼️')
    }
    
    for extensions, (color, icon) in file_types.items():
        if file_ext in extensions:
            return color, icon
    
    return Fore.WHITE, '📄'

def print_item(name: str, level: int, is_directory: bool = False) -> None:
    """Print a directory or file with appropriate formatting."""
    indent = '  ' * level
    if is_directory:
        color = Fore.CYAN if level == 0 else Fore.BLUE
        print(f"{indent}{color}📂 {name}{Style.RESET_ALL}")
    else:
        color, icon = get_file_info(name)
        print(f"{indent}{color}{icon} {name}{Style.RESET_ALL}")

def print_directory_structure(
    startpath: str, 
    exclude_dirs: Optional[List[str]] = None, 
    max_depth: Optional[int] = None
) -> None:
    """Print the directory structure with optional depth limit."""
    if exclude_dirs is None:
        exclude_dirs = []

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, '').count(os.sep)
        
        if max_depth is not None and level >= max_depth:
            del dirs[:]
            continue

        print_item(os.path.basename(root), level, is_directory=True)
        
        for file in sorted(files):
            print_item(file, level + 1)

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Print a pretty project structure.")
    parser.add_argument("-d", "--depth", type=int, help="Maximum depth to print")
    return parser.parse_args()

def main() -> None:
    """Main function to run the script."""
    args = parse_arguments()
    current_dir = os.getcwd()
    exclude = ['venv', '__pycache__', '.git']
    max_depth = args.depth

    print(f"{Fore.GREEN}{Style.BRIGHT}Project structure for: {current_dir}{Style.RESET_ALL}")
    if max_depth is not None:
        print(f"{Fore.YELLOW}Printing to a maximum depth of {max_depth}{Style.RESET_ALL}")
    print_directory_structure(current_dir, exclude, max_depth)

if __name__ == "__main__":
    main()