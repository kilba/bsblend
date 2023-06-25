# Assume we are in object mode and have a mesh object

import bpy
import bmesh
from bpy import context

from time import sleep
from enum import IntEnum
import numpy as np
import ctypes
import struct
import mmap

class Types(IntEnum):
    CREATE_OBJECT = 1,
    TRANSFORM_OBJECT = 2,

class VertexData(ctypes.Structure):
    # _pack_ = 4
    _fields_ = [
        # Position
        ('1', ctypes.c_float),
        ('2', ctypes.c_float),
        ('3', ctypes.c_float),
        # Normals
        ('4', ctypes.c_float),
        ('5', ctypes.c_float),
        ('6', ctypes.c_float),
    ]

class Object(ctypes.Structure):
    # _pack_ = 4
    _fields_ = [
        ('Type', ctypes.c_int),
        ('vstream', ctypes.c_int),
        # Position
        ('px', ctypes.c_float),
        ('py', ctypes.c_float),
        ('pz', ctypes.c_float),
        # Rotation
        ('rx', ctypes.c_float),
        ('ry', ctypes.c_float),
        ('rz', ctypes.c_float),
        ('rw', ctypes.c_float),
        # Scale
        ('sx', ctypes.c_float),
        ('sy', ctypes.c_float),
        ('sz', ctypes.c_float),
    ]


def send_data(data):
    shm.write(bytes(data))

def send_mesh_vertices(mesh):
    mesh.calc_normals_split()


    for i, triangle in enumerate(mesh.loop_triangles):
        indices = triangle.vertices
        for l in triangle.loops:
            loop = mesh.loops[l]
            print(l)
            shm.write(struct.pack('%sf' % 3, *mesh.vertices[loop.vertex_index].co))
            shm.write(struct.pack('%sf' % 3, *mesh.loops[l].normal))
            

def send_mesh_indices(mesh):
    for edge in mesh.edges:
        for vert in edge.verts:
            shm.write(struct.pack('i', vert.index))

def send_object(obj):
    bsobj = Object()

    obj.data.calc_loop_triangles()
    num_vertices = 0
    for i, f in enumerate(obj.data.loop_triangles):
        for j, v in enumerate(f.vertices):
            num_vertices += 1

    setattr(bsobj, 'Type', Types.CREATE_OBJECT)
    setattr(bsobj, 'vstream', num_vertices)
    # Position
    setattr(bsobj, 'px', obj.location[0])
    setattr(bsobj, 'py', obj.location[1])
    setattr(bsobj, 'pz', obj.location[2])
    # Rotation
    rot = obj.rotation_euler.to_quaternion()
    setattr(bsobj, 'rx', rot[0])
    setattr(bsobj, 'ry', rot[1])
    setattr(bsobj, 'rz', rot[2])
    setattr(bsobj, 'rw', rot[3])
    # Scale
    setattr(bsobj, 'sx', obj.scale[0])
    setattr(bsobj, 'sy', obj.scale[1])
    setattr(bsobj, 'sz', obj.scale[2])
    
    shm.write(bytes(bsobj))

    send_mesh_vertices(obj.data)

def transform_object(obj):
    shm.seek(0)

def send_initial_data():
    obj = context.active_object
    send_object(obj)

def set_data():
    shm.seek(0)

    send_initial_data()

shm = mmap.mmap(0, 1024*1024*8, "bs_blend")
set_data()
