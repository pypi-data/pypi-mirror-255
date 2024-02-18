use std::mem;
use windows::core::{decode_utf8_char, utf16_len, wcslen, PCWSTR};

/// Converts a `&str` to a `PCWSTR`.
///
/// # Safety
///
/// The returned `PCWSTR` should be manually freed using `drop_manually_allocated_pcwstr`.
pub unsafe fn new_pcwstr_from_str<S: AsRef<str>>(s: S) -> PCWSTR {
    let input = s.as_ref().as_bytes();
    let output_len = utf16_len(input) + 1;
    let mut buffer = Vec::with_capacity(output_len);

    let mut input_pos = 0;
    while let Some((mut code_point, new_pos)) = decode_utf8_char(input, input_pos) {
        input_pos = new_pos;
        if code_point <= 0xffff {
            buffer.push(code_point as u16);
        } else {
            code_point -= 0x10000;
            buffer.push(0xd800 + (code_point >> 10) as u16);
            buffer.push(0xdc00 + (code_point & 0x3ff) as u16);
        }
    }
    debug_assert!(buffer.len() == output_len - 1);
    buffer.resize(output_len, 0);

    let w = PCWSTR::from_raw(buffer.as_ptr());
    mem::forget(buffer);

    w
}

/// Drops a `PCWSTR` that was manually allocated by `new_pcwstr_from_str`.
///
/// # Safety
///
/// The `PCWSTR` must have been allocated by `new_pcwstr_from_str` and not used after this function is called.
pub unsafe fn drop_manually_allocated_pcwstr(pcwstr: PCWSTR) {
    assert!(!pcwstr.is_null(), "Attempted to drop a null PCWSTR");
    let len = wcslen(pcwstr);
    Vec::from_raw_parts(pcwstr.0 as *mut u16, len, len);
}
