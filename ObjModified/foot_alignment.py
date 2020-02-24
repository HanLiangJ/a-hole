import os


# import numpy as np


def extract_v(s):
    v = []
    v_s = s.split(' ')
    for _, num in enumerate(v_s[1:]):
        v.append(float(num))

    return v


def extract_f(s):
    f = []
    f_s = s.split(' ')
    for _, num in enumerate(f_s[1:]):
        if '//' in s:
            idx = num.find('/')
            f.append(int(num[:idx]))
        else:
            f.append(int(num))

    return f


def read_obj(filename):
    with open(filename) as f:
        vertexs = []
        faces = []
        for line in f.readlines():
            # line = line.replace('\n','').replace('\r','')
            line = " ".join(line.split())
            if len(line) > 0:
                if not '#' in line:
                    if not 'vn' in line:
                        if not 'vt' in line:
                            if line[0] == 'v':
                                vertexs.append(extract_v(line))
                            elif line[0] == 'f':
                                faces.append(extract_f(line))
        return vertexs, faces



def change_obj(vertexs,faces):
    vertexs_new=[]
    vertexs_center=[]
    faces_new=[]

    sum_x=0
    sum_y=0
    cnt=0
    max_y=0
    max_x=0
    min_z=9999
    isright=False

    #计算与坐标轴标准中心的偏差
    for v in vertexs:
        sum_x+=v[0]
        sum_y+=v[1]
        cnt+=1
        if min_z>v[2]:
            min_z=v[2]
    sum_x/=cnt
    sum_y/=cnt

    # 移动到坐标轴中心和xoy平面以上
    for v in vertexs:
        vertexs_center.append([(v[0]-sum_x),(v[1]-sum_y),v[2]-min_z])

    # 判断是否是左右脚
    for v in vertexs_center:
        if max_y<v[1]:
            max_y=v[1]
            max_x=v[0]
    if max_x <0:
        isright=True #是右脚

    if isright:
        for v in vertexs_center:
            vertexs_new.append([v[0],-v[1],v[2]])
        for f in faces:
            faces_new.append([f[0],f[2],f[1]])
    else:
        for v in vertexs_center:
            vertexs_new.append([-v[0],-v[1],v[2]])
        faces_new=faces
    return vertexs_new,faces_new


def rm_wrist(vertexs, thresh=100, return_idx=False):
    z_min = 10000.0
    res = []
    idx = []
    for v in vertexs:
        if v[2] < z_min:
            z_min = v[2]
    for v in vertexs:
        if v[2] <= z_min + thresh:
            res.append(v)
            idx.append(True)
        else:
            idx.append(False)
    if return_idx:
        return idx
    else:
        return res


def save_obj(filename, vertexs, faces):
    with open(filename, 'w') as f:
        for i in range(len(vertexs)):
            f.write('v {:f} {:f} {:f}\n'.format(vertexs[i][0], vertexs[i][1],
                                                vertexs[i][2]))
        for i in range(len(faces)):
            f.write('f {:d} {:d} {:d}\n'.format(
                int(faces[i][0]), int(faces[i][1]), int(faces[i][2])))


def align_obj(data_info, vertexs, faces):
    vertexs_new = []
    for v in vertexs:
        # rotate along axis z
        if data_info[2] == 'up':
            # rotate clock-wise 180 degrees
            vertexs_new.append([-v[0], -v[1], v[2]])
        elif data_info[2] == 'left':
            # rotate clock-wise 270 degrees
            vertexs_new.append([-v[1], v[0], v[2]])
        elif data_info[2] == 'right':
            # rotate clock-wise 90 degrees
            vertexs_new.append([v[1], -v[0], v[2]])
        else:
            vertexs_new.append([v[0], v[1], v[2]])

    if data_info[3] == 'outer':
        # rotate along axis x
        vertexs_tmp = []
        for v in vertexs_new:
            # rotate clock-wise 180 degrees
            vertexs_tmp.append([v[0], -v[1], -v[2]])
        vertexs_new = vertexs_tmp

    if data_info[5] == 'N':
        # mirror face index
        faces_new = []
        for f in faces:
            faces_new.append([f[0], f[2], f[1]])
    else:
        faces_new = faces

    if data_info[4] == 'right':
        # mirror over y-z plane
        vertexs_tmp = []
        faces_tmp = []
        for v in vertexs_new:
            vertexs_tmp.append([-v[0], -v[1], v[2]])
        for f in faces_new:
            faces_tmp.append([f[0], f[2], f[1]])
        vertexs_new = vertexs_tmp
        faces_new = faces_tmp

    return vertexs_new, faces_new


def infor_normalization(data_info):
    data_info = data_info.replace('\n', '').replace('\r', '')
    data_info = data_info.split(',')
    res = []
    if not data_info[0].endswith('.obj'):
        return res
    if len(data_info) != 5:
        return res
    if data_info[1] == '0':
        return res
    res.append(data_info[0][:-4])
    res.append('400')
    if data_info[3] == 'r':
        res.append('right')
    elif data_info[3] == 'u':
        res.append('up')
    elif data_info[3] == 'l':
        res.append('left')
    else:
        res.append('down')
    res.append('inner')
    if data_info[2] == '1':
        res.append('left')
    else:
        res.append('right')
    if data_info[4] == '1':
        res.append('Y')
    else:
        res.append('N')
    return res


if __name__ == '__main__':
    root_path = './teacher_mask'

    dir_names=os.listdir(root_path)
    for file in dir_names:
        print(file[0])
        print(ord(file[0])-ord('a'))
        if ((ord(file[0])-ord('a')<=26) and (ord(file[0])-ord('a')>=0) or(ord(file[0])-ord('0')<=9) and (ord(file[0])-ord('0')>=0)) :
            data_path=root_path+'/'+file
            save_path = root_path + '_new_new/'

            if not os.path.exists(save_path):
              os.makedirs(save_path)

            data_name = data_path+'/'+'model.obj'
            save_name = save_path+file+'.obj'
            print(file)
            vertexs,faces=read_obj(data_name)
            vertexs_new,faces_new=change_obj(vertexs,faces)
            save_obj(save_name,vertexs_new,faces_new)

