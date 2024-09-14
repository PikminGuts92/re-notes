# templates/forge/rnd_mesh_data.bt
import mrp

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
        start_offset = i
        matched = True

        for b in bytes:
            if i >= buff_length or b != buffer[i]:
                matched = False
                i += 1
                break

            i += 1

        if matched:
            offsets.append(start_offset)
        else:
            i = start_offset + 1

    return offsets

def find_offsets(bf, bytes, max_buffer_size):
    offsets = []

    # Get stream length
    bf.seek(0, 2)
    bf_length = bf.tell()
    print(f'Length: {bf_length}')

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

def read_mesh(bf, name, size):
    faces = []
    vertices = []

    # Read faces
    bf.seek(46, 1) # Skip to face count
    face_count = bf.readint()
    bf.seek(4, 1) # Skip 21845 constant
    print(f'Face count: {face_count}')

    for _ in range(0, face_count):
        face = bf.read3Int()
        faces.append(face)

    # Read vertices
    vert_size = 114 # Default size if not specified
    vertex_count = bf.readint()
    bf.seek(4, 1) # Skip 2114 constant
    print(f'Vert count: {vertex_count}')

    if bf.readByte():
        # Use defined vert size
        vert_size = bf.readint()
        bf.seek(4, 1) # Skip 2 or 4 constant

    extra_vert_data_size = vert_size - 12
    for _ in range(0, vertex_count):
        vert_xyz = bf.read3Float()
        vertices.append(vert_xyz)
        bf.seek(extra_vert_data_size, 1)

    # Create mesh
    mesh = mrp.create_mesh(name)
    mesh.set_faces(faces)
    mesh.set_vertices(vertices, 'YZX', 'x')

    #mrp.print_mesh(name)

# Open file in little endian
bf = mrp.get_bfile(byte_order = '<')

mesh_offsets = find_offsets(bf, b'RndMeshData', 0x2000000) # Buffer size of ~32Mb
print(mesh_offsets)

for mesh_offset in mesh_offsets:
    # Go to offset and read mesh name
    bf.seek(mesh_offset + len(b'RndMeshData'))
    mesh_name = read_string(bf)

    if len(mesh_name) == 0:
        # Skip unnamed meshes (don't seems to have geometry data anyway)
        continue

    print(mesh_name)

    mesh_size = read_uint64(bf)
    read_mesh(bf, mesh_name, mesh_size)

mrp.render('All')