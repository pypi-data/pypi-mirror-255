from typing import List, Tuple

# Custom sorting key function
def custom_sort(row: List[str], tags: List[int]) -> Tuple[int, int]:
    if int(row[0]) in tags:
        return tags.index(int(row[0])), 0  # Sort based on index in tags
    else:
        return len(tags), int(row[0])  # Sort numerically

# Sample list of rows with tags in row[0]
rows: List[List[str]] = [
    ["3", "data1"],
    ["1", "data2"],
    ["2", "data3"],
    ["5", "data4"],
    ["9", "data5"],  # Non-numeric value
    ["4", "data6"]
]

# Sample list of tags in the desired order
tags: List[int] = [3, 2, 1, 4]

# Sort the rows based on the custom sorting logic
sorted_rows = sorted(rows, key=lambda row: custom_sort(row, tags))

# Display the sorted rows
for row in sorted_rows:
    print(row)
