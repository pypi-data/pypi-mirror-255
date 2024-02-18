from cython.parallel cimport prange
cimport openmp
import numpy as np
cimport numpy as np
import cython
cimport cython
from libcpp.unordered_map cimport unordered_map
from cython.operator cimport dereference, postincrement

ctypedef fused realfull:
    cython.char
    cython.schar
    cython.uchar
    cython.short
    cython.ushort
    cython.int
    cython.uint
    cython.long
    cython.ulong
    cython.longlong
    cython.ulonglong
    cython.size_t
    cython.Py_ssize_t

ctypedef fused fordict1:
    cython.char
    cython.schar
    cython.uchar
    cython.short
    cython.ushort
    cython.int
    cython.uint
    cython.long
    cython.ulong
    cython.longlong
    cython.ulonglong
    cython.size_t
    cython.Py_ssize_t
    cython.float
    cython.double
    cython.Py_UCS4

ctypedef fused fordict2:
    cython.char
    cython.schar
    cython.uchar
    cython.short
    cython.ushort
    cython.int
    cython.uint
    cython.long
    cython.ulong
    cython.longlong
    cython.ulonglong
    cython.size_t
    cython.Py_ssize_t
    cython.float
    cython.double
    cython.Py_UCS4

cpdef Py_ssize_t create_nr_lookupdict_with_qty(
fordict1[:] allarra,
dict[fordict1, Py_ssize_t] lookupdict1,
dict[Py_ssize_t, fordict1] lookupdict2,
dict[Py_ssize_t, Py_ssize_t] lookupdict3,
Py_ssize_t indexcoun 
):
    cdef:
        Py_ssize_t len_allarra = allarra.shape[0]
        Py_ssize_t hasharray_index
    for hasharray_index in range(len_allarra):
        if allarra[hasharray_index] in lookupdict1:
            lookupdict3[lookupdict1[allarra[hasharray_index]] ]+=1
            continue
        else:
            lookupdict1[allarra[hasharray_index]] = indexcoun
            lookupdict2[indexcoun] = allarra[hasharray_index]
            lookupdict3[indexcoun]=1
            indexcoun += 1
    return indexcoun

cpdef Py_ssize_t create_nr_lookupdict_from_array(
fordict1[:] allarra,
dict[fordict1, Py_ssize_t] lookupdict1,
dict[Py_ssize_t, fordict1] lookupdict2,
Py_ssize_t indexcoun 
):
    cdef:
        Py_ssize_t len_allarra = allarra.shape[0]
        Py_ssize_t hasharray_index
    for hasharray_index in range(len_allarra):
        if allarra[hasharray_index] in lookupdict1:
            continue
        else:
            lookupdict1[allarra[hasharray_index]] = indexcoun
            lookupdict2[indexcoun] = allarra[hasharray_index]
            indexcoun += 1
    return indexcoun
cpdef create_dict_from_np(
    fordict1[::1] a1,
    fordict2[::1] a2,
    ):
        cdef:
            unordered_map[fordict1, fordict2] resultdict
            Py_ssize_t h
            Py_ssize_t width = a1.shape[0]
        with nogil:
            for h in range(width):
                resultdict[a1[h]] = a2[h]
        return resultdict

cpdef void create_normal_checknumpyarray(
    realfull[:,::1] lookupnumpyarray,
    realfull dummyindex,
    cython.char[:,::1] checknumpyarray,
):
    cdef:
        Py_ssize_t lookupnumpyarray_shape_0=lookupnumpyarray.shape[0]
        Py_ssize_t lookupnumpyarray_shape_1=lookupnumpyarray.shape[1]
        Py_ssize_t x,y
    for y in prange(lookupnumpyarray_shape_0,nogil=True):
        for x in range(lookupnumpyarray_shape_1):
            if dummyindex == lookupnumpyarray[y][x]:
                continue
            checknumpyarray[y][lookupnumpyarray[y][x]] = 1

cpdef Py_ssize_t create_numpy_dict_lookup(
realfull[:,::1] lookupnumpyarray,
Py_ssize_t[:,::1] allarra,
int[:] idcounter,
Py_ssize_t[:,::1] lookuparray
):
    cdef:
        unordered_map[Py_ssize_t, Py_ssize_t] lookupdict1
        unordered_map[Py_ssize_t, Py_ssize_t] lookupdict2
        unordered_map[Py_ssize_t, Py_ssize_t] lookupdict3

        unordered_map[Py_ssize_t, Py_ssize_t].iterator it
        Py_ssize_t len_allarra = allarra.shape[0]
        Py_ssize_t w_allarra = allarra.shape[1]
        Py_ssize_t dummyindex = 0
        Py_ssize_t indexcoun = 0
        Py_ssize_t hasharray_index,y,i,j
    for hasharray_index in range(len_allarra):
        for y in range(w_allarra):
            it=lookupdict1.begin()
            while(it != lookupdict1.end()):
                if dereference(it).first == allarra[hasharray_index][y]:
                    break
                postincrement(it)
            else:
                lookupdict1[allarra[hasharray_index][y]] = idcounter[0]
                lookupdict2[idcounter[0]] = hasharray_index
                lookupdict3[idcounter[0]] = y
                if allarra[hasharray_index][y] == -1:
                    dummyindex = idcounter[0]
                idcounter[0] += 1
            lookupnumpyarray[hasharray_index][y] = lookupdict1[allarra[hasharray_index][y]]
    it=lookupdict1.begin()
    while(it != lookupdict1.end()):
        j = dereference(it).second
        lookuparray[indexcoun][0]=lookupdict2[j]
        lookuparray[indexcoun][1]=lookupdict3[j]
        lookuparray[indexcoun][2]=j
        indexcoun+=1
        postincrement(it)
    return dummyindex

cpdef get_all_intersecting(
    cython.char[:,::1] checknumpyarray,
    Py_ssize_t[:,::1] allintersectinglists,
    Py_ssize_t[:] intersectionqty,
    Py_ssize_t[:] newtotalvalues,
    ):
    cdef:
        Py_ssize_t checknumpyarray_shape_0=checknumpyarray.shape[0]
        Py_ssize_t checknumpyarray_shape_1=checknumpyarray.shape[1]
        Py_ssize_t index1,index2,horizontal_index
        openmp.omp_lock_t locker
    openmp.omp_init_lock(&locker)
    for index1 in prange(checknumpyarray_shape_0,nogil=True):
        for index2 in range(checknumpyarray_shape_0):
            if index1 == index2:
                continue
            for horizontal_index in range(checknumpyarray_shape_1):
                if (
                    checknumpyarray[index1][horizontal_index] == 1
                    and checknumpyarray[index2][horizontal_index] == 1
                ):
                    openmp.omp_set_lock(&locker)
                    allintersectinglists[index1][index2] = index2
                    allintersectinglists[index2][index1] = index1
                    intersectionqty[index1] += 1
                    newtotalvalues[index1] += index2
                    openmp.omp_unset_lock(&locker)
    openmp.omp_destroy_lock(&locker)

cpdef loop_until_all_found(
    Py_ssize_t[:,::1] allintersectinglists,
    Py_ssize_t[:] newtotalvalues
):
    cdef:
        Py_ssize_t allintersectinglists_shape_0=allintersectinglists.shape[0]
        Py_ssize_t allintersectinglists_shape_1=allintersectinglists.shape[1]
        Py_ssize_t index1,index2,index3
        openmp.omp_lock_t locker
    openmp.omp_init_lock(&locker)
    for index1 in prange(allintersectinglists_shape_0,nogil=True):
        for index2 in range(allintersectinglists_shape_1):
            if allintersectinglists[index1][index2] == -1:
                continue
            for index3 in range(allintersectinglists_shape_1):
                if allintersectinglists[index2][index3] != -1:
                    openmp.omp_set_lock(&locker)

                    if allintersectinglists[index1][index3] != index3:
                        allintersectinglists[index1][index3] = index3
                        newtotalvalues[index1] += index3

                    if allintersectinglists[index3][index1] != index1:
                        allintersectinglists[index3][index1] = index1
                        newtotalvalues[index3] += index1
                    openmp.omp_unset_lock(&locker)
    openmp.omp_destroy_lock(&locker)

cpdef minus_1_to_0(
    cython.char[:,::1] checknumpyarray,
):
    cdef:
        Py_ssize_t checknumpyarray_shape_0=checknumpyarray.shape[0]
        Py_ssize_t checknumpyarray_shape_1=checknumpyarray.shape[1]
        Py_ssize_t x,y
    for y in prange(checknumpyarray_shape_0,nogil=True):
        for x in range(checknumpyarray_shape_1):
            if checknumpyarray[y][x] == -1:
                checknumpyarray[y][x] = 0

cpdef adjust_dummy(
    realfull[:,::1] lookupnumpyarray,
    realfull dummyindex
):
    cdef:
        Py_ssize_t lookupnumpyarray_shape_0=lookupnumpyarray.shape[0]
        Py_ssize_t lookupnumpyarray_shape_1=lookupnumpyarray.shape[1]
        Py_ssize_t x,y
    for y in prange(lookupnumpyarray_shape_0,nogil=True):
        for x in range(lookupnumpyarray_shape_1):
            if lookupnumpyarray[y][x] == dummyindex:
                lookupnumpyarray[y][x] = -1

                