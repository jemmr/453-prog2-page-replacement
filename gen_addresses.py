def gen_addresses(ref_list):
    with open('my-addresses.txt', 'w') as f:
        for i in range(len(ref_list)):
            f.write(f"{ref_list[i] * 256 + i}\n")



if __name__ == '__main__':
    gen_addresses([1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3, 2, 1, 2, 3, 6])
