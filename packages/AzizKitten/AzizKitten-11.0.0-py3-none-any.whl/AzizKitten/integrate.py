def integrate(integrand, lower_limit, upper_limit):
    segment_width = (upper_limit - lower_limit) / 50000
    result = 0.5 * (integrand(lower_limit) + integrand(upper_limit))
    for i in range(1,50000):
        x_i = lower_limit + i * segment_width
        result += integrand(x_i)
    result *= segment_width
    return result
