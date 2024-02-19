from libc.errno cimport EAGAIN
cimport libav as lib

from av.bitstream.filter cimport BitStreamFilter, wrap_filter
from av.error cimport err_check
from av.packet cimport Packet
from av.stream cimport Stream


cdef class BitStreamFilterContext(object):

    def __cinit__(self, filter_):

        cdef int res
        cdef char *filter_str
        cdef lib.AVBitStreamFilter *filter_ptr

        if isinstance(filter_, str):
            filter_str = filter_
            with nogil:
                res = lib.av_bsf_list_parse_str(filter_str, &self.ptr)
            err_check(res)
            self.filter = wrap_filter(self.ptr.filter)

        else:
            self.filter = filter_ if isinstance(filter_, BitStreamFilter) else BitStreamFilter(filter_)
            filter_ptr = self.filter.ptr
            with nogil:
                res = lib.av_bsf_alloc(filter_ptr, &self.ptr)
            err_check(res)

    def __dealloc__(self):
        if self.ptr:
            lib.av_bsf_free(&self.ptr)

    def set_input_stream(self, Stream stream):
        cdef int res
        with nogil:
            self.ptr.time_base_in = stream.ptr.time_base
            res = lib.avcodec_parameters_copy(self.ptr.par_in, stream.ptr.codecpar)
            if res >= 0:
                res = lib.av_bsf_init(self.ptr)
        err_check(res)

    def send(self, Packet packet=None):

        cdef lib.AVPacket *pkt = packet.ptr if packet is not None else NULL

        cdef int res
        with nogil:
                res = lib.av_bsf_send_packet(self.ptr, pkt)
        err_check(res)

    def recv(self):

        cdef Packet packet = Packet()

        cdef int res
        with nogil:
            res = lib.av_bsf_receive_packet(self.ptr, packet.ptr)

        if res == -EAGAIN or res == lib.AVERROR_EOF:
            return
        err_check(res)

        # Since we keep track of the time base in the packet, we need to update it
        packet._time_base = self.ptr.time_base_out

        return packet

    def __call__(self, Packet packet=None):

        self.send(packet)

        output = []
        while True:
            packet = self.recv()
            if packet is None:
                return output
            output.append(packet)
