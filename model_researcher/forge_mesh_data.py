# templates/forge/rnd_mesh_data.bt
import mrp

class ForgeMeshData:
    def __init__(self, name, faces, vertices):
        self.name = name
        self.faces = faces
        self.vertices = vertices

class ForgeMesh:
    def __init__(self, name, data_name, data=None):
        self.name = name
        self.data_name = data_name
        self.data = data

def read_string(bf):
    str_length = bf.readint()
    if str_length <= 0:
        return b''

    return bf.read(str_length).decode('ascii')

def read_uint64(bf):
    # TODO: Don't assume little endian
    (n1, n2) = bf.read2Int()
    return (n2 << 32) | n1

def find_offsets_in_buffer(buffer, bytes):
    offsets = []
    buff_length = len(buffer)

    # Go to start and begin search
    i = 0
    while i < buff_length:
        bytes_idx = buffer[i:].find(bytes)
        if bytes_idx == -1:
            break

        offsets.append(i + bytes_idx)
        i += bytes_idx + len(bytes)

    return offsets

def find_offsets(bf, bytes, max_buffer_size):
    offsets = []

    # Get stream length
    bf.seek(0, 2)
    bf_length = bf.tell()

    bf.seek(0)
    while bf.tell() < bf_length:
        # Overlap buffer with size of searched bytes
        buffer_start = max(0, bf.tell() - len(bytes))
        bf.seek(buffer_start)

        rem_length = bf_length - buffer_start
        buffer_size = min(rem_length, max_buffer_size)
        buffer = bf.read(buffer_size)

        buffer_offsets = find_offsets_in_buffer(buffer, bytes)
        for bo in buffer_offsets:
            offsets.append(buffer_start + bo)

    # Remove potential duplicates and sort
    offsets = list(set(offsets))
    offsets.sort()

    return offsets

def read_mesh(bf, name):
    bf.seek(4, 1) # Magic

    # Object
    bf.seek(4, 1) # Magic
    bf.seek(4, 1) # 8 constant
    file_count = bf.readint() # Embedded files
    for _ in range(0, file_count):
        read_string(bf)
        file_size = read_uint64(bf)
        bf.seek(file_size, 1)

    # Trans
    bf.seek(4, 1) # Magic
    bf.seek(2 * 48, 1) # 2x matrix data
    bf.seek(4, 1) # Some enum
    read_string(bf) # Bone name
    bf.readByte() # Some bool
    read_string(bf) # Parent name

    # Draw
    bf.seek(4, 1) # Magic
    bf.readByte() # Showing
    bf.seek(4, 1) # Some enum
    read_string(bf) # Property 1
    read_string(bf) # Property 2
    bf.seek(16, 1) # Bounding sphere
    bf.seek(4, 1) # Some float

    bf.seek(4, 1) # Always 0
    mat_name = read_string(bf)

    bone_count = bf.readint()
    for _ in range(0, bone_count):
        read_string(bf) # Name
        bf.seek(48, 1) # Matrix

    mesh_name = read_string(bf)
    bf.seek(4, 1) # Some enum

    if bf.readByte():
        # Rnd mesh data embedded directly
        mesh_data = read_mesh_data(bf, mesh_name)
        return ForgeMesh(name, mesh_name, mesh_data)
    else:
        rnd_mesh_data_name = read_string(bf)
        return ForgeMesh(name, rnd_mesh_data_name)

def read_mesh_data(bf, name):
    faces = []
    vertices = []

    # Read faces
    bf.seek(46, 1) # Skip to face count
    face_count = bf.readint()
    bf.seek(4, 1) # Skip 21845 constant

    for _ in range(0, face_count):
        face = bf.read3Int()
        faces.append(face)

    # Read vertices
    vert_size = 114 # Default size if not specified
    vertex_count = bf.readint()
    bf.seek(4, 1) # Skip 2114 constant

    if bf.readByte():
        # Use defined vert size
        vert_size = bf.readint()
        bf.seek(4, 1) # Skip 2 or 4 constant

    extra_vert_data_size = vert_size - 12
    for _ in range(0, vertex_count):
        vert_xyz = bf.read3Float()
        vertices.append(vert_xyz)
        bf.seek(extra_vert_data_size, 1)

    return ForgeMeshData(name, faces, vertices)

# Open file in little endian
bf = mrp.get_bfile(byte_order = '<')

# Read mesh data
mesh_data_offsets = find_offsets(bf, b'RndMeshData', 0x2000000) # Buffer size of ~32Mb
print(f'Mesh data offsets: {mesh_data_offsets}')

mesh_datas = {}

for mesh_data_offset in mesh_data_offsets:
    # Go to offset and read mesh name
    bf.seek(mesh_data_offset + len(b'RndMeshData'))
    mesh_data_name = read_string(bf)

    if len(mesh_data_name) == 0:
        # Skip unnamed meshes (doesn't seem to have geometry data anyway)
        continue

    mesh_size = read_uint64(bf)
    mesh_data = read_mesh_data(bf, mesh_data_name)

    mesh_datas[mesh_data_name] = mesh_data

# Read mesh names
mesh_name_offsets = find_offsets(bf, b'\x04\x00\x00\x00\x4D\x65\x73\x68', 0x2000000) # Buffer size of ~32Mb
mesh_names = []
for mesh_name_offset in mesh_name_offsets:
    bf.seek(mesh_name_offset + 8)
    mesh_name = read_string(bf)
    mesh_names.append(mesh_name)

# Read meshes
mesh_offsets = find_offsets(bf, b'\x2B\x00\x00\x00\x06\x00\x00\x00\x08\x00\x00\x00', 0x2000000) # Buffer size of ~32Mb
print(f'Mesh offsets: {mesh_offsets}')

meshes = []

for i, mesh_offset in enumerate(mesh_offsets):
    bf.seek(mesh_offset)
    mesh_name = mesh_names[i]
    mesh = read_mesh(bf, mesh_name)

    if not mesh.data_name:
        # Ignore meshes without mesh data
        continue

    if mesh.data is None:
        mesh.data = mesh_datas[mesh.data_name]

    meshes.append(mesh)

for mesh in meshes:
    #print(f'{mesh.name}/{mesh.data.name} ({len(mesh.data.vertices)} verts, {len(mesh.data.faces)} faces)')

    # Create mesh
    mr_mesh = mrp.create_mesh(mesh.name)
    mr_mesh.set_faces(mesh.data.faces)
    mr_mesh.set_vertices(mesh.data.vertices, 'YZX', 'x')

mrp.render('All')
print(f'Found {len(meshes)} meshes!')