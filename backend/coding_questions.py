QUESTIONS = [
    {
        "title": "Two Sum",
        "description": "Given an array of integers `nums` and an integer `target`, return `True` if there are two numbers in the array that add up to the `target`.",
        "function_name": "two_sum",
        "template": "def two_sum(nums, target):\n    # Your code here\n    pass",
        "tests": [
            {"input": ([2, 7, 11, 15], 9), "output": True},
            {"input": ([3, 2, 4], 6), "output": True},
            {"input": ([3, 3], 6), "output": True},
            {"input": ([3, 4, 5], 6), "output": False},
        ],
    },
    {
        "title": "Is Palindrome",
        "description": "Given a string, return `True` if it is a palindrome, otherwise return `False`.",
        "function_name": "is_palindrome",
        "template": "def is_palindrome(s):\n    # Your code here\n    pass",
        "tests": [
            {"input": ("racecar",), "output": True},
            {"input": ("hello",), "output": False},
            {"input": ("A man a plan a canal Panama",), "output": False}, # This is case sensitive
            {"input": ("madam",), "output": True},
        ],
    }
]
