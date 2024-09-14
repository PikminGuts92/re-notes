# templates/forge/rnd_mesh_data.bt
import mrp

def read_string(bf):
    str_length = bf.readint()
    return bf.read(str_length).decode('ascii')

def read_uint64(bf):
    # TODO: Don't assume little endian
    (n1, n2) = bf.read2Int()
    return (n2 << 32) | n1

def find_byte_offsets(bf, bytes):
    offsets = []

    # Get stream length
    bf.seek(0, 2)
    bf_length = bf.tell()
    print(f'Length: {bf_length}')

    # Go to start and begin search
    bf.seek(0)
    while bf.tell() < bf_length:
        start_offset = bf.tell()
        matched = True

        # TODO: Remove after performance fix
        if len(offsets) > 0:
            break

        for b in bytes:
            if bf.tell() >= bf_length:
                break

            if b != bf.readByte():
                matched = False
                break

        if matched:
            offsets.append(start_offset)
        else:
            bf.seek(start_offset + 1)

    print(f'Offset: {bf.tell()}')

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
    mesh.set_vertices(vertices)

    #mrp.print_mesh(name)

# Open file in little endian
bf = mrp.get_bfile(byte_order = '<')

mesh_offsets = find_byte_offsets(bf, b'RndMeshData')
print(mesh_offsets)

for mesh_offset in mesh_offsets:
    # Go to offset and read mesh name
    bf.seek(mesh_offset + len(b'RndMeshData'))
    mesh_name = read_string(bf)
    print(mesh_name)

    mesh_size = read_uint64(bf)
    read_mesh(bf, mesh_name, mesh_size)

mrp.render('All')