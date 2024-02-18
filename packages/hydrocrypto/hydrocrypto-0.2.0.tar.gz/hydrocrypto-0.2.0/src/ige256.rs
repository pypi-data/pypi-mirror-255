use aes::{cipher::{generic_array::GenericArray, BlockDecrypt, BlockEncrypt, KeyInit}, Aes256};
use crate::aes256::AES_BLOCK_SIZE;

pub fn ige_encrypt(data: &[u8], length: usize, key: &[u8], iv: &[u8]) -> Vec<u8> { 
    let mut out = Vec::with_capacity(length);
    let cipher = Aes256::new(&GenericArray::clone_from_slice(&key));
    let mut iv_1 = iv[..AES_BLOCK_SIZE].to_owned();
    let mut iv_2 = iv[AES_BLOCK_SIZE..].to_owned();
    
    for chunk in data.chunks(AES_BLOCK_SIZE) {
        let mut encrypted = GenericArray::clone_from_slice(&xor(chunk, &iv_1));
        cipher.encrypt_block(&mut encrypted);
        iv_1 = xor(&encrypted, &iv_2);
        iv_2 = chunk.to_owned();
        out.extend_from_slice(&iv_1)
    }
    out
}

pub fn ige_decrypt(data: &[u8], length: usize, key: &[u8], iv: &[u8]) -> Vec<u8> { 
    let mut out = Vec::with_capacity(length);
    let cipher = Aes256::new(&GenericArray::clone_from_slice(&key));
    let mut iv_1 = iv[..AES_BLOCK_SIZE].to_owned();
    let mut iv_2 = iv[AES_BLOCK_SIZE..].to_owned();
    
    for chunk in data.chunks(AES_BLOCK_SIZE) {
        let mut decrypted = GenericArray::clone_from_slice(&xor(chunk, &iv_2));
        cipher.decrypt_block(&mut decrypted);
        iv_2 = xor(&decrypted, &iv_1);
        iv_1 = chunk.to_owned();
        out.extend_from_slice(&iv_2)
    }
    out
}

fn xor(a: &[u8], b: &[u8]) -> Vec<u8> {
    assert_eq!(a.len(), b.len(), "Input slices must have the same length");
    let mut result = vec![0u8; a.len()];
    for i in 0..a.len() {
        result[i] = a[i] ^ b[i];
    }
    result
}