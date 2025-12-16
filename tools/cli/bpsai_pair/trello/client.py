"""
Trello client wrapper.
"""
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TrelloService:
    """Wrapper around the Trello API client."""

    def __init__(self, api_key: str, token: str):
        """Initialize Trello service.

        Args:
            api_key: Trello API key
            token: Trello API token
        """
        try:
            from trello import TrelloClient
            self.client = TrelloClient(api_key=api_key, token=token)
        except ImportError:
            raise ImportError(
                "py-trello is required for Trello integration. "
                "Install with: pip install py-trello"
            )
        self.board = None
        self.lists: Dict[str, Any] = {}

    def healthcheck(self) -> bool:
        """Check if the connection is working.

        Returns:
            True if connection works, False otherwise
        """
        try:
            self.client.list_boards()
            return True
        except Exception as e:
            logger.warning(f"Trello healthcheck failed: {e}")
            return False

    def list_boards(self) -> List[Any]:
        """List all accessible boards.

        Returns:
            List of Trello board objects
        """
        return self.client.list_boards()

    def set_board(self, board_id: str) -> Any:
        """Set the active board.

        Args:
            board_id: Trello board ID

        Returns:
            The board object
        """
        self.board = self.client.get_board(board_id)
        self.lists = {lst.name: lst for lst in self.board.all_lists()}
        return self.board

    def get_board_lists(self) -> Dict[str, Any]:
        """Get all lists on the current board.

        Returns:
            Dict mapping list names to list objects

        Raises:
            ValueError: If no board is set
        """
        if not self.board:
            raise ValueError("Board not set. Call set_board() first.")
        return self.lists

    def get_cards_in_list(self, list_name: str) -> List[Any]:
        """Get all cards in a list.

        Args:
            list_name: Name of the list

        Returns:
            List of card objects
        """
        lst = self.lists.get(list_name)
        if not lst:
            return []
        return lst.list_cards()

    def move_card(self, card: Any, list_name: str) -> None:
        """Move a card to a different list.

        Args:
            card: Card object to move
            list_name: Name of target list (created if doesn't exist)
        """
        target = self.lists.get(list_name)
        if not target:
            target = self.board.add_list(list_name)
            self.lists[list_name] = target
        card.change_list(target.id)

    def add_comment(self, card: Any, comment: str) -> None:
        """Add a comment to a card.

        Args:
            card: Card object
            comment: Comment text
        """
        card.comment(comment)

    def is_card_blocked(self, card: Any) -> bool:
        """Check if a card has unchecked dependencies.

        Args:
            card: Card object

        Returns:
            True if card has unchecked items in 'card dependencies' checklist
        """
        try:
            for checklist in card.checklists:
                if checklist.name.lower() == 'card dependencies':
                    for item in checklist.items:
                        if not item.get('checked', False):
                            return True
        except Exception:
            pass
        return False

    def find_card(self, card_id: str) -> tuple[Optional[Any], Optional[Any]]:
        """Find a card by ID or short ID.

        Args:
            card_id: Card ID, short ID, or TRELLO-<short_id>

        Returns:
            Tuple of (card, list) or (None, None) if not found
        """
        if not self.board:
            return None, None

        # Normalize card_id
        if card_id.startswith("TRELLO-"):
            card_id = card_id[7:]  # Remove prefix

        for lst in self.board.all_lists():
            for card in lst.list_cards():
                if (card.id == card_id or
                    str(card.short_id) == card_id):
                    return card, lst
        return None, None
