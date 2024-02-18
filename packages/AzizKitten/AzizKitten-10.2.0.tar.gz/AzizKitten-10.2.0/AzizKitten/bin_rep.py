def bin_rep(n):
    from struct import pack
    binary_representation = pack(">d", n)
    binary_representation = "".join(f"{b:08b}" for b in binary_representation)
    bin_rep.sign = binary_representation[0]
    bin_rep.exponent = binary_representation[1:12]
    bin_rep.mantissa = bin_rep.fraction = binary_representation[12:]
    return bin_rep.sign + " " + bin_rep.exponent + " " + bin_rep.mantissa