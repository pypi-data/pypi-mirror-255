
def _get_link_dict(links_in_files):
    link_dict = {}
    for l in links_in_files:
        if l["id"] not in link_dict:
            link_dict[l["id"]] = []
        link_dict[l["id"]].append(l)
    return link_dict


def _get_card_dict(cards_in_boards):
    card_dict = {}
    for c in cards_in_boards:
        if c["id"] not in card_dict:
            card_dict[c["id"]] = []
        card_dict[c["id"]].append(c)
    return card_dict


def group_scan_results(scan_results):

    links_in_files = scan_results.get("linksInFiles", [])
    cards_in_boards = scan_results.get("cardsInBoards", [])

    links_by_card_id = _get_link_dict(links_in_files)
    cards_by_card_id = _get_card_dict(cards_in_boards)

    grouped_by_file = {}
    grouped_by_board = {}

    for link in links_in_files:
        file_path = link["path"]
        if file_path not in grouped_by_file:
            grouped_by_file[file_path] = {}
        card = cards_by_card_id.get(link["id"], [])
        if card:
            card = card[0]  # since the value is a list, use first entry
            grouped_by_file[file_path][link["id"]] = card

    for card in cards_in_boards:
        board_path = card["path"]
        if board_path not in grouped_by_board:
            grouped_by_board[board_path] = {}
        link = links_by_card_id.get(card["id"], [])
        if link:
            link = link[0]  # since the value is a list, use first entry
            grouped_by_board[board_path][link["id"]] = link

    return grouped_by_file, grouped_by_board
