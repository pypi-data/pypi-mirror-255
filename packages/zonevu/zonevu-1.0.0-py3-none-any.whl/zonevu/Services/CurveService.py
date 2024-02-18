# DEPRECATED.  Use WelllogService for these methods
# class CurveService:
#     client: Client = None
#
#     def __init__(self, c: Client):
#         self.client = c
#
#     def load_curve_samples(self, curve: Curve):
#         url = "welllog/curvedatabytes/%s" % curve.id
#         samples_txt = self.client.get_text(url)
#
#         base64Txt = samples_txt[1:-1]  # Get rid of double quotes from downloaded base64 text
#         curve_float_bytes = base64.b64decode(base64Txt)  # Convert from base64 text to byte array
#         num_bytes = len(curve_float_bytes)
#         num_samples = int(num_bytes / 4)  # Number of samples in well log curve
#         samples = np.zeros(num_samples, dtype='f')  # Allocate and zero out an array of floats of appropriate length
#         for i in range(0, num_samples):  # Loop over samples
#             i1 = 4 * i
#             i2 = 4 * (i + 1)
#             sample_bytes = curve_float_bytes[i1:i2]         # Get 4 byte segment that is next float sample
#             sample = struct.unpack('f', sample_bytes)[0]    # Convert bytes to a float sample
#             samples[i] = sample
#         curve.samples = samples
#
#     def add_curve_samples(self, curve: Curve) -> None:
#         url = "welllog/curvedatabytes/%s" % curve.id
#
#         num_samples = len(curve.samples)
#         curve_float_bytes: bytes = bytearray(4 * num_samples)
#         for i in range(0, num_samples):  # Loop over samples
#             i1 = 4 * i
#             i2 = 4 * (i + 1)
#             sample = curve.samples[i]
#             sample_bytes = struct.pack('f', sample)
#             curve_float_bytes[i1:i2] = sample_bytes
#
#         self.client.post_data(url, curve_float_bytes)
