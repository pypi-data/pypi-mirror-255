from typing import Callable
from copy import deepcopy
import numpy as np
from flatten_any_dict_iterable_or_whatsoever import set_in_original_iter
import os
from numpycythonpermutations import hash_2d_nparray

try:
    from .intercg import (
        create_normal_checknumpyarray,
        create_numpy_dict_lookup,
        get_all_intersecting,
        loop_until_all_found,
        # minus_1_to_0,
        adjust_dummy,
        # create_dict_from_np,
        create_nr_lookupdict_from_array,
        create_nr_lookupdict_with_qty,
    )

except Exception:
    from cycompi import compile_cython_code
    import os

    numpyincludefolder = np.get_include()
    pyxfile = "intercg.pyx"
    uniqueproductcythonmodule = pyxfile.split(".")[0]
    dirname = os.path.abspath(os.path.dirname(__file__))
    pyxfile_complete_path = os.path.join(dirname, pyxfile)
    optionsdict = {
        "Options.docstrings": False,
        "Options.embed_pos_in_docstring": False,
        "Options.generate_cleanup_code": False,
        "Options.clear_to_none": True,
        "Options.annotate": True,
        "Options.fast_fail": False,
        "Options.warning_errors": False,
        "Options.error_on_unknown_names": True,
        "Options.error_on_uninitialized": True,
        "Options.convert_range": True,
        "Options.cache_builtins": True,
        "Options.gcc_branch_hints": True,
        "Options.lookup_module_cpdef": False,
        "Options.embed": False,
        "Options.cimport_from_pyx": False,
        "Options.buffer_max_dims": 8,
        "Options.closure_freelist_size": 8,
    }
    configdict = {
        "py_limited_api": False,
        "name": uniqueproductcythonmodule,
        "sources": [pyxfile_complete_path],
        "include_dirs": [numpyincludefolder],
        "define_macros": [
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
            ("CYTHON_USE_DICT_VERSIONS", 1),
            ("CYTHON_FAST_GIL", 1),
            ("CYTHON_USE_PYLIST_INTERNALS", 1),
            ("CYTHON_USE_UNICODE_INTERNALS", 1),
            ("CYTHON_ASSUME_SAFE_MACROS", 1),
            ("CYTHON_USE_TYPE_SLOTS", 1),
            ("CYTHON_USE_PYTYPE_LOOKUP", 1),
            ("CYTHON_USE_ASYNC_SLOTS", 1),
            ("CYTHON_USE_PYLONG_INTERNALS", 1),
            ("CYTHON_USE_UNICODE_WRITER", 1),
            ("CYTHON_UNPACK_METHODS", 1),
            ("CYTHON_USE_EXC_INFO_STACK", 1),
            ("CYTHON_ATOMICS", 1),
        ],
        "undef_macros": [],
        "library_dirs": [],
        "libraries": [],
        "runtime_library_dirs": [],
        "extra_objects": [],
        "extra_compile_args": ["/O2", "/Oy", "/openmp", "/std:c++20"],
        "extra_link_args": [],
        "export_symbols": [],
        "swig_opts": [],
        "depends": [],
        "language": "c++",
        "optional": None,
    }
    compiler_directives = {
        "binding": True,
        "boundscheck": False,
        "wraparound": False,
        "initializedcheck": False,
        "nonecheck": False,
        "overflowcheck": False,
        "overflowcheck.fold": False,
        "embedsignature": False,
        "embedsignature.format": "c",  # (c / python / clinic)
        "cdivision": True,
        "cdivision_warnings": False,
        "cpow": True,
        "always_allow_keywords": False,
        "c_api_binop_methods": False,
        "profile": False,
        "linetrace": False,
        "infer_types": True,
        "language_level": "3str",  # (2/3/3str)
        "c_string_type": "bytes",  # (bytes / str / unicode)
        "c_string_encoding": "ascii",  # (ascii, default, utf-8, etc.)
        "type_version_tag": False,
        "unraisable_tracebacks": True,
        "iterable_coroutine": False,
        "annotation_typing": False,
        "emit_code_comments": False,
        "cpp_locals": False,
        "legacy_implicit_noexcept": False,
        "optimize.use_switch": True,
        "optimize.unpack_method_calls": True,
        "warn.undeclared": False,  # (default False)
        "warn.unreachable": True,  # (default True)
        "warn.maybe_uninitialized": False,  # (default False)
        "warn.unused": False,  # (default False)
        "warn.unused_arg": False,  # (default False)
        "warn.unused_result": False,  # (default False)
        "warn.multiple_declarators": True,  # (default True)
        "show_performance_hints": True,  # (default True)
    }

    compile_cython_code(
        name=uniqueproductcythonmodule,
        configdict=configdict,
        optionsdict=optionsdict,
        cmd_line_args=compiler_directives,
        cwd=dirname,
        shell=True,
        env=os.environ.copy(),
    )
    from .intercg import (
        create_normal_checknumpyarray,
        create_numpy_dict_lookup,
        get_all_intersecting,
        loop_until_all_found,
        # minus_1_to_0,
        adjust_dummy,
        # create_dict_from_np,
        create_nr_lookupdict_from_array,
        create_nr_lookupdict_with_qty,
    )


def create_lookup_dicts(list_of_arrays):
    """
    Creates lookup dictionaries from a list of arrays.

    Parameters:
    - list_of_arrays: a list of arrays

    Returns:
    - lookupdict1: the first lookup dictionary
    - lookupdict2: the second lookup dictionary
    """
    lookupdict1 = {}
    lookupdict2 = {}
    indexcount = 0
    for lx in list_of_arrays:
        indexcount = create_nr_lookupdict_from_array(
            lx, lookupdict1, lookupdict2, indexcount
        )
    return lookupdict1, lookupdict2


def create_nr_lookupdict_with_quanty(list_of_arrays):
    """
    Create a lookup dictionary with quantities and return the dictionaries along with id counter and numpy data type.
    """
    lookupdict1 = {}
    lookupdict2 = {}
    lookupdict3 = {0: 0}
    idcounter = 0
    for lx in list_of_arrays:
        idcounter = create_nr_lookupdict_with_qty(
            lx, lookupdict1, lookupdict2, lookupdict3, idcounter
        )
    if idcounter < 256 // 2:
        numpydtype = np.int8
    elif idcounter < 65536 // 2:
        numpydtype = np.int16

    elif idcounter < 4294967296 // 2:
        numpydtype = np.int32
    else:
        numpydtype = np.int64
    return lookupdict1, lookupdict2, lookupdict3, idcounter, numpydtype


def generate_product(
    args: list[list | tuple | np.ndarray] | np.ndarray[np.ndarray],
    str_format_function: Callable = repr,
    dummyval: str = "DUMMYVAL",
):
    """
    A function that takes in a list of lists or numpy arrays, a string formatting function, and a dummy value.
    It performs several operations on the input data and returns a tuple containing various processed data and dictionaries.
    """
    argscpy = deepcopy(args)
    specialdict = {}
    for rl1 in range(len(argscpy)):
        suli = argscpy[rl1]
        for rl2 in range(len(suli)):
            v = suli[rl2]
            try:
                _ = hash(v)
            except Exception:
                v = str_format_function(v)
                args[rl1][rl2] = v
                specialdict[v] = suli[rl2]
    original_lookup_list_passed = []
    longest_array = 0
    smallest_array = 9999999
    for x in args:
        if longest_array < len(x):
            longest_array = len(x)
        if smallest_array > len(x):
            smallest_array = len(x)
        for y in x:
            original_lookup_list_passed.append(((str_format_function(y)), y))
    original_lookup_dict_passed = dict(original_lookup_list_passed)
    all_lists = []
    for ax in args:
        if smallest_array < longest_array:
            dummylist = [dummyval] * (longest_array - len(ax))
            all_lists.append(ax + dummylist)
        else:
            all_lists.append(ax)
    allarras = [longest_array for x in range(len(args))]
    argscopy = deepcopy(all_lists)
    flattend = []
    for rl1 in range(len(argscopy)):
        suli = argscopy[rl1]
        for rl2 in range(len(suli)):
            v = suli[rl2]
            try:
                hash(v)
            except Exception:
                v = str_format_function(v)
            flattend.append((v, (rl1, rl2)))

    repruniqueid = {}
    repruniqueidv = {}
    repruniquerepr = {}
    ordered_in_one_list_id = []
    ordered_in_one_list_original = []
    idcounter = 0

    for repri, keys in flattend:
        try:
            if repri not in repruniquerepr:
                repruniquerepr[repri] = original_lookup_dict_passed.get(
                    str_format_function(repri)
                )
                repruniqueid[repri] = idcounter
                repruniqueidv[idcounter] = repri
                ordered_in_one_list_id.append(idcounter)
                ordered_in_one_list_original.append(repruniquerepr[repri])
                try:
                    ordered_in_one_list_original[-1] = specialdict[repri]
                except Exception:
                    pass

                idcounter += 1
        except Exception:
            repri = str(repri)
            repruniquerepr[repri] = original_lookup_dict_passed.get(
                str_format_function(repri)
            )
            repruniqueid[repri] = idcounter
            repruniqueidv[idcounter] = repri
            ordered_in_one_list_id.append(idcounter)
            ordered_in_one_list_original.append(repruniquerepr[repri])
            idcounter += 1

        try:
            set_in_original_iter(
                iterable=argscopy, keys=keys, value=repruniqueid[repri]
            )
        except Exception:
            pass
    if idcounter < 256 // 2:
        numpydtype = np.int8
    elif idcounter < 65536 // 2:
        numpydtype = np.int16

    elif idcounter < 4294967296 // 2:
        numpydtype = np.int32
    else:
        numpydtype = np.int64
    return (
        idcounter,
        longest_array,
        numpydtype,
        numpydtype,
        repruniqueid,
        repruniqueidv,
        repruniquerepr,
        ordered_in_one_list_id,
        ordered_in_one_list_original,
        argscopy,
        all_lists,
        original_lookup_dict_passed,
        allarras,
    )


def find_intersection_of_lists(
    list_: list[list | tuple | np.ndarray] | np.ndarray[np.ndarray], debug=False
) -> dict:
    r"""
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
    """
    allnparrays = np.all([isinstance(x, np.ndarray) for x in list_])
    if not allnparrays:
        (
            idcounter,
            longest_array,
            numpydtype,
            numpydtype,
            repruniqueid,
            repruniqueidv,
            repruniquerepr,
            ordered_in_one_list_id,
            ordered_in_one_list_original,
            argscopy,
            all_lists,
            original_lookup_dict_passed,
            allarras,
        ) = generate_product(
            args=list_,
            str_format_function=repr,
            dummyval="DUMMYVAL",
        )
        lookupnumpyarray = np.array(argscopy, dtype=numpydtype)
        dummyindex = repruniqueid["DUMMYVAL"]
        allnumpyarrayshash = []
    else:
        allnumpyarrayshash = [hash_2d_nparray(x) for x in list_]
        maxw = np.max([x.shape[0] for x in allnumpyarrayshash])
        idcounter = 0
        allarra = np.vstack(
            [
                np.concatenate([x, np.full((maxw - x.shape[0]), -1, dtype=np.int64)])
                for x in allnumpyarrayshash
            ]
        )
        lookupnumpyarray = np.full((len(allarra), maxw), -1, dtype=np.int64)
        idcounter = np.zeros(1, dtype=np.int32)
        lookuparray = np.full((np.prod(allarra.shape), 3), -1, dtype=np.int64)
        dummyindex = create_numpy_dict_lookup(
            lookupnumpyarray, allarra, idcounter, lookuparray
        )
        idcounter = idcounter[0]
        repruniqueidv = {}
        for x in range(idcounter):
            if lookuparray[x][2] != dummyindex:
                repruniqueidv[lookuparray[x][2]] = list_[lookuparray[x][0]][
                    lookuparray[x][1]
                ]

    checknumpyarray = np.full((lookupnumpyarray.shape[0], idcounter), -1, dtype=np.int8)
    create_normal_checknumpyarray(lookupnumpyarray, dummyindex, checknumpyarray)
    allintersectinglists = np.full(
        ((lookupnumpyarray.shape[0]), (lookupnumpyarray.shape[0])), -1, dtype=np.int64
    )
    intersectionqty = np.full((lookupnumpyarray.shape[0]), 0, dtype=np.int64)
    newtotalvalues = np.full((lookupnumpyarray.shape[0]), 0, dtype=np.int64)
    get_all_intersecting(
        checknumpyarray, allintersectinglists, intersectionqty, newtotalvalues
    )

    oldtotalvalues = np.full((lookupnumpyarray.shape[0]), -1, dtype=np.int64)
    directintersections = allintersectinglists.copy()
    while np.all(oldtotalvalues != newtotalvalues):
        oldtotalvalues = newtotalvalues.copy()
        loop_until_all_found(allintersectinglists, newtotalvalues)
    adjust_dummy(lookupnumpyarray, dummyindex)
    for y in range(lookupnumpyarray.shape[0]):
        for x in range(lookupnumpyarray.shape[1]):
            if lookupnumpyarray[y][x] == dummyindex:
                lookupnumpyarray[y][x] = -1

    intersectionsnested = {}
    for x in range(len(allintersectinglists)):
        intersectionsnested[x] = allintersectinglists[x][
            np.where(allintersectinglists[x] != -1)[0]
        ]
    directintersectionsdict = {}
    for x in range(len(directintersections)):
        directintersectionsdict[x] = directintersections[x][
            np.where(directintersections[x] != -1)[0]
        ]
    return {
        "direct_intersections": directintersectionsdict,
        "nested_intersections": allintersectinglists,
        "qty_of_intersections": {k: v for k, v in enumerate(intersectionqty)},
        "arrays_with_id": lookupnumpyarray,
        "different_values": idcounter,
        "mapped_ids": repruniqueidv,
    }
