# -*- coding: utf-8 -*-
"""
@Organization : SupaVision
@Author       : 18317
@Date Created : 29/12/2023
@Description  : Refactored script to generate directory links and recently modified files.
"""
import logging
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


class GitHandler:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_recent_changes(self, num_commits: int) -> list:
        separator = "|||"
        commit_log = subprocess.check_output(
            [
                "git",
                "log",
                f"-{num_commits}",
                f"--pretty=format:%ad{separator}%an{separator}%s",
                "--date=short",
                "--name-status",
            ],
            cwd=self.repo_path,
            universal_newlines=True,
        )
        return self.parse_commit_log(commit_log, separator)

    @staticmethod
    def parse_commit_log(commit_log: str, separator: str) -> list:
        commit_changes = []
        current_commit_info = []
        for line in commit_log.splitlines():
            if separator in line:
                date, author, message = line.split(separator)
                current_commit_info = {
                    "date": date,
                    "author": author,
                    "message": message,
                    "changes": [],
                }
                commit_changes.append(current_commit_info)
            else:
                match = re.match(r"^([AMDRT])(\d+)?\t(.+?)(?:\t(.+))?$", line)
                if match and current_commit_info:
                    current_commit_info["changes"].append(match.groups())
        return commit_changes


class MarkdownFormatter:
    suffixes: list[str] = [
        ".md",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".pdf",
        ".py",
        ".yml",
        ".yaml",
        ".json",
        ".txt",
        ".csv",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".rar",
        ".docx",
        ".pptx",
        ".xlsx",
        ".doc",
        ".ppt",
        ".xls",
    ]
    omit_prefixes: list[str] = [
        "README",
        "LICENSE",
        "CONTRIBUTING",
        ".",
        "_",
        "pycache",
    ]

    def __init__(self, root_path: Path, output_file: Path):
        self.root_path = root_path
        self.output_file = output_file

    def omited_file(self, path: Path) -> bool:
        return any(path.name.startswith(prefix) for prefix in self.omit_prefixes)

    def replace_spaces_in_path(
        self, abs_path: Path, replace_with: str = "_"
    ) -> (str, str):
        """
        Replace spaces in file_path with the specified character.
        :arg abs_path: Absolute path to the file linked by the markdown link.
        :arg rel_path: Relative path to the root as the markdown link.
        """
        # return if it is  root
        if abs_path.parent == self.root_path:
            rel_path = abs_path.relative_to(self.root_path).as_posix()
            return abs_path.as_posix(), rel_path

        # get normalized path parents
        new_parent_path, _ = self.replace_spaces_in_path(abs_path.parent, replace_with)

        abs_path = Path(new_parent_path) / abs_path.name

        # normalize abs_path name
        new_abs_path = (
            abs_path.as_posix()
            .strip()
            .replace(" ", replace_with)
            .replace("%20", replace_with)
        )

        # rename if needed
        if new_abs_path != abs_path.as_posix() and not Path(new_abs_path).exists():
            try:
                abs_path.rename(new_abs_path)
                logging.info(f"Renamed '{abs_path}' to '{new_abs_path}'")
            except FileNotFoundError:
                logging.error(f"rename failed during renaming: {abs_path}")
        rel_path = Path(new_abs_path).relative_to(self.root_path).as_posix()
        return new_abs_path, rel_path

    def _valid_link(self, path: str, *, depth: int = 0) -> str:
        """
        convert path to valid link
        :param path: link path
        :return: url or rel_path to root
        """
        abs_path = self.root_path / path.strip('"')
        prefix = "../" * depth
        # http link
        if self._is_url(path):
            # pure url
            return path
        elif abs_path.exists():
            if abs_path.is_file():
                # true file
                return prefix + self.replace_spaces_in_path(abs_path)[1]
        # no exist
        else:
            abs_path = self.replace_spaces_in_path(abs_path)[0]
            file_name = Path(abs_path).stem
            # try find it in root dir
            for new_abs_path in self.root_path.rglob("*"):
                if (
                    not self.omited_file(new_abs_path)
                    and new_abs_path.stem == file_name
                ):
                    return prefix + self.replace_spaces_in_path(new_abs_path)[1]

        logging.warning(f"Invalid path: {abs_path}")
        return path

    @staticmethod
    def _is_url(path: str) -> bool:
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def _is_markdown_link(text: str) -> bool:
        """检查文本是否是标准 Markdown 链接格式"""
        markdown_link_pattern = r"\[.*?\]\(.*?\)"
        return bool(re.match(markdown_link_pattern, text))

    def convert_links(self, content: str, *, depth: int = 0) -> str:
        """
        Convert Obsidian-style and Markdown-style links to valid Markdown links.
        """
        obsidian_pattern = r"!\[\[(.+?)\]\]|\[\[(.+?)\]\]"

        def replace_obsidian(match):
            link_text = match.group(1) or match.group(2)
            parts = link_text.split("|")
            link = self._valid_link(parts[0], depth=depth)

            text = parts[1].strip() if len(parts) > 1 else link.strip()
            prefix = "!" if match.group(1) else ""
            return f"{prefix}[{text}]({link})"

        def replace_markdown(match):
            text, link = match.group(1), match.group(2)
            valid_link = self._valid_link(link, depth=depth)
            return f"[{text}]({valid_link})"

        # 先转换 Obsidian 链接
        content = re.sub(obsidian_pattern, replace_obsidian, content)

        # 再检查并转换标准 Markdown 链接
        markdown_pattern = r"\[(.*?)\]\((.*?)\)"
        content = re.sub(markdown_pattern, replace_markdown, content)

        return content

    def generate_link(self, rel_path: Path, *, name: str = "") -> str:
        """
        Generate a markdown link with the given relative path and name.
        """
        name = rel_path.name if not name else name

        rel_path = self._valid_link(rel_path.as_posix())
        return f"[{name}]({rel_path})"


class MarkdownHandler(MarkdownFormatter):
    def __init__(self, root_path: str, output_file: str = "README.md"):
        root_path = Path(root_path)
        self._check_path(root_path)
        output_file = root_path / output_file
        self._check_path(output_file)
        super().__init__(root_path, output_file)
        self.git_handler = GitHandler(root_path)
        # self.replace_spaces_in_filenames()

    def _calculate_relative_depth(self, output_file: Path) -> int:
        depth = 0
        parent = output_file.parent
        while parent != self.root_path and parent != parent.parent:
            depth += 1
            parent = parent.parent
        return depth

    def _check_path(self, path: Path | str):
        if not path.exists():
            raise FileNotFoundError(f"{path} not found!")

    def _create_links(self, path: Path, level: int = 0) -> list:
        links = []
        for item in path.iterdir():
            if (
                item.is_dir()
                and not self.omited_file(item)
                and "assets" not in item.as_posix()
            ):
                links.append(f"{'  ' * level}- **{item.name}/:**")
                links.extend(self._create_links(item, level + 1))
            elif (
                item.is_file()
                and not self.omited_file(item)
                and "assets" not in item.as_posix()
                and level > 0
            ):
                rel_path = item.relative_to(self.root_path)
                links.append(f"{'  ' * level}- {self.generate_link(rel_path)}")
        return links

    def generate_nav_links(self, title: str):
        """
        Generate navigation links
        :param title:
        """
        markdown_links = self._create_links(self.root_path)
        self._update_md_content("\n".join(markdown_links), title)

    def generate_recently_modified_from_git(self, num_commits: int, title: str):
        """
        Generate recently modified files from git changes under the target directory.
        :param num_commits:
        :param title:
        """
        commit_changes = self.git_handler.get_recent_changes(num_commits)
        # logging.info(f"Found {len(commit_changes)} commits")
        # logging.info(f"git log: {commit_changes}")
        markdown_content = self._generate_markdown_from_git_changes(commit_changes)
        # logging.info(f"markdown content: {markdown_content}")
        self._update_md_content(markdown_content, title)

    def convert_wiki_links_in_dir(self, ext=".md"):
        """
        Convert wiki-links like [[]] -> standard markdown links []()
        by git changes under root_path.
        """
        # pathlist = self.root_path.rglob(f"*{ext}")
        for path in self.root_path.rglob("*"):
            if path.is_file() and path.suffix == ext:
                self._convert_wiki_links_in_file(path)

    def _convert_wiki_links_in_file(self, file_path: Path):
        """
        Convert wiki-links in a single file to standard markdown links.
        """
        with file_path.open("r", encoding="utf-8") as file:
            content = file.read()
        depth = len(file_path.relative_to(self.root_path).parents) - 1
        converted_content = self.convert_links(content, depth=depth)

        with file_path.open("w", encoding="utf-8") as file:
            file.write(converted_content)

        logging.info(f"Converted links in {file_path}")

    def _update_md_content(self, new_content: str, header_title: str):
        """
        Update the markdown file by replacing content under the specified header title
        with new_content.
        """
        with self.output_file.open("r+", encoding="utf-8") as file:
            lines = file.readlines()
            start_index = None
            end_index = None

            # Find the start and end index for the replacement
            for i, line in enumerate(lines):
                if line.strip() == header_title:
                    start_index = i + 1
                elif (
                    start_index is not None
                    and line.startswith("## ")
                    and not line.strip() == header_title
                ):
                    end_index = i
                    break

            # Replace the content if the header title is found
            if start_index is not None:
                end_index = end_index or len(lines)
                lines[start_index:end_index] = [new_content + "\n"]

            # Write back to the file
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    def _generate_markdown_from_git_changes(self, commit_changes: list) -> str:
        status_emojis = {
            "A": "✨",  # Added
            "M": "🔨",  # Modified
            "D": "🗑️",  # Deleted
            "R": "🚚",  # Renamed
        }
        markdown_lines = []

        for commit in commit_changes:
            markdown_lines.append(
                f"### {commit['date']} by {commit['author']} - {commit['message']}"
            )
            before = len(markdown_lines)
            for change in commit["changes"]:
                status, _, file_path, renamed = change
                full_path = self.root_path / file_path
                emoji = status_emojis.get(status, "")
                rel_path = full_path.relative_to(self.root_path)

                # Handle renamed files
                if status == "R" and renamed:
                    rel_renamed = self.root_path / Path(renamed)
                    if not rel_renamed.exists():
                        logging.warning(f"Skipping {rel_renamed} for not existing")
                        continue
                    markdown_lines.append(
                        f"- {emoji} {self.generate_link(rel_renamed)} <- {full_path.name}"
                    )
                else:
                    # No need to link deleted files
                    if status != "D":
                        linked_path = f"[{rel_path.name}]({rel_path})"
                    else:
                        linked_path = rel_path.name
                    markdown_lines.append(f"- {emoji} {linked_path}")
            if len(markdown_lines) == before:
                markdown_lines.pop()
        return "\n".join(markdown_lines)


if __name__ == "__main__":
    # Example usage:
    root_dir = Path("/path/to/your/project")
    output_md = root_dir / "README.md"
    handler = MarkdownHandler(root_dir)
    handler.generate_nav_links(output_md, "docs", "## Quick Navigation")
    handler.generate_recently_modified_from_git(
        output_md, 10, "docs", "## Recently Modified"
    )
