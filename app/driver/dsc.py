from .hsio import HsIO


# This driver is failed.

class DSC:
    h_mask = 'DSC FORMAT 1.00'

    @staticmethod
    def encode(data):
        pass

    @staticmethod
    def decode(data):
        c_byte_2 = 0
        dbufc_1 = 0
        cou_c_byte = 0

        io_in = HsIO(data)
        h_mask = io_in.read_string(len(DSC.h_mask) + 1, True)
        if h_mask == DSC.h_mask:
            io_out = HsIO()
            [h_num, d_size, l_pwd] = io_in.read_param('<iii')
            io_in.seek(4, 1)
            in_buf = io_in.read()
            arr_1 = [0 for _ in range(513 * 4)]
            arr_2 = [0 for _ in range(1024 * 4)]
            arr_buf = [0 for _ in range(0xffb)]
            cnt_2 = 0
            for cnt in range(512):
                num = DSC._count_num(h_num)
                w_byte = in_buf[cnt] - (num & 0xff)
                if w_byte != 0:
                    arr_1[cnt_2] = cnt + (w_byte >> 16)
                    cnt_2 += 1
            d_cnt_2 = cnt_2

            if cnt_2 - 1 > 0:
                cnt_a_1 = 0
                cnt_3 = 0

                while cnt_3 < cnt_2:
                    for i in range(cnt_3, cnt_2):
                        w_num = arr_1[cnt_a_1]
                        w_num_2 = arr_1[i]
                        if w_num_2 < w_num:
                            arr_1[cnt_a_1] = w_num_2
                            arr_1[i] = w_num
                    cnt_a_1 += 1
                    cnt_3 += 1
            si_12 = 1
            si_34 = 1
            w_10 = 0
            w_11 = 0
            e_cnt = 0
            condit = 0

            if cnt_2 > 0:
                cnt_a_2 = 0

                while True:
                    w_num = w_10 ^ 0x200
                    sav = w_num
                    w_cnt_1 = w_11
                    w_cnt_2 = w_num
                    w_word = (arr_1[w_cnt_1] >> 16) & 0xffff
                    s_cnt_a_2 = w_cnt_2
                    count_16 = 0
                    while condit == w_word:
                        buf_c = 4 * arr_2[cnt_a_2]
                        wc = arr_1[w_cnt_1] & 0x1ff
                        cnt_a_2 += 1
                        arr_buf[buf_c] = 0
                        arr_buf[buf_c + 1] = wc
                        count_16 += 1
                        w_cnt_1 += 1
                        e_cnt += 1
                        w_word = (arr_1[w_cnt_1] >> 16) & 0xffff
                    w_17 = si_34 - count_16
                    w_18 = 2 * w_17
                    if count_16 < si_34:
                        si_34 = w_17
                        while si_34 != 0:
                            buf_c_2 = 4 * arr_2[cnt_a_2]
                            cnt_a_2 += 1
                            n_2 = 2
                            arr_buf[buf_c_2] = 1
                            buf_c_2 += 2
                            while n_2 > 0:
                                arr_2[w_cnt_2] = si_12
                                arr_buf[buf_c_2] = si_12
                                w_cnt_2 += 1
                                buf_c_2 += 1
                                si_12 += 1
                                n_2 -= 1
                            si_34 -= 1
                    w_11 = e_cnt
                    si_34 = w_18
                    condit += 1
                    if e_cnt >= d_cnt_2:
                        break
                    w_10 = sav
                    cnt_a_2 = s_cnt_a_2

                    in_cnt = 0x200
                    c_byte = 0
                    pass_cnt = 0

                    while pass_cnt < l_pwd:
                        dbufc_1 = 0
                        while True:
                            if c_byte == 0:
                                c_byte = 8
                                c_byte_2 = in_buf[in_cnt]
                                in_cnt += 1
                            c_byte -= 1
                            dbufc_1 = arr_buf[2 + (c_byte_2 >> 7) + dbufc_1 * 4]
                            c_byte_2 *= 2
                            if arr_buf[dbufc_1 * 4] == 0:
                                break

                    word_16 = arr_buf[dbufc_1 * 4 + 1]
                    if word_16 & 0x100 != 0:
                        w_9 = c_byte_2 >> (8 - c_byte)
                        if c_byte < 12:
                            j = ((11 - c_byte) >> 3) + 1
                            cou_c_byte = c_byte + 8 * j
                            while j != 0:
                                w_9 = in_buf[in_cnt] + (w_9 >> 8)
                                in_cnt += 1
                                j -= 1

                        c_byte = cou_c_byte - 12
                        c_byte_2 = w_9 << (8 - c_byte)

                        out_pos = io_out.tell() - 2 - (w_9 >> c_byte)
                        cnt_out = (word_16 & 0xff) + 2

                        while cnt_out > 0:
                            io_out.seek(out_pos)
                            rb = io_out.read(1)
                            io_out.seek(0, 2)
                            io_out.write_param(rb)
                            out_pos += 1
                            cnt_out -= 1

                    else:
                        io_out.write_param('<B', word_16)
                    pass_cnt += 1
                ret = io_out.read_range(0)
                io_in.close()
                io_out.close()
                return ret

    @staticmethod
    def _count_num(st_num):
        work = 20021 * (st_num & 0xffff)
        h_num = (((st_num & 0xffff0000) >> 16) | 0x44530000) * 20021
        work_2 = work * 346 + h_num
        work = work & 0xffff
        work_3 = work_2 & 0xffff
        result = work_2 & 0x7fff
        work_3 = work_3 << 16
        return work + work_3 + 1
