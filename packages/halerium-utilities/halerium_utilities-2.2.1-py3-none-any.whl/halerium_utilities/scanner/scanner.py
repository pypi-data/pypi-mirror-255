import re
import uuid
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Union, Callable, Any

from ..board.schemas.node_types import NOTECOLORS
from ..file import read_board, read_notebook, read_text_file


class RegexLinkScanner:
    """The RegexLinkScanner class

    Class for detecting Halerium links in Python code.
    """
    allowed_link_types = ("open", "close", "output")

    def scan(self, text: str, is_notebook: bool = True) -> List[Dict]:
        """The scan method.

        Scan multiline code string and extract Halerium links.

        Parameters
        ----------
        text : str
            The multiline code string.
        is_notebook : bool, optional
            If True, output links are extracted, if False not.
            The default is True.

        Returns
        -------
        list
            List of links. Each link is a dict with the keys
            "id", "startLine", "endLine", and "type".
        """
        matches = {}
        line_number = 0
        lines = text.split("\n")

        for line in lines:
            line_number += 1

            match = self._process_line(line, is_notebook=is_notebook)

            if match is not None:
                if match["id"] not in matches:
                    matches[match["id"]] = {
                        typ: [] for typ in self.allowed_link_types}
                matches[match["id"]][match["type"]].append(line_number)

        return self._convert_matches_to_links(matches)

    def _process_line(self, line: str, is_notebook: bool) -> Union[Dict, None]:
        line = line.strip()

        # only consider commented part
        line = "#".join(line.split("#")[1:])

        if len(line) == 0:
            # don't process an empty line
            return None

        # check if the line is a match for the opening tag,
        # if so the first group is supposed to be the id
        open_match = re.search('<halerium id="(.*)">', line, re.M)
        if open_match and open_match.group(1):
            return self._postprocess_line(
                card_id=open_match.group(1),
                link_type="open")

        # check if the line is a match for the closing tag,
        # if so the first group is supposed to be the id
        close_match = re.search('</halerium id="(.*)">', line, re.M)
        if close_match and close_match.group(1):
            return self._postprocess_line(
                card_id=close_match.group(1),
                link_type="close")

        if is_notebook:  # only notebooks may have output links
            # check if the line is a match for the output link tag,
            # if so the first group is supposed to be the id
            output_match = re.search('<halerium-output id="(.*)"/>', line, re.M)
            if output_match and output_match.group(1):
                return self._postprocess_line(
                    card_id=output_match.group(1),
                    link_type="output")

        # if no match was found return None
        return None

    def _postprocess_line(self, card_id: str, link_type: str):
        # check whether type is valid
        if link_type not in self.allowed_link_types:
            return None

        # check whether link_id is valid uuid4
        try:
            card_id = str(uuid.UUID(card_id, version=4))
        except ValueError:
            card_id = None
        if not card_id:
            return None

        return {"id": card_id, "type": link_type}

    @staticmethod
    def _convert_matches_to_links(matches: Dict[str, Dict]) -> List[Dict]:
        links = []
        for card_id, match in matches.items():

            # try to match the found matches (multiple) with start and end lines
            for index, start_line in enumerate(match["open"]):
                try:
                    end_line = match["close"][index]
                    links.append(
                        {
                            "id": card_id,
                            "startLine": start_line + 1,
                            "endLine": end_line - 1,
                            "type": "code"
                        }
                    )
                # the exception handling is to not interrupt the scan in the case
                # of more open comments than close comments
                except IndexError:
                    continue

            if match.get("output", False):
                links.append(
                    {
                        "id": card_id,
                        "startLine": -1,
                        "endLine": -1,
                        "type": "output"
                    }
                )

        return links


class Scanner:
    """The Scanner class

    Class to scan directory trees and extract all links from notebooks 
    and .py files as well as all cards from boards.
    """
    notebook_pattern = "[!.~]*.ipynb"
    text_pattern = "[!.~]*.py"
    board_pattern = "[!.~]*.board"

    def __init__(self):
        self.regex_scanner = RegexLinkScanner()
    
    def scan(self, paths: List[Union[str, Path]]) -> Dict[str, List[Dict[str, Any]]]:
        """The scan method.

        Scans a list of paths and extracts the links and card of all files in the
        whole file tree of the path.
        .ipynb files are scanned as notebooks, .py files are scanned as code files,
        .board files are scanned as boards. All other files are ignored.

        Parameters
        ----------
        paths : list
            List of paths to scan.

        Returns
        -------
        dict
            Dict with two keys
            Under the "linksInFiles" key is a list of links found in notebooks and .py files.
            Each link is a dict with the keys "id", "startLine", "endLine", and "type".
            Under the "cardsInBoards" key is a list of card previews found in boards.
            Each card preview is a dict with the keys "id", "color", and "title".
        """
        if not isinstance(paths, list):
            raise TypeError("`paths` has to be a list of paths.")
        links_and_cards = self._scan(paths)
        return links_and_cards

    def _scan(self, paths: List[Union[str, Path]]) -> Dict[str, List]:
        notebook_links = self._scan_notebooks(paths)
        textfile_links = self._scan_text_files(paths)

        links_in_files = notebook_links + textfile_links

        cards_in_boards = self._scan_boards(paths)

        # join the link arrays together
        return {
            "linksInFiles": links_in_files,
            "cardsInBoards": cards_in_boards,
        }

    def _scan_notebooks(self, paths: List[Union[str, Path]]) -> List:
        return self._scan_files(self.notebook_pattern, self._scan_notebook, paths)

    def _scan_text_files(self, paths: List[Union[str, Path]]) -> List:
        return self._scan_files(self.text_pattern, self._scan_text_file, paths)

    def _scan_boards(self, paths: List[Union[str, Path]]) -> List:
        return self._scan_files(self.board_pattern, self._scan_board, paths)

    def _scan_files(self, file_pattern: str, scan_function: Callable, 
                    paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        cache = []

        for path in paths:
            path = Path(path)
            if path.is_dir():
                for filepath in path.glob("**/" + file_pattern):
                    if any([part.startswith(".") for part in filepath.parts]):
                        continue
                    results = self._scan_file(filepath, scan_function)
                    self._insert_path(results, filepath)
                    cache.extend(results)
            elif path.match(file_pattern):
                results = self._scan_file(path, scan_function)
                self._insert_path(results, path)
                cache.extend(results)

        return cache

    def _scan_file(self, path: Path, scan_function: Callable) -> List:
        try:
            results = scan_function(path)
        except Exception as exc:
            print(f"File {str(path)}")
            print("".join(traceback.format_tb(exc.__traceback__)))
            results = []
        return results

    def _insert_path(self, cache: List[Dict[str, Any]], path: Path) -> None:
        for c in cache:
            c["path"] = str(path.resolve())

    def _scan_notebook(self, filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        links = []

        notebook = read_notebook(filepath, code_format="jupyter")

        for index, cell in enumerate(notebook["cells"]):
            try:
                if cell["cell_type"] == "markdown":
                    continue
                source_text = self._merge_lines(cell["source"])
                cell_links = self.regex_scanner.scan(source_text)
                links.extend(cell_links)
            except KeyError as exc:
                print(f"File {str(filepath)}")
                print(f"Cell {index}")
                print("".join(traceback.format_tb(exc.__traceback__)))
                continue

        return links

    def _scan_text_file(self, filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        links = []

        lines = read_text_file(filepath)
        source_text = self._merge_lines(lines)

        links.extend(self.regex_scanner.scan(source_text))

        return links

    def _merge_lines(self, lines: List[str]) -> str:
        # notebook source and read_text_file output is a list of lines (with line breaks)
        # to avoid sensitivity on the presence of line breaks
        # as well as their type (windows, unix, ...)
        # we remove potentially existing line breaks with rstrip and add our own line breaks
        # and then also try to replace still existing windows line breaks by unix style line break
        # this is of course inefficient, but for most files the read io of the file itself should be
        # slower than the string manipulations
        if not isinstance(lines, list):
            raise TypeError("lines must be a list object.")

        text = [line.rstrip() for line in lines]
        text = "\n".join(text)
        text = text.replace("\r\n", "\n")
        return text

    def _scan_board(self, filepath: Union[str, Path]) -> List[Dict[str, Any]]:
        card_previews = []

        board = read_board(filepath)

        for card in board.cards:
            try:
                preview = {
                    "id": card.id,
                    "color": getattr(card.type_specific, "color", None),
                    "title": getattr(card.type_specific, "title", card.type),
                }
                card_previews.append(preview)
            except KeyError:
                continue  # skip card if it is not properly formatted

        return card_previews
