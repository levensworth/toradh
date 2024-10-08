from toradh import Optional, Option


def find_user_by_id(user_id: int) -> Optional[dict]:
    """
    Simulates fetching a user from a database by their ID.

    Args:
        user_id (int): The ID of the user to fetch.

    Returns:
        Optional[dict]: A dictionary containing user information if found, otherwise None.
    """
    # Simulated user database
    users = {
        1: {"name": "Alice", "age": 30},
        2: {"name": "Bob", "age": 25},
        3: {"name": "Charlie", "age": 35},
    }

    # Fetch the user from the database
    return Option.of(users.get(user_id))


def display_user_info(user_id: int) -> None:
    """
    Displays user information based on their ID.

    Args:
        user_id (int): The ID of the user to display.
    """
    user = find_user_by_id(user_id)

    # for python > 3.10
    # match user:
    #     case Some(data):
    #         print(f"User found: Name - {data['name']}, Age - {data['age']}")

    #     case Nothing():
    #         print("User not found")

    if user.is_some():
        data = user.unwrap()
        print(f"User found: Name - {data['name']}, Age - {data['age']}")
    else:
        print("User not found")


if __name__ == "__main__":
    # Example usage
    display_user_info(1)  # User found: Name - Alice, Age - 30
    display_user_info(4)  # User not found
