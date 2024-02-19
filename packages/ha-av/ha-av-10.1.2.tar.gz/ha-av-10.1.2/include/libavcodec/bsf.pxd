
cdef extern from "libavcodec/avcodec.h" nogil:

    # The bitstream filters API was moved to bsf.h in version 58.87.100 of libavcodec (FFmpeg >= 4.3)

    cdef const AVBitStreamFilter* av_bsf_get_by_name(
        const char *name
    )

    cdef const AVBitStreamFilter* av_bsf_iterate(
        void **opaque
    )

cdef extern from "libavcodec/bsf.h" nogil:

    cdef const AVBitStreamFilter* av_bsf_iterate(
        void **opaque
    )

    cdef const AVBitStreamFilter* av_bsf_get_by_name(
        const char *name
    )
