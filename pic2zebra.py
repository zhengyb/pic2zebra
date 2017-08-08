#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Translate input picture to zebra print ~DGR cmd

 (C)2017 - zhengyb zhengyb@inhand.com.cn

 contributors:
----------------------------------
* zhengyb

Please let us know if your name is missing!
"""
import os
#pip install Pillow
from PIL import Image
import math


class pic2zebra_cmd(object):

    def __init__(self):
        self.original_path = './original_pic/'
        self.tmp_path = './tmp_pic/'
        self.cmd_path = './zebra_files/'
        self.pic = None
        self.image = None
        if not os.path.exists(self.original_path):
            os.mkdir(self.original_path)
        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)
        if not os.path.exists(self.cmd_path):
            os.mkdir(self.cmd_path)

    def init(self, pic):
        self.pic = pic
        self.image = Image.open(self.original_path + self.pic)

    def _intTo2Str(self, X, K):
        """ intTo2Str( X , K )
            将整数 X 转化为 K位2进制字符串
        """
        try:
            X = long(X)
        except:
            X = 0
        try:
            K = int(K)
        except:
            K = 0
        if K < 1:
            K = 1
        if X < 0:
            FH = 1
            X = -X
        else:
            FH = 0
        A = [0 for J in xrange(0, K)]
        J = K - 1
        while (J >= 0) and (X > 0):
            Y = X % 2
            X = X / 2
            A[J] = Y
            J = J - 1
        if FH == 1:
            # 求反
            for J in xrange(0, K):
                if A[J] == 1:
                    A[J] = 0
                else:
                    A[J] = 1
            # 末位加1
            J = K - 1
            while J >= 0:
                A[J] = A[J] + 1
                if A[J] <= 1:
                    break
                A[J] = 0
                J = J - 1
        return "".join([chr(J + 48) for J in A])

    def _binaryzation(self, image, threshold=127):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        bim = image.point(table, '1')
        return bim

    def _pic_resize_x(self, image, resize_x):
        w0, h0 = image.size
        w_div_h = (w0 * 1.0) / h0
        print("(w0, h0, w/h) = (%d, %d, %f),", w0, h0, w_div_h)
        resize_y = int(math.ceil(resize_x / w_div_h))
        print('resize(w, h) = (%d, %d)', resize_x, resize_y)
        im_resize = image.resize((resize_x, resize_y), Image.ANTIALIAS)
        return (im_resize, resize_x, resize_y)

    def _pic_resize_y(self, image, resize_y):
        w0, h0 = image.size
        w_div_h = (w0 * 1.0) / h0
        print("(w0, h0, w/h) = (%d, %d, %f),", w0, h0, w_div_h)
        resize_x = int(math.ceil(resize_y * w_div_h))
        print('resize(w, h) = (%d, %d)', resize_x, resize_y)
        #im_resize = image.resize((resize_x, resize_y), Image.ANTIALIAS)
        #im_resize = image.resize((resize_x, resize_y), Image.NEAREST)
        im_resize = image.resize((resize_x, resize_y), Image.BILINEAR)
        return (im_resize, resize_x, resize_y)

    def _get_zebra_byte_num(self, x, y):
        row_bytes = int(math.ceil(x / 8.0))
        total_bytes = row_bytes * y
        return (total_bytes, row_bytes)

    def _get_zebra_data(self, image, x, y):
        data = []
        for h in range(0, y):
            #h1 = y-h-1
            h1 = h
            #byte = 0x00
            byte = 0xFF
            for r in range(0, x):
                #print("getpixel(%d, %d)\n", r, h1)
                # if image.getpixel((r, h1)) > 0:
                if image.getpixel((r, h1)) == 0:
                    byte = byte & ~(0x01 << (r % 8))
                if (r % 8 == 7):
                    data.append(byte)
                    #byte = 0x00
                    byte = 0xFF
            if (x % 8) != 0:
                data.append(byte)
        return data

    def _show_zebra_data(self, data, x, y):
        (total, row) = self._get_zebra_byte_num(x, y)
        print("total, row = (%d, %d)\n", total, row)
        ss = ''
        for i in range(len(data)):
            if i % row == 0:
                print("%s" % ss)
                ss = ""
            #ss += "%02X"%(data[i])
            ss += self._intTo2Str(data[i], 8)[::-1]
        print("%s" % ss)

    def tran2zebra(self, cmdfile, xy, resize_x=True, show=1, threshold=127):
        # resize
        if resize_x:
            im_rs, x_rs, y_rs = self._pic_resize_x(self.image, xy)
        else:
            im_rs, x_rs, y_rs = self._pic_resize_y(self.image, xy)
        pic_name = self.pic.rsplit('.', 1)
        resize_file = self.tmp_path + \
            pic_name[0] + "_" + str(x_rs) + "_" + str(y_rs) + '.' + pic_name[1]
        print resize_file
        im_rs.save(resize_file)
        # to binary
        im_lmode = im_rs.convert("L")
        im_lmode.save(
            self.tmp_path + pic_name[0] + "_" + str(x_rs) + "_" + str(y_rs) + '_Lmode.bmp')
        im_bin = self._binaryzation(im_lmode, threshold)
        im_bin.save(
            self.tmp_path + pic_name[0] + "_" + str(x_rs) + "_" + str(y_rs) + "_bin"+str(threshold) + '.bmp')
        # to zebra cmd
        (total_bytes, row_bytes) = self._get_zebra_byte_num(x_rs, y_rs)
        data = self._get_zebra_data(im_bin, x_rs, y_rs)
        if show:
            print("binary picture>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self._show_zebra_data(data, x_rs, y_rs)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        cmd = '~DGR:' + cmdfile + '.GRF,' + \
            str(total_bytes) + ',' + str(row_bytes) + ','
        if show:
            print(cmd)
        row = ''
        for i in range(len(data)):
            if (i > 0) and (i % row_bytes == 0):
                cmd += row
                if show:
                    print row
                row = ''
            row += "%02X" % (data[i])
        cmd += row
        if show:
            print row
        outfile = self.cmd_path + cmdfile + "_" + \
            str(x_rs) + "_" + str(y_rs) + "th" + str(threshold) + ".txt"
        with open(outfile, 'w') as f:
            f.write(cmd)


if __name__ == '__main__':
    tool = pic2zebra_cmd()

    tool.init('callback.bmp')
    #tool.tran2zebra('0001', 100)
    #tool.tran2zebra('0001', 64)
    tool.tran2zebra('0001', 100, False)
    tool.init('rohs.bmp')
    tool.tran2zebra('0002', 100, False)
    tool.init('lajitong.bmp')
    tool.tran2zebra('0003', 100, False)
    tool.init('rohs.jpeg')
    tool.tran2zebra('0004', 100, False, 1, 190)
    tool.init('girl.jpg')
    tool.tran2zebra('0005', 300, False, 1, 127)
