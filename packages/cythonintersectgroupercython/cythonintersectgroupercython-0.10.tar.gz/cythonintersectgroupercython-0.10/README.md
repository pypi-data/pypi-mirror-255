# finds direct and nested intersections of lists 

## pip install cythonintersectgroupercython

### Tested against Windows 10 / Python 3.11 / Anaconda 

### Important!

The module will be compiled when you import it for the first time. Cython and a C/C++ compiler must be installed!

```python
Find the intersection of the input lists and numpy arrays and return a dictionary containing
the direct intersections, nested intersections, quantity of intersections, arrays with ID,
different values, mapped IDs, hashes, and check numpy array.

Parameters:
- list_: The input list of lists or numpy arrays
- debug: A flag to enable debugging (default: False)

Returns:
A dictionary containing the following keys:
- direct_intersections: A dictionary containing the direct intersections of the input lists and numpy arrays
- nested_intersections: An array containing the nested intersections of the input lists and numpy arrays
- qty_of_intersections: A dictionary containing the quantity of intersections for each input list or numpy array
- arrays_with_id: An array containing the arrays with ID
- different_values: The count of different values
- mapped_ids: A dictionary containing the mapped IDs
from cythonintersectgroupercython import find_intersection_of_lists
list_ = [
[5, 3, 4, 5],
[5, 11, 12, 3],
[52, 34],
[34, 111, 112],
[1000, 300],
[300, 5000],
]
inters=find_intersection_of_lists(list_)
print(inters)

# {
#     "direct_intersections": {
#         0: array([1], dtype=int64),
#         1: array([0], dtype=int64),
#         2: array([3], dtype=int64),
#         3: array([2], dtype=int64),
#         4: array([5], dtype=int64),
#         5: array([4], dtype=int64),
#     },
#     "nested_intersections": array(
#         [
#             [0, 1, -1, -1, -1, -1],
#             [0, 1, -1, -1, -1, -1],
#             [-1, -1, 2, 3, -1, -1],
#             [-1, -1, 2, 3, -1, -1],
#             [-1, -1, -1, -1, 4, 5],
#             [-1, -1, -1, -1, 4, 5],
#         ],
#         dtype=int64,
#     ),
#     "qty_of_intersections": {0: 2, 1: 2, 2: 1, 3: 1, 4: 1, 5: 1},
#     "arrays_with_id": array(
#         [
#             [0, 1, 2, 0],
#             [0, 3, 4, 1],
#             [5, 6, -1, -1],
#             [6, 8, 9, -1],
#             [10, 11, -1, -1],
#             [11, 12, -1, -1],
#         ],
#         dtype=int8,
#     ),
#     "different_values": 13,
#     "mapped_ids": {
#         0: 5,
#         1: 3,
#         2: 4,
#         3: 11,
#         4: 12,
#         5: 52,
#         6: 34,
#         7: "DUMMYVAL",
#         8: 111,
#         9: 112,
#         10: 1000,
#         11: 300,
#         12: 5000,
#     },
# }


list_ = [
[5, 3, 4, 5],
[5, 11, 12, 3],
[52, 34],
[34, 111, 112],
[1000, 300, 34],
[300, 5000],
]
inters = find_intersection_of_lists(list_)
print(inters)


# {
#     "direct_intersections": {
#         0: array([1], dtype=int64),
#         1: array([0], dtype=int64),
#         2: array([3, 4], dtype=int64),
#         3: array([2, 4], dtype=int64),
#         4: array([2, 3, 5], dtype=int64),
#         5: array([4], dtype=int64),
#     },
#     "nested_intersections": array(
#         [
#             [0, 1, -1, -1, -1, -1],
#             [0, 1, -1, -1, -1, -1],
#             [-1, -1, 2, 3, 4, 5],
#             [-1, -1, 2, 3, 4, 5],
#             [-1, -1, 2, 3, 4, 5],
#             [-1, -1, 2, 3, 4, 5],
#         ],
#         dtype=int64,
#     ),
#     "qty_of_intersections": {0: 2, 1: 2, 2: 2, 3: 2, 4: 3, 5: 1},
#     "arrays_with_id": array(
#         [
#             [0, 1, 2, 0],
#             [0, 3, 4, 1],
#             [5, 6, -1, -1],
#             [6, 8, 9, -1],
#             [10, 11, 6, -1],
#             [11, 12, -1, -1],
#         ],
#         dtype=int8,
#     ),
#     "different_values": 13,
#     "mapped_ids": {
#         0: 5,
#         1: 3,
#         2: 4,
#         3: 11,
#         4: 12,
#         5: 52,
#         6: 34,
#         7: "DUMMYVAL",
#         8: 111,
#         9: 112,
#         10: 1000,
#         11: 300,
#         12: 5000,
#     },
# }

```