


def main(buffer, reader, receiver):
    sats = []
    
    while True:
        sat = receiver.recv()
        print(f"[ACQUISITION] Sat {sat.prn} found at doppler {sat.doppler} and chip {sat.chip}")