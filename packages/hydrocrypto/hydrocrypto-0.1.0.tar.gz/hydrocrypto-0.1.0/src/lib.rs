use pyo3::{prelude::*, types::PyBytes};
use aes::{cipher::{generic_array::GenericArray, BlockDecrypt, BlockEncrypt, KeyInit}, Aes256};


fn xor(a: &[u8], b: &[u8]) -> Vec<u8> {
    assert_eq!(a.len(), b.len(), "Input slices must have the same length");

    let result: Vec<u8> = a.iter().zip(b.iter()).map(|(&x, &y)| x ^ y).collect();
    result
}

#[pyfunction]
#[pyo3(text_signature = "(data, key, iv, state)")]
fn ctr256<'a>(py: Python<'a>,data: &[u8], key: &[u8], iv: &[u8], state: &[u8]) -> PyResult<&'a PyBytes> {
    let key = GenericArray::from_slice(key);
    let cipher = Aes256::new(key);
    let mut out = Vec::from(data);
    let mut state_array = [0u8; 32];
    state_array.copy_from_slice(state);
    let mut iv_array = [0u8; 32];
    iv_array.copy_from_slice(iv);

    //let iv = iv.as_mut();
    let mut chunk = GenericArray::clone_from_slice(&iv);
    cipher.encrypt_block(&mut chunk);

    for i in (0..data.len()).step_by(16) {
        for j in 0..std::cmp::min(data.len() - i, 16) {
            out[i + j] ^= chunk[state_array[0] as usize];
            state_array[0] += 1;

            if state_array[0] >= 16 {
                state_array[0] = 0;
            }

            if state_array[0] == 0 {
                for k in (0..=15).rev() {
                    match iv_array[k].checked_add(1) {
                        Some(val) => {
                            iv_array[k] = val;
                            break;
                        }
                        None => {
                            iv_array[k] = 0
                        }
                    }
                }

                cipher.encrypt_block(&mut chunk);
            }
        }
    }

    Ok(PyBytes::new(py, &out))

}

#[pyfunction]
#[pyo3(text_signature = "(data, key, iv)")]
fn ige256_encrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> PyResult<&'a PyBytes> {
    let key = GenericArray::from_slice(key);
    let cipher = Aes256::new(key);
    let mut iv_1 = iv[..16].to_owned();
    let mut iv_2 = iv[16..].to_owned();
    let mut result = Vec::new();

    for chunk in data.chunks(16) {
        let e_data = xor(chunk, &iv_1);
        // let e_data_ref = e_data.as_slice();
        let mut encrypt_arr = GenericArray::clone_from_slice(&e_data.as_slice());
        cipher.encrypt_block(&mut encrypt_arr);
        let encrypted_chunk = xor(&encrypt_arr, &iv_2);
        iv_1 = encrypted_chunk.clone();
        iv_2 = chunk.to_owned();
        result.extend_from_slice(&encrypted_chunk)
    }

    Ok(PyBytes::new(py, &result))
}


#[pyfunction]
#[pyo3(text_signature = "(data, key, iv)")]
fn ige256_decrypt<'a>(py: Python<'a>, data: &[u8], key: &[u8], iv: &[u8]) -> PyResult<&'a PyBytes> {
    let key = GenericArray::from_slice(key);
    let cipher = Aes256::new(key);
    let mut iv_1 = iv[..16].to_owned();
    let mut iv_2 = iv[16..].to_owned();
    //let mut data_array: Vec<&[u8]> = Vec::new();
    let mut result = Vec::new();

    for chunk in data.chunks(16) {
        let e_data = xor(chunk, &iv_2);
        //let e_data_ref = e_data.as_slice();
        let mut decrypt_arr = GenericArray::clone_from_slice(&e_data.as_slice());
        cipher.decrypt_block(&mut decrypt_arr);
        let decrypted_chunk = xor(&decrypt_arr, &iv_1);
        iv_2 = decrypted_chunk.clone();
        iv_1 = chunk.to_owned();
        result.extend_from_slice(&decrypted_chunk)
    }

    Ok(PyBytes::new(py, &result))
}

/// A Python module implemented in Rust.
#[pymodule]
fn hydrocrypto(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ctr256, m)?)?;
    m.add_function(wrap_pyfunction!(ige256_encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(ige256_decrypt, m)?)?;
    Ok(())
}
