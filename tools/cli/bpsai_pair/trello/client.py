"""
Trello client wrapper.
"""
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CustomFieldDefinition:
    """Represents a Trello custom field definition."""
    id: str
    name: str
    field_type: str  # 'text', 'number', 'checkbox', 'list', 'date'
    options: Dict[str, str]  # For list type: option_id -> option_text


@dataclass
class EffortMapping:
    """Maps complexity scores to effort values (S/M/L)."""
    small: tuple = (0, 25)
    medium: tuple = (26, 50)
    large: tuple = (51, 100)

    def get_effort(self, complexity: int) -> str:
        """Convert complexity score to S/M/L effort."""
        if complexity <= self.small[1]:
            return "S"
        elif complexity <= self.medium[1]:
            return "M"
        else:
            return "L"


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

    def find_card_with_prefix(self, prefix: str) -> tuple[Optional[Any], Optional[Any]]:
        """Find a card by prefix in title (e.g., '[TASK-001]').

        Args:
            prefix: Prefix to search for in card title

        Returns:
            Tuple of (card, list) or (None, None) if not found
        """
        if not self.board:
            return None, None

        # Format prefix with brackets if not already
        search_prefix = prefix if prefix.startswith("[") else f"[{prefix}]"

        for lst in self.board.all_lists():
            for card in lst.list_cards():
                if search_prefix in card.name:
                    return card, lst
        return None, None

    def move_card_by_task_id(self, task_id: str, target_list: str, comment: Optional[str] = None) -> bool:
        """Move a card by task ID to a target list.

        Args:
            task_id: Task ID (e.g., 'TASK-001')
            target_list: Name of target list
            comment: Optional comment to add

        Returns:
            True if card was found and moved
        """
        card, _ = self.find_card_with_prefix(task_id)
        if not card:
            return False

        self.move_card(card, target_list)

        if comment:
            self.add_comment(card, comment)

        return True

    # ========== Custom Field Methods ==========

    def get_custom_fields(self) -> List[CustomFieldDefinition]:
        """Get all custom field definitions for the current board.

        Returns:
            List of CustomFieldDefinition objects

        Raises:
            ValueError: If no board is set
        """
        if not self.board:
            raise ValueError("Board not set. Call set_board() first.")

        definitions = self.board.get_custom_field_definitions()
        result = []

        for defn in definitions:
            options = {}
            if defn.field_type == 'list':
                options = defn.list_options

            result.append(CustomFieldDefinition(
                id=defn.id,
                name=defn.name,
                field_type=defn.field_type,
                options=options
            ))

        return result

    def get_custom_field_by_name(self, name: str) -> Optional[CustomFieldDefinition]:
        """Find a custom field by name.

        Args:
            name: Name of the custom field (case-insensitive)

        Returns:
            CustomFieldDefinition or None if not found
        """
        fields = self.get_custom_fields()
        name_lower = name.lower()

        for field in fields:
            if field.name.lower() == name_lower:
                return field

        return None

    def set_custom_field_value(
        self,
        card: Any,
        field: CustomFieldDefinition,
        value: Union[str, int, float, bool]
    ) -> bool:
        """Set a custom field value on a card.

        Args:
            card: Trello card object
            field: Custom field definition
            value: Value to set (type depends on field type)

        Returns:
            True if successful
        """
        try:
            if field.field_type == 'text':
                post_args = {'value': {'text': str(value)}}
            elif field.field_type == 'number':
                post_args = {'value': {'number': str(value)}}
            elif field.field_type == 'checkbox':
                post_args = {'value': {'checked': 'true' if value else 'false'}}
            elif field.field_type == 'list':
                # Find option ID by value text
                option_id = None
                value_str = str(value)
                for opt_id, opt_text in field.options.items():
                    if opt_text.lower() == value_str.lower():
                        option_id = opt_id
                        break

                if not option_id:
                    logger.warning(f"Option '{value}' not found for field '{field.name}'")
                    return False

                post_args = {'idValue': option_id}
            elif field.field_type == 'date':
                # Expect ISO format: YYYY-MM-DDTHH:MM:SS.000Z
                post_args = {'value': {'date': str(value)}}
            else:
                logger.warning(f"Unknown field type: {field.field_type}")
                return False

            self.client.fetch_json(
                f'/card/{card.id}/customField/{field.id}/item',
                http_method='PUT',
                post_args=post_args
            )
            return True

        except Exception as e:
            logger.error(f"Failed to set custom field '{field.name}': {e}")
            return False

    def set_card_custom_fields(
        self,
        card: Any,
        field_values: Dict[str, Union[str, int, float, bool]]
    ) -> Dict[str, bool]:
        """Set multiple custom fields on a card.

        Args:
            card: Trello card object
            field_values: Dict mapping field names to values

        Returns:
            Dict mapping field names to success status
        """
        results = {}

        for field_name, value in field_values.items():
            field = self.get_custom_field_by_name(field_name)
            if not field:
                logger.warning(f"Custom field '{field_name}' not found on board")
                results[field_name] = False
                continue

            results[field_name] = self.set_custom_field_value(card, field, value)

        return results

    def set_effort_field(self, card: Any, complexity: int, field_name: str = "Effort") -> bool:
        """Set the Effort custom field based on complexity score.

        Args:
            card: Trello card object
            complexity: Complexity score (0-100)
            field_name: Name of the effort field (default: "Effort")

        Returns:
            True if successful
        """
        effort_mapping = EffortMapping()
        effort = effort_mapping.get_effort(complexity)

        field = self.get_custom_field_by_name(field_name)
        if not field:
            logger.warning(f"Effort field '{field_name}' not found on board")
            return False

        if field.field_type != 'list':
            logger.warning(f"Effort field must be a list type, got {field.field_type}")
            return False

        return self.set_custom_field_value(card, field, effort)

    def create_card_with_custom_fields(
        self,
        list_name: str,
        name: str,
        desc: str = "",
        custom_fields: Optional[Dict[str, Union[str, int, float, bool]]] = None
    ) -> Optional[Any]:
        """Create a card with custom fields.

        Args:
            list_name: Name of the list to create the card in
            name: Card name/title
            desc: Card description
            custom_fields: Dict mapping field names to values

        Returns:
            Created card object or None if failed
        """
        target_list = self.lists.get(list_name)
        if not target_list:
            logger.error(f"List '{list_name}' not found")
            return None

        try:
            card = target_list.add_card(name=name, desc=desc)

            if custom_fields:
                self.set_card_custom_fields(card, custom_fields)

            return card

        except Exception as e:
            logger.error(f"Failed to create card: {e}")
            return None

    # ========== Label Methods ==========

    def get_labels(self) -> List[Dict[str, str]]:
        """Get all labels on the current board.

        Returns:
            List of label dicts with 'id', 'name', 'color'
        """
        if not self.board:
            raise ValueError("Board not set. Call set_board() first.")

        labels = self.board.get_labels()
        return [
            {'id': lbl.id, 'name': lbl.name, 'color': lbl.color}
            for lbl in labels
        ]

    def get_label_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Find a label by name.

        Args:
            name: Label name (case-insensitive)

        Returns:
            Label dict or None if not found
        """
        labels = self.get_labels()
        name_lower = name.lower()

        for label in labels:
            if label['name'] and label['name'].lower() == name_lower:
                return label

        return None

    def create_label(self, name: str, color: str) -> Optional[Dict[str, str]]:
        """Create a label on the board.

        Args:
            name: Label name
            color: Color name (green, yellow, orange, red, purple, blue, sky, lime, pink, black)

        Returns:
            Created label dict or None if failed
        """
        if not self.board:
            raise ValueError("Board not set. Call set_board() first.")

        try:
            label = self.board.add_label(name=name, color=color)
            return {'id': label.id, 'name': label.name, 'color': label.color}
        except Exception as e:
            logger.error(f"Failed to create label: {e}")
            return None

    def ensure_label_exists(self, name: str, color: str) -> Optional[Dict[str, str]]:
        """Ensure a label exists, creating it if necessary.

        Args:
            name: Label name
            color: Color to use if creating

        Returns:
            Label dict or None if failed
        """
        existing = self.get_label_by_name(name)
        if existing:
            return existing

        return self.create_label(name, color)

    def add_label_to_card(self, card: Any, label_name: str) -> bool:
        """Add a label to a card by name.

        Args:
            card: Trello card object
            label_name: Name of the label to add

        Returns:
            True if successful
        """
        label = self.get_label_by_name(label_name)
        if not label:
            logger.warning(f"Label '{label_name}' not found")
            return False

        try:
            # Use the direct API call to add label by ID
            # (Card.add_label expects a Label object, but we have a dict)
            card.client.fetch_json(
                f'/cards/{card.id}/idLabels',
                http_method='POST',
                post_args={'value': label['id']}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add label: {e}")
            return False
