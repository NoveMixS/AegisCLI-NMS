"""
hash module — identify a hash's algorithm, or compute hashes of text.

Usage:
    aegis hash -i <hash>       Identify likely algorithm(s)
    aegis hash -c <text>       Compute MD5/SHA1/SHA256/... of text

Examples:
    aegis hash -i 5f4dcc3b5aa765d61d8327deb882cf99
    aegis hash -c mypassword
"""
import argparse
import hashlib
import re

NAME = "hash"
DESCRIPTION = "Identify hash algorithms or compute hash digests."

HASH_LENGTH_MAP = {
    32: ["MD5", "NTLM", "MD4"],
    40: ["SHA1", "RIPEMD-160"],
    56: ["SHA224", "SHA3-224"],
    64: ["SHA256", "SHA3-256", "BLAKE2s"],
    96: ["SHA384", "SHA3-384"],
    128: ["SHA512", "SHA3-512", "BLAKE2b", "Whirlpool"],
}
HEX_RE = re.compile(r"^[a-fA-F0-9]+$")
BCRYPT_RE = re.compile(r"^\$2[aby]?\$\d{2}\$")
SHA512CRYPT_RE = re.compile(r"^\$6\$")
MD5CRYPT_RE = re.compile(r"^\$1\$")


def identify(value: str) -> list[str]:
    value = value.strip()
    if BCRYPT_RE.match(value):
        return ["bcrypt"]
    if SHA512CRYPT_RE.match(value):
        return ["sha512crypt (Unix)"]
    if MD5CRYPT_RE.match(value):
        return ["md5crypt (Unix)"]
    if HEX_RE.match(value):
        return HASH_LENGTH_MAP.get(len(value), ["Unknown (hex, unrecognized length)"])
    return ["Unknown (non-hex format)"]


def compute(text: str) -> dict[str, str]:
    algos = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    return {a: hashlib.new(a, text.encode()).hexdigest() for a in algos}


def run(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="aegis hash", add_help=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--identify", metavar="HASH", help="Identify a hash's algorithm")
    group.add_argument("-c", "--compute", metavar="TEXT", help="Compute hashes of a string")
    args = parser.parse_args(argv)

    if args.identify:
        candidates = identify(args.identify)
        print(f"[*] Input length: {len(args.identify)} chars")
        print(f"[+] Likely algorithm(s): {', '.join(candidates)}")
    else:
        digests = compute(args.compute)
        print(f"[*] Hashes for: '{args.compute}'\n")
        for algo, digest in digests.items():
            print(f"{algo.upper():<8} {digest}")
