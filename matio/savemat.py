import numpy as np

# #TODO:
# 1. Manage object arrays
# 2. Properly manage dependencies
# 3. Add handles
# 4. Add default props


class MatFileWriter:
    def __init__(self):
        self.num_mcos_objects = 0

        self.mcos_object_names = []
        self.region1_class_ids = []
        self.region3_deps = []
        self.region5_handles = []
        self.region2_fields = []
        self.region4_fields = []
        self.field_contents = []

        self.type1_id = 0
        self.type2_id = 0
        self.cell_idx = 0
        self.class_id = 0

    def is_type_1(self, field, class_name):
        if class_name in ["string", "timetable"] and field == "any":
            return True
        return False

    def add_field_name(self, field):
        if field in self.mcos_object_names:
            return self.mcos_object_names.index(field) + 1
        else:
            self.mcos_object_names.append(field)
            return len(self.mcos_object_names)

    def add_class_name(self, class_name):
        class_names = class_name.split(".")
        if len(class_names) == 2:
            handle_name = class_names[0]
            class_name = class_names[1]
        else:
            handle_name = None
            class_name = class_names[0]

        if handle_name is None:
            handle_idx = 0
        else:
            if handle_name in self.mcos_object_names:
                handle_idx = self.mcos_object_names.index(handle_name) + 1
            else:
                self.mcos_object_names.append(handle_name)
                handle_idx = len(self.mcos_object_names)

        if class_name in self.mcos_object_names:
            class_idx = self.region1_class_ids.index(class_name) + 1
        else:
            self.mcos_object_names.append(class_name)
            class_idx = len(self.mcos_object_names)
            self.class_id += 1

        return handle_idx, class_idx

    def get_metadata(self, class_id, num_mcos_objects, dims):
        ndims = len(dims)
        total_objects = np.prod(dims)
        metadata = np.zeros((3 + ndims + total_objects, 1), dtype=np.uint32)
        metadata[0, 0] = 0xDD000000
        metadata[1, 0] = ndims
        metadata[2 : 2 + ndims, 0] = dims
        metadata[2 + ndims : 2 + ndims + total_objects, 0] = np.arange(
            num_mcos_objects - total_objects + 1, num_mcos_objects + 1
        )
        metadata[-1, 0] = class_id
        return metadata

    def np2string(self, arr):
        shape = arr.shape
        header = np.array([1, arr.ndim, *shape], dtype=np.uint64)

        # Flatten array
        flat = arr.ravel()
        n_strings = flat.size

        # Step 1: Get character counts (number of unicode code points)
        char_counts = np.fromiter(
            (len(s) for s in flat), count=n_strings, dtype=np.uint64
        )

        # Step 2: Encode all strings to UTF-16 LE (each character = 2 bytes)
        encoded_bytes = b"".join(s.encode("utf-16-le") for s in flat)
        utf16_all = np.frombuffer(encoded_bytes, dtype=np.uint16)

        # Step 3: Pack UTF-16 uint16s into uint64s (4 uint16s per uint64)
        pad_len = (-utf16_all.size) % 4
        if pad_len:
            utf16_all = np.pad(utf16_all, (0, pad_len), constant_values=0)

        utf16_reshaped = utf16_all.reshape(-1, 4).astype(np.uint64)
        packed_chars = (
            utf16_reshaped[:, 0]
            | (utf16_reshaped[:, 1] << 16)
            | (utf16_reshaped[:, 2] << 32)
            | (utf16_reshaped[:, 3] << 48)
        )

        # Combine all parts
        result = np.concatenate([header, char_counts, packed_chars]).reshape(-1, 1)

        return result

    def convert_from_val(self, val, class_name):
        if class_name == "string":
            return self.np2string(val)

    def write_subsystem(self, props_arr, class_name, is_dep=0):
        dims = props_arr.shape
        self.num_mcos_objects += 1
        dep_id = self.num_mcos_objects

        for idx in np.ndindex(props_arr.shape):
            prop = props_arr[idx]
            for field, val in prop.items():
                field_idx = self.add_field_name(field)
                if self.is_type_1(field, class_name):
                    self.type1_id += 1
                    val_convert = self.convert_from_val(
                        val, class_name
                    )  # For strings mainly
                    self.field_contents.append(val_convert)
                    self.region2_fields.append((field_idx, 1, self.cell_idx))
                    self.cell_idx += 1
                else:
                    self.type2_id += 1

                    if isinstance(val, dict):
                        metadata = self.write_subsystem(val, class_name, is_dep=1)
                        dep_id += 1
                        self.field_contents.append(metadata)
                        self.region4_fields.append((field_idx, dep_id, self.cell_idx))
                    else:
                        if isinstance(val, bool):
                            self.region4_fields.append((field_idx, 2, int(val)))
                        else:
                            self.field_contents.append(val)
                            self.region4_fields.append((field_idx, 1, self.cell_idx))
                            self.cell_idx += 1
                    if is_dep:
                        dep_id -= 1

            self.region1_class_ids.append((handle_idx, class_index, 0, 0))
            self.region3_deps.append(
                (self.class_id, 0, 0, self.type1_id, self.type2_id, dep_id)
            )

        return self.get_metadata(self.class_id, self.num_mcos_objects, dims)


def save_to_mat(file_path, data_dict):
    writer = MatFileWriter()

    for key, value in data_dict.items():
        if isinstance(value, dict):
            class_name = value.get("_Class", None)
            props_arr = value.get("_Props", None)
            metadata = writer.write_subsystem(props_arr, class_name)
        else:
            raise ValueError(f"Unsupported data type for key: {key}")
        pass


if __name__ == "__main__":
    # Example data structure
    data_dict = {
        "a": {
            "_Class": "YesConstructor",
            "_Props": np.tile(
                np.array(
                    {
                        "a": np.array([10]).reshape(1, 1),
                        "b": np.array([20]).reshape(1, 1),
                        "c": np.array([30]).reshape(1, 1),
                    }
                ),
                (2, 3),
            ),
        },
    }

    save_to_mat("test.mat", data_dict)
