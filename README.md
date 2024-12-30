Jemma Arona, Luis Guzman

Program 3 - Virtual Memory Simulator (memSim)

Special Instructions:
; Ensure BACKING_STORE.bin is located in the same directory as the memSim.py executable, as the program will reference this file for simulating secondary storage.
; Make the Python script executable by running:
chmod +x memSim.py
;Run the program using the command-line format specified below.

Overview:
;This project simulates a virtual memory system, converting logical addresses into physical addresses by managing page tables, TLBs (Translation Lookaside Buffers), and a backing store. The simulator supports multiple page replacement algorithms, enabling it to manage limited physical memory.

Features:
; Translation Lookaside Buffer (TLB) with FIFO replacement for quick access to frequently used pages.
; Page Table for mapping logical pages to physical frames.
; Page Replacement Algorithms:
-FIFO (default setting)
-LRU (Least Recently Used)
-OPT (Optimal replacement)
; Backing Store Management: Reads data from BACKING_STORE.bin to simulate disk-based secondary storage.

Files:
; memSim.py: Main Python script for the memory simulation.
