import struct
import argparse


def tobmd(s, fmt):
    struct_map = {'f32':'f', 'i32':'i', 'i16':'h', 'i8':'b'}
    result = b''
    if fmt=='str':
        for item in s:
            result += b'\x00'+bytes(item, encoding='utf-8')
        result += b'\x00\x00'
    else:
        result = struct.pack("!"+struct_map[fmt], s)

    return result

class SmdNode(object):
    def __init__(self, ins):
        if type(ins)==list:
            idx, name, parent = ins
            self.idx=int(idx)
            self.name=name
            self.parent=int(parent)
        else:
            1

    def serialize(self):
        return tobmd(self.idx, 'i16')+tobmd(self.parent, 'i16')+tobmd(self.name, 'str')

class SmdFrame(object):
    def __init__(self):
        self.data=[]
    
    def readnode(self, ins):
        boneId = int(ins[0])
        if len(self.data)==0 or boneId>self.data[-1][0]:
            self.data.append([boneId]+[
                float(ins[i]) for i in range(1,7)
            ])
    
    def serialize(self):
        result = tobmd(len(self.data), 'i16') # number of bones
        for fr in self.data:
            result += tobmd(fr[0], 'i16')
            for i in range(1,7):
                result += tobmd(fr[i], 'f32')
        return result

class SmdPoints(object):
    def __init__(self):
        self.data=[]
        self.buffer = []
    
    def readpoint(self, ins):
        links = int(ins[9])
        point_info = [int(ins[0])]+[
            float(ins[i]) for i in range(1,9)
        ]+[links]
        for lk in range(links):
            point_info += [int(ins[10+lk*2]), float(ins[11+lk*2])]
        self.buffer.append(point_info)
        if len(self.buffer)==3:
            self.data.append(self.buffer)
            self.buffer=[]

    def serialize(self):
        result = tobmd(len(self.data), 'i16') # number of trangles, just 1 in this case
        for traingle in self.data:
            result += tobmd(0, 'i8') # material id
            for point_info in traingle:
                result += tobmd(point_info[0], 'i16')
                for i in range(1, 9):
                    result += tobmd(point_info[i], 'f32')
                result += tobmd(point_info[9], 'i8')
                for lk in range(point_info[9]):
                    result += tobmd(point_info[10+lk*2], 'i16')
                    result += tobmd(point_info[11+lk*2], 'f32')
        return result

class Smddata(object):
    def __init__(self, filepath):
        version = 1
        nodes = []
        frames = []
        points = SmdPoints()
        with open(filepath) as fp:
            flags = {'nodes':False, 'skeleton':False, 'triangles':False}
            for line in fp:
                if line.find('version')>=0:
                    version = int(line[:-1].split(' ')[-1])
                elif line[:-1]=="nodes":
                    flags['nodes']=True
                elif line[:-1]=="skeleton":
                    flags['skeleton']=True
                elif line[:-1]=="triangles":
                    flags['triangles']=True
                elif line[:-1]=="end":
                    for flag in flags:
                        flags[flag]=False
                else:
                    splits = line[:-1].split(' ')
                    while '' in splits:
                        splits.remove('')

                    if flags['nodes']:
                        splits[1]=splits[1].replace('"','')
                        nodes.append(SmdNode(splits))
                    elif flags["skeleton"]:
                        if splits[0]=='time':
                            frames.append(SmdFrame())
                        else:
                            frames[-1].readnode(splits)
                    elif flags['triangles']:
                        if splits[0]!='Material':
                            points.readpoint(splits)

        self.version = version
        self.nodes = nodes
        self.frames = frames
        self.points = points
        self.isanim = len(self.points.data)==0
        self.filepath = filepath

    def print(self):
        print('nodes:')
        for node in self.nodes:
            print(vars(node))
        print('\n\nskeleton:')
        for i in [0, -1]:
            print('time', i)
            frame = self.frames[i]
            for fr in frame.data:
                print(fr)
        if not self.isanim:
            print('\ntriangle', self.points.data[-1])

    def serialize(self):
        result = tobmd(self.version, 'i8')
        result += tobmd(len(self.nodes), 'i16')
        for node in self.nodes:
            result += node.serialize()
        result += tobmd(len(self.frames), 'i16') # number of frames
        for frame in self.frames:
            result += frame.serialize()
        if not self.isanim:
            result += tobmd(1, 'i16') # number of materials, just 1 in this case
            result += tobmd('Material', 'str')
            result += self.points.serialize()
        else:
            result += b'\x00'*4
        return result

    def savebmd(self):
        with open(self.filepath[:-3]+'bmd', 'wb') as fp:
            fp.write(self.serialize())

def getargs():
    parser = argparse.ArgumentParser(description='smd2bmd converter')
    parser.add_argument('--file',type=str)

    args = parser.parse_args()
    return args


if __name__=='__main__':
    args = getargs()
    smd = Smddata(args.path)
    smd.savebmd()
