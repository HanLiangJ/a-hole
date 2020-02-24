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
      #line = line.replace('\n','').replace('\r','')
      line = " ".join(line.split())
      if len(line) > 0:
        if not '#' in line:
          if not 'vn' in line:
            if line[0] == 'v':
              vertexs.append(extract_v(line))
            elif line[0] == 'f':
              faces.append(extract_f(line))
    return vertexs, faces


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
      vertexs_tmp.append([-v[0], v[1], v[2]])
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
  #data_path = '/home/sunguofei/hd_disk/datas/3D_foot/foot_reduction/test_data/'
  #num = '3000'
  #save_path = data_path+'aligned/'+num
  data_path = '/home/sunguofei/hd_disk/datas/3D_foot/foot_reduction/artShoe_1_database/'
  save_path = '/home/sunguofei/hd_disk/datas/3D_foot/foot_reduction/artShoe_1_database/Foot_left/aligned'
  if not os.path.exists(save_path):
    os.makedirs(save_path)

  #with open(data_path+num+'_info.txt','rb') as f:
  with open(data_path + 'result.csv', 'rb') as f:
    lines = f.readlines()
    for line in lines:
      #line = line.replace('\n','').replace('\r','')
      #data_info = line.split(' ')
      data_info = infor_normalization(line)
      if len(data_info) != 6:
        continue
      data_name = data_path + 'Foot/' + data_info[0] + '.obj'
      save_name = save_path + '/' + data_info[0] + '.obj'

      vertexs, faces = read_obj(data_name)
      vertexs_new, faces_new = align_obj(data_info, vertexs, faces)
      save_obj(save_name, vertexs_new, faces_new)
