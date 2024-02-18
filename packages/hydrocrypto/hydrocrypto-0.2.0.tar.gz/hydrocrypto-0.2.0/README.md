## HydroCrypto

> Cryptography Extension for Hydrogram

**HydroCrypto** is a Cryptography Library written in __Rust__ as a Python extension using pyo3.<br/><br/>
It is designed to be portable, fast, easy to install and use. 
**HydroCrypto** is intended for **[Hydrogram](https://github.com/hydrogram/hydrogram)**.

**HydroCrypto** uses the `AES-IGE` and `AES-CTR` for the **Telegram MTProto and CDN**

## Requirements

- `Python 3.8 or higher`

## Installation

```
$ pip install hydrocrypto
```

## Usage

**HydroCrypto** consists of functions like

```python
ige256_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
ige256_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
ctr256_encrypt(data: bytes, key: bytes, iv: bytes, state: bytes) -> bytes:
ctr256_decrypt(data: bytes, key: bytes, iv: bytes, state: bytes) -> bytes:
```

## License 

`LGPLV3+` _© 2024 _    **_Anand_**