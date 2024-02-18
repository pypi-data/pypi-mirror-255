# cython: language_level=3

cimport cython

@cython.final
cdef class Tesselator:

    cdef:
        int max_floats

        object __buffer
        float[524288] __array

        int __vertices

        float __u
        float __v
        float __r
        float __g
        float __b

        bint __hasColor
        bint __hasTexture

        int __len
        int __p

        bint __noColor

    cpdef void end(self)
    cdef void __clear(self)
    cpdef void begin(self)
    cpdef inline void colorFloat(self, float r, float g, float b)
    cpdef void vertexUV(self, float x, float y, float z, float u, float v)
    cpdef void vertex(self, float x, float y, float z)
    cpdef inline void color(self, int c)
    cpdef inline void noColor(self)
