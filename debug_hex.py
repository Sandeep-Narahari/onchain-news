from hexbytes import HexBytes
from web3 import Web3

# Simulate a Transfer input
# Method: a9059cbb
# Address: 0x6baeF23eeb7c09D731095bb5531da50b96b2D9B4
# Start with 0s padding (24 chars = 12 bytes of 0s)
# Amount: 100000 (0.1 USDC) -> 0x186a0 -> padded to 64 chars

method = "a9059cbb"
address = "6baeF23eeb7c09D731095bb5531da50b96b2D9B4"
padding_addr = "0" * 24
param1 = padding_addr + address

amount_hex = hex(100000)[2:] # 186a0
padding_amount = "0" * (64 - len(amount_hex))
param2 = padding_amount + amount_hex

full_hex = "0x" + method + param1 + param2
print(f"Full Hex: {full_hex}")

hb = HexBytes(full_hex)
print(f"HexBytes.hex(): {hb.hex()}")

input_str = hb.hex()

# Check Logic
if not input_str.startswith("0xa9059cbb"):
    print("FAIL: Does not start with method ID")
else:
    print("PASS: Starts with method ID")

# Extract Address
# 0x (2) + method (8) + padding (24) = 34
addr_extracted = "0x" + input_str[34:74]
print(f"Extracted Address: {addr_extracted}")
print(f"Expected Address:  0x{address}")

# Extract Amount
# 34 + 40 = 74
amt_extracted = "0x" + input_str[74:138]
amt_int = int(amt_extracted, 16)
print(f"Extracted Amount: {amt_int}")
