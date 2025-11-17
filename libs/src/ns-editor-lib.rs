//use std::cell::OnceCell;
//use std::collections::HashMap;
use std::ffi::CStr; // CString
use std::os::raw::c_char;
use std::sync::LazyLock;

const CRC32_TABLE_SIZE: usize = 0x100;

static CRC32: LazyLock<Crc32> = LazyLock::new(|| Crc32::new());

struct Crc32 {
    initial_n: u32,
    final_n: u32,
    table: [u32; CRC32_TABLE_SIZE]
}

impl Crc32 {
    fn new() -> Self {
        let poly = 0xEDB88320;
        let init = 0xFFFFFFFF;
        let fin = 0x0; //0xFFFFFFFF;

        let table = Self::generate_table(poly);

        Self {
            initial_n: init,
            final_n: fin,
            table
        }
    }

    fn generate_table(poly: u32) -> [u32; CRC32_TABLE_SIZE] {
        let mut table = [0u32; CRC32_TABLE_SIZE];

        for (i, v) in table.iter_mut().enumerate() {
            *v = Self::compute_table_value(i as u32, poly);
        }

        table
    }

    fn compute_table_value(mut v: u32, poly: u32) -> u32 {
        for _ in 0..8 {
            v = if (v & 1) == 1 {
                poly ^ (v >> 1)
            } else {
                v >> 1
            }
        }

        v
    }

    fn compute_hash(&self, value: &str) -> u32 {
        let mut curr = self.initial_n;

        for b in value.as_bytes() {
            curr = self.table_value(*b, curr);
        }

        curr ^ self.final_n
    }

    fn table_value(&self, b: u8, c: u32) -> u32 {
        self.table[((c as u8 ^ b) & 0xFF) as usize] ^ (c >> 8)
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn compute_crc32_hash(string_value: *const c_char) -> u32 {
    let string_value = (unsafe { CStr::from_ptr(string_value) })
        .to_str()
        .unwrap();

    CRC32.compute_hash(string_value)
}