import os
from random import randint
from operations import *

def init_sequence(size):
    bit_sequence = [randint(0, 1) for i in range(size)]
    return bit_sequence


def calc_bit(first_bit_sequence, second_bit_sequence):
    bit1 = first_bit_sequence[13] ^ first_bit_sequence[16]
    bit2 = second_bit_sequence[100] ^ second_bit_sequence[110]
    bit = bit1 ^ bit2
    first_bit_sequence.pop()
    second_bit_sequence.pop()
    first_bit_sequence.insert(0, bit1)
    second_bit_sequence.insert(0, bit2)

    return bit

def gen_key(key_size):
    first_size, second_size = 17, 111
    first_bit_sequence = init_sequence(first_size)
    second_bit_sequence = init_sequence(second_size)
    key = ''

    for i in range(key_size):
        bit = calc_bit(first_bit_sequence, second_bit_sequence)
        key += str(bit)

    with open('key.key', 'wb') as f:
        for i in range(0, len(key), 8):
            sub_block_key = key[i: i+8]
            f.write(int(sub_block_key, 2).to_bytes(1, 'big'))

def key_deploy():
    K = ''

    with open('key.key', 'rb') as f:
        byte = f.read(1)
        while byte:
            K += hex(byte[0])[2:].zfill(2)
            byte = f.read(1)

    k1, k2 = K[:32], K[32:]
    keys = []
    keys.append(k1)
    keys.append(k2)
    C_constants = []

    for i in range(1, 33):
        vector = hex(i)[2:].zfill(32)
        C = L_conversion(vector)
        C_constants.append(C)

    for i in range(len(C_constants)):

        F_result = L_conversion(S_conversion(X_conversion(C_constants[i], k1)))

        k1, k2 = X_conversion(F_result, k2), k1

        if (i + 1) % 8 == 0:
            keys.append(k1)
            keys.append(k2)

    return keys


def encrypt(file_path):
    keys = key_deploy()

    file_size = os.path.getsize(file_path)
    f = open('encrypted.enc', 'wb')
    f.close()
    count_read_blocks = 0
    with open(file_path, 'rb') as f:
        while True:
            count_read_blocks += 1
            if count_read_blocks != file_size // 16 + 1 or file_size % 16 == 0:
                block_data = f.read(16)

                block_data = int.from_bytes(block_data, 'big')


            else:

                block_data = f.read(file_size % 16)

                block_data = bin(int.from_bytes(block_data, 'big'))[2:].zfill((file_size % 16) * 8)
                
                block_data += '1' + '0' * (127 - len(block_data))

                block_data = int(block_data, 2)

            if not block_data:
                break

            block_data = hex(block_data)[2:].zfill(32)


            for i in range(len(keys)):

                if i != 9:
                    block_data = L_conversion(S_conversion(X_conversion(keys[i], block_data)))

                else:
                    block_data = int(X_conversion(keys[i], block_data), 16)


                    with open('encrypted.enc', 'ab') as out:
                        out.write(block_data.to_bytes(16, 'big'))



def decrypt(file_path):
    keys = key_deploy()
    f = open('decrypted.txt', 'wb')
    f.close()
    count_read_blocks = 0
    with open(file_path, 'rb') as f:
        while True:
            count_read_blocks += 1
            block_data = f.read(16)

            block_data = int.from_bytes(block_data, 'big')

            if not block_data:
                break

            block_data = hex(block_data)[2:].zfill(32)

            for i in range(len(keys) - 1, -1, -1):

                if i != 0:
                    block_data = S_reverse_conversion(L_reverse_conversion(X_conversion(keys[i], block_data)))


                else:
                    block_data = int(X_conversion(keys[i], block_data), 16)

                    if os.path.getsize(file_path) // 16 == count_read_blocks:
                        block_data = bin(block_data)[2:].zfill(128)
                        last_unit = block_data.rfind('1')
                        block_data = block_data[:last_unit]


                        with open('decrypted.txt', 'ab') as out:

                            out.write(int(block_data, 2).to_bytes(len(block_data) // 8, 'big'))

                        

                    else:
                        with open('decrypted.txt', 'ab') as out:
                            out.write(block_data.to_bytes(16, 'big'))

gen_key(256)

while True:
    mode = input('Введите режим работы "enc" или "dec": ')

    if mode == 'enc':
        file_path = input('Путь к файлу: ')
        encrypt(file_path)


    elif mode == 'dec':
        file_path = input('Путь к файлу: ')
        decrypt(file_path)
