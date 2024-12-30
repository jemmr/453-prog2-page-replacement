#!/usr/bin/env python3
import sys


# Represents the backing store, typically a file simulating secondary storage
class BackingStore:
    # File path for the backing store, where page data is stored
    def __init__(self, file_path):
        self.file_path = file_path

    # Reads a page from the backing store given its page number
    def read_page(self, page_number):
        with open(self.file_path, "rb") as file:
            # Page size in bytes; 256 bytes per page
            # Calculate the offset to start reading from in the file
            page_size = 256
            offset = page_number * page_size
            file.seek(offset)  # Move file pointer to the start of the page
            # Read and return the page data as a bin string
            return file.read(page_size)


# Simulates physical memory with a fixed number of frames, each capable of holding one page
class PhysicalMemory:
    # Initializes physical memory with the specified number of frames
    # Each frame is pre-set to 256 bytes of zero data
    def __init__(self, frame_count):
        self.memory = [b'\x00' * 256] * frame_count  # Initialize empty frames

    def read_byte(self, frame, offset):
        return int.from_bytes(self.memory[frame][offset:offset+1], signed=True)

    # Reads and returns data from the specified frame in physical memory
    def read_frame(self, frame_number):
        return self.memory[frame_number].hex().upper()

    # Writes data to the specified frame in physical memory
    def write_frame(self, frame_number, data):
        self.memory[frame_number] = data


# Represents a page table to map logical pages to physical frames
class PageTable:
    # Initialize an empty dictionary to store page table entries
    # Store the total number of available frames in physical memory
    def __init__(self, page_count):
        self.entries = [[-1, False]] * page_count
        self.page_count = page_count

    # Adds a mapping from a logical page to a physical frame in the page table
    def load_frame(self, physical_frame, logical_page):
        self.entries[logical_page] = [physical_frame, True]

    # Removes a mapping from a logical page to a physical frame in the page table
    # returns frame it was in
    def unload_frame(self, physical_frame):
        for entry in self.entries:
            if entry[0] == physical_frame:
                entry[1] = False
        return

    # Checks if a logical page is currently loaded in the page table
    def is_loaded(self, logical_page):
        return self.entries[logical_page][1]

    # Retrieves the physical frame for a given logical page
    # Returns -1 if the page is not loaded
    def get_frame(self, logical_page):
        page = self.entries[logical_page]
        if page[1]:
            return self.entries[logical_page][0]
        return -1


# Represents the Translation Lookaside Buffer (TLB) for fast page-to-frame lookup
class TLB:
    # Initializes an empty TLB dictionary to store recent page-to-frame mappings
    def __init__(self):
        self.entries = [(-1, -1)] * 16
        self.ptr = 0

    # Retrieves the physical frame for a given logical page if it exists in the TLB
    # Returns -1 if the page is not in the TLB
    def get_frame(self, logical_page):
        for entry in self.entries:
            if entry[0] == logical_page:
                return entry[1]
        return -1

    # Adds or updates an entry in the TLB with a logical-to-physical page mapping
    def add_page(self, logical_page, physical_frame):
        self.entries[self.ptr] = (logical_page, physical_frame)
        self.ptr = (self.ptr+1)%16

    def remove_page(self, logical_page):
        for i in range(16):
            if self.entries[i][0] == logical_page:
                self.entries[i] = (-1, -1)

    def remove_frame(self, physical_frame):
        for i in range(16):
            if self.entries[i][1] == physical_frame:
                self.entries[i] = (-1, -1)

    def __repr__(self):
        return str(self.entries)


# Page Replacement Algorithms. initialize fields needed to choose victim frames.
# all have methods access() and next().
#   access(self, logical_page) notifies pra that logical_page has been accessed.
#       lru adds access to history.
#       opt advances through ref string.
#   next(self) chooses victim page. returns frame number.
#       fifo chooses frames in numerical order.
#       lru, opt check for empty frames. if none, choose last page to show up when:
#           lru: reading backwards through history.
#           opt: reading forwards through ref string.
class FIFO:
    # keeps 'oldest' pointer to oldest page / next to evacuate
    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.oldest = 0

    def access(self, _):
        return

    def next(self):
        f = self.oldest
        self.oldest = (self.oldest + 1) % self.frame_number
        return f


class LRU:
    # keeps 'history' list of page access order
    def __init__(self, page_table, frame_number):
        self.page_table = page_table
        self.frame_number = frame_number
        self.history = []

    def access(self, logical_page):
        self.history.append(logical_page)

    def next(self):
        frames = [-1]*self.frame_number
        to_check = self.frame_number
        for p in range(self.page_table.page_count):
            if self.page_table.entries[p][1]:
                frames[self.page_table.entries[p][0]] = p
        for f in range(self.frame_number):
            if frames[f] == -1:
                return f
        for acc in self.history[-1::-1]:
            if acc not in frames:
                continue
            f = frames.index(acc)
            if frames[f] != -1:
                frames[f] = -1
                to_check -= 1
            if to_check == 0:
                return f
        # for f in range(self.frame_number):
        #     if frames[f] != -1:
        #         return f


class OPT:
    # keeps 'future' ref list and 'current' position in ref list
    def __init__(self, page_table, frame_number, ref_path):
        self.page_table = page_table
        self.frame_number = frame_number
        self.future = []
        self.current = -1;
        with open(ref_path, 'rb') as f:
            for line in f:
                self.future.append(int(line.strip()) >> 8)

    def access(self, _):
        self.current += 1

    def next(self):
        frames = [-1]*self.frame_number
        to_check = self.frame_number
        for p in range(self.page_table.page_count):
            if self.page_table.entries[p][1]:
                frames[self.page_table.entries[p][0]] = p
        for f in range(self.frame_number):
            if frames[f] == -1:
                return f
        for acc in self.future[self.current:]:
            if acc not in frames:
                continue
            f = frames.index(acc)
            if frames[f] != -1:
                frames[f] = -1
                to_check -= 1
            if to_check == 0:
                return f
        for f in range(self.frame_number):
            if frames[f] != -1:
                return f


# Main
def main():
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("usage: memSim <reference-sequence-file.txt> <FRAMES> <PRA>")
        return
    rs_file = sys.argv[1]
    with open(rs_file, 'rb') as ref_seq:
        backing_store = BackingStore("BACKING_STORE.bin")
        frames = 0
        pra = None
        if len(sys.argv) > 2:
            frames = int(sys.argv[2])
        if frames <= 0 or frames > 256:
            frames = 256
        phys_mem = PhysicalMemory(frames)
        page_table = PageTable(256)
        tlb = TLB()
        if len(sys.argv) > 3:
            if sys.argv[3] == "lru":
                pra = LRU(page_table, frames)
            elif sys.argv[3] == "opt":
                pra = OPT(page_table, frames, rs_file)
        if pra is None:
            pra = FIFO(frames)

        addr_count = 0
        tlb_miss = 0
        page_miss = 0
        for addr in ref_seq:
            addr_count += 1
            addr = int(addr.strip())
            p_num = addr >> 8
            p_offset = addr & 0xff
            pra.access(p_num)
            f_num = tlb.get_frame(p_num)
            if f_num == -1:
                tlb_miss += 1
                f_num = page_table.get_frame(p_num)
                if f_num == -1:
                    page_miss += 1
                    f_num = pra.next()
                    tlb.remove_frame(f_num)
                    page_table.unload_frame(f_num)
                    phys_mem.write_frame(f_num, backing_store.read_page(p_num))
                    page_table.load_frame(f_num, p_num)
                tlb.add_page(p_num, f_num)
            print(f"{addr}, {phys_mem.read_byte(f_num, p_offset)}, {f_num}, ", end="")
            print(phys_mem.read_frame(f_num))
        print("Number of Translated Addresses =", addr_count)
        print("Page Faults =", page_miss)
        print("Page Fault Rate =", "{:.3f}".format(page_miss/addr_count))
        print("TLB Hits =", addr_count-tlb_miss)
        print("TLB Misses =", tlb_miss)
        print("TLB Hit Rate =", "{:.3f}".format((addr_count-tlb_miss)/addr_count))


if __name__ == "__main__":
    main()
