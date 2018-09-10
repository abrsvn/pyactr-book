"""
Declarative memory. Consists of the actual declarative memory, and its associated buffer.
"""

import collections
import math

import numpy as np

import pyactr.chunks as chunks
import pyactr.utilities as utilities
import pyactr.buffers as buffers

class DecMem(collections.MutableMapping):
    """
    Declarative memory module.
    """

    def __init__(self, data=None):
        self._data = {}
        self.restricted_number_chunks = collections.Counter() #counter for pairs of slot - value, used to store strength association
        self.unrestricted_number_chunks = collections.Counter() # counter for chunks, used to store strength association
        self.activations  = {}
        if data is not None:
            try:
                self.update(data)
            except ValueError:
                self.update({x:0 for x in data})

    def __contains__(self, elem):
        if not isinstance(elem, chunks.Chunk):
            return False
        for x in elem:
            temp_chunk = chunks.Chunk(typename=getattr(elem, "typename"), **{x[0]: x[1]})
            #elem is in structued _data
            return temp_chunk in self._data and elem in self._data[temp_chunk]
        #if we got here, it's because loop above did not proceed, so elem has no slot-values; then we check the empty chunk
        return chunks.Chunk(typename=getattr(elem, "typename")) in self._data
    
    def __delitem__(self, key):
        for x in key:
            temp_chunk = chunks.Chunk(typename=getattr(key, "typename"), **{x[0]: x[1]})
            try:
                del self._data[temp_chunk][key]
            except KeyError:
                del self._data[key]
        if len(key) == 0:
            del self._data[chunks.Chunk(typename=getattr(key, "typename"))]

    def __iter__(self):
        temp_data = set()
        for basic_chunk in self._data:
            if len(basic_chunk) == 0:
                yield basic_chunk
                continue
            for elem in self._data[basic_chunk]:
                if elem not in temp_data:
                    temp_data.add(elem)
                    yield elem

    def __getitem__(self, key):
        for x in key.removeunused():
            temp_chunk = chunks.Chunk(typename=getattr(key, "typename"), **{x[0]: x[1]})
            try:
                return self._data[temp_chunk][key]
            except KeyError:
                return self._data[key]
        return self._data[chunks.Chunk(typename=getattr(key, "typename"))]

    def __len__(self):
        length = 0
        for key in self._data:
            length += len(self._data[key])
        return length

    def __repr__(self):
        string = "{"
        for key in self:
            string += " ".join([repr(key), "TIMESTAMPS:", repr(self[key]), " "]) 
        string += "}"
        return string

    def __setitem__(self, key, time):
        if self.unrestricted_number_chunks and key not in self:
            for x in key:
                if utilities.splitting(x[1]).values and utilities.splitting(x[1]).values in self.unrestricted_number_chunks:
                    self.unrestricted_number_chunks.update([utilities.splitting(x[1]).values])
        if self.restricted_number_chunks and key not in self:
            for x in key:
                if utilities.splitting(x[1]).values and (x[0], utilities.splitting(x[1]).values) in self.restricted_number_chunks:
                    self.restricted_number_chunks.update([(x[0], utilities.splitting(x[1]).values)])
        if isinstance(key, chunks.Chunk):
            if len(key) == 0:
                if isinstance(time, np.ndarray):
                    #time is an array
                    self._data.update({key: time})
                else:
                    try:
                        #time is a number
                        self._data.update({key: np.array([round(float(time), 4)])})
                    except TypeError:
                        #time is a sequence
                        self._data.update({key: np.array(time)})
            for x in key.removeunused():
                temp_chunk = chunks.Chunk(typename=getattr(key, "typename"), **{x[0]: x[1]})
                if isinstance(time, np.ndarray):
                    #time is an array
                    self._data.setdefault(temp_chunk, {}).update({key: time})
                else:
                    try:
                        #time is a number
                        self._data.setdefault(temp_chunk, {}).update({key: np.array([round(float(time), 4)])})
                    except TypeError:
                        #time is a sequence
                        self._data.setdefault(temp_chunk, {}).update({key: np.array(time)})
        else:
            raise utilities.ACTRError("Only chunks can be added as attributes to Declarative Memory; '%s' is not a chunk" % key)
    
    def add_activation(self, element, activation):
        """
        Add activation of an element.

        This raises an error if the element is not in the declarative memory
        """
        if element in self:
            self.activations[element] = activation
        else:
            raise AttributeError("The chunk %s is not in the declarative memory." % key)

    def add(self, element, time=0):
        """
        Add an element to decl. mem. Add time to the existing element.

        element can be either one chunk, or an iterable of chunks.
        """
        if isinstance(time, collections.Iterable):
            try:
                new = np.concatenate((self.setdefault(element, np.array([])), np.array(time)))
                self[element] = new
            except (TypeError, AttributeError):
                for x in element:
                    new = np.concatenate((self.setdefault(x, np.array([])), np.array(time)))
                    self[x] = new
        else:
            try:
                new = np.append(self.setdefault(element, np.array([])), round(float(time), 4))
                self[element] = new
            except (TypeError, AttributeError):
                for x in element:
                    new = np.append(self.setdefault(x, np.array([])), round(float(time), 4))
                    self[x] = new

    def copy(self):
        """
        Copy declarative memory.
        """
        dm = DecMem({x: self[x] for x in self})
        dm.activations = self.activations.copy()
        dm.restricted_number_chunks = self.restricted_number_chunks.copy()
        dm.unrestricted_number_chunks = self.unrestricted_number_chunks.copy()
        return dm

class DecMemBuffer(buffers.Buffer):
    """
    Declarative memory buffer.
    """

    def __init__(self, decmem=None, data=None, finst=0):
        buffers.Buffer.__init__(self, decmem, data)
        self.recent = collections.deque()
        self.__finst = finst
        self.activation = None #activation of the last retrieved element
        self.spreading_activation = None #spr activation of the last retrieved element

        #parameters
        self.model_parameters = {}

    @property
    def finst(self):
        """
        Finst - how many chunks are 'remembered' in declarative memory buffer.
        """
        return self.__finst

    @finst.setter
    def finst(self, value):
        if value >= 0:
            self.__finst = value
        else:
            raise ValueError('Finst in the dm buffer must be >= 0')

    @property
    def decmem(self):
        """
        Default harvest of retrieval buffer.
        """
        return self.dm

    @decmem.setter
    def decmem(self, value):
        try:
            self.dm = value
        except ValueError:
            raise ACTRError('The default harvest set in the retrieval buffer is not a possible declarative memory')

    def add(self, elem, time=0):
        """
        Clear current buffer and adds a new chunk.
        """
        self.clear(time)
        super().add(elem)

    def clear(self, time=0):
        """
        Clear buffer, add cleared chunk into memory.
        """
        if self._data:
            self.dm.add(self._data.pop(), time)

    def copy(self, dm=None):
        """
        Copy buffer, along with its declarative memory, unless dm is specified. You need to specify new dm if 2 buffers share the same dm - only one of them should copy dm then.
        """
        if dm == None:
            dm = self.dm 
        copy_buffer = DecMemBuffer(dm, self._data.copy())
        return copy_buffer

    def test(self, state, inquiry):
        """
        Is current state busy/free/error?
        """
        return getattr(self, state) == inquiry

    def retrieve(self, time, otherchunk, actrvariables, buffers, extra_tests, model_parameters):
        """
        Retrieve a chunk from declarative memory that matches otherchunk.
        """
        model_parameters = model_parameters.copy()
        model_parameters.update(self.model_parameters)

        if actrvariables == None:
            actrvariables = {}
        try:
            mod_attr_val = {x[0]: utilities.check_bound_vars(actrvariables, x[1], negative_impossible=False) for x in otherchunk.removeunused()}
        except utilities.ACTRError as arg:
            raise utilities.ACTRError("Retrieving the chunk '%s' is impossible; %s" % (otherchunk, arg))
        chunk_tobe_matched = chunks.Chunk(otherchunk.typename, **mod_attr_val)

        max_A = float("-inf")

        #collect the subset of dm that is useful (only chunks that match the searched chunk will be used
        if len(chunk_tobe_matched.removeunused()) == 0 or ( model_parameters["subsymbolic"] and model_parameters["partial_matching"]):
            used_dm = self.dm
        else:
            used_dm = {}
            for x in chunk_tobe_matched.removeunused():
                temp_chunk = chunks.Chunk(typename=getattr(chunk_tobe_matched, "typename"), **{x[0]: x[1]})
                temp_data = {}
                for x in self.dm._data:
                    if temp_chunk <= x:
                        temp_data.update(self.dm._data[x])
                #update used_dm with found chunks (either by creating it, if it is empty, or by intersecting with already present chunks)
                if not used_dm:
                    used_dm = temp_data
                elif len(used_dm) <= len(temp_data):
                    temp_data2 = {}
                    for i in used_dm:
                        if i in temp_data:
                            temp_data2[i] = temp_data[i]
                    used_dm = temp_data2
                elif len(temp_data) < len(used_dm):
                    temp_data2 = {}
                    for i in temp_data:
                        if i in used_dm:
                            temp_data2[i] = used_dm[i]
                    used_dm = temp_data2

        retrieved = None

        #loop through this subset and check activation

        for chunk in used_dm:

            try:
                if extra_tests["recently_retrieved"] == False or extra_tests["recently_retrieved"] == 'False':
                    if self.__finst and chunk in self.recent:
                        continue

                else:
                    if self.__finst and chunk not in self.recent:
                        continue
            except KeyError:
                pass
            if model_parameters["subsymbolic"]: #if subsymbolic, check activation
                A_pm = 0
                if model_parameters["partial_matching"]:

                    A_pm = chunk_tobe_matched.match(chunk, partialmatching=True, mismatch_penalty=model_parameters["mismatch_penalty"])
                else:
                    if not chunk_tobe_matched <= chunk:
                        continue

                try:
                    A_bll = utilities.baselevel_learning(time, self.dm[chunk], model_parameters["baselevel_learning"], model_parameters["decay"], self.dm.activations.get(chunk), optimized_learning=model_parameters["optimized_learning"]) #bll
                except UnboundLocalError:
                    continue
                if math.isnan(A_bll):
                    raise utilities.ACTRError("The following chunk cannot receive base activation: %s. The reason is that one of its traces did not appear in a past moment." % chunk)
                try:
                    A_sa = utilities.spreading_activation(chunk, buffers, self.dm, model_parameters["buffer_spreading_activation"], model_parameters["strength_of_association"], model_parameters["spreading_activation_restricted"], model_parameters["association_only_from_chunks"])
                except IndexError:
                    A_sa = float(0)
                inst_noise = utilities.calculate_instantanoues_noise(model_parameters["instantaneous_noise"])
                A = A_bll + A_sa + A_pm + inst_noise #chunk.activation is the manually specified activation, potentially used by the modeller

                if utilities.retrieval_success(A, model_parameters["retrieval_threshold"]) and max_A < A:
                    self.spreading_activation = A_sa
                    max_A = A
                    self.activation = max_A
                    retrieved = chunk
                    extra_time = utilities.retrieval_latency(A, model_parameters["latency_factor"],  model_parameters["latency_exponent"])

                    if model_parameters["activation_trace"]:
                        print("(Partially) matching chunk:", chunk)
                        print("Base level learning:", A_bll)
                        print("Spreading activation", A_sa)
                        print("Partial matching", A_pm)
                        print("Noise:", inst_noise)
                        print("Total activation", A)
                        print("Time to retrieve", extra_time)
            else: #otherwise, just standard time for rule firing, so no extra calculation needed
                if chunk_tobe_matched <= chunk and self.dm[chunk][0] != time: #the second condition ensures that the chunk that was created are not retrieved at the same time
                    retrieved = chunk
                    extra_time = model_parameters["rule_firing"]

        if not retrieved:
            self.activation, self.spreading_activation = None, None
            if model_parameters["subsymbolic"]:
                extra_time = utilities.retrieval_latency(model_parameters["retrieval_threshold"], model_parameters["latency_factor"],  model_parameters["latency_exponent"])
            else:
                extra_time = model_parameters["rule_firing"]
        if self.__finst:
            self.recent.append(retrieved)
            if self.__finst < len(self.recent):
                self.recent.popleft()

        return retrieved, extra_time
        
